"""
AAP (Agent Address Protocol) Python SDK
https://github.com/thomaszta/aap-protocol

Usage:
    pip install aap-sdk
"""

import re
import secrets
import urllib.parse
import json
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from time import sleep

import requests

__version__ = "0.1.1"

# 重试配置
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # 秒

AAP_PATTERN = re.compile(
    r"^ai:([^~#]+)~([^#]+)#(.+)$",
    re.IGNORECASE
)

# 输入验证常量
MAX_OWNER_LENGTH = 64
MAX_ROLE_LENGTH = 64
MAX_PROVIDER_LENGTH = 253  # DNS 域名最大长度
VALID_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_."
)
# Provider 可以包含端口号 (localhost:5000, 192.168.1.1:8080)
VALID_CHARS_PROVIDER = VALID_CHARS | frozenset(":")


def _validate_address_component(value: str, name: str, max_len: int, valid_chars=None) -> None:
    """Validate a single address component."""
    if not value:
        raise InvalidAddressError(f"{name} cannot be empty")
    
    if len(value) > max_len:
        raise InvalidAddressError(
            f"{name} too long (max {max_len} characters): {len(value)}"
        )
    
    # 检查有效字符
    chars = valid_chars or VALID_CHARS
    invalid_chars = set(value) - chars
    if invalid_chars:
        raise InvalidAddressError(
            f"Invalid characters in {name}: {invalid_chars}"
        )


class AAPError(Exception):
    """Base exception for AAP SDK."""
    pass


class InvalidAddressError(AAPError):
    """Invalid AAP address format."""
    pass


class ResolveError(AAPError):
    """Failed to resolve address."""
    pass


class MessageError(AAPError):
    """Failed to send/receive message."""
    pass


class ProviderError(AAPError):
    """Provider is unreachable or returned an error."""
    pass


@dataclass
class AAPAddress:
    """Parsed AAP address: ai:owner~role#provider."""
    owner: str
    role: str
    provider: str

    def __str__(self) -> str:
        return f"ai:{self.owner}~{self.role}#{self.provider}"

    @property
    def uri(self) -> str:
        return urllib.parse.quote(str(self), safe="")


def parse_address(address: str) -> AAPAddress:
    """
    Parse an AAP address string into components.
    
    Args:
        address: AAP address string like "ai:tom~novel#molten.com"
    
    Returns:
        AAPAddress object
    
    Raises:
        InvalidAddressError: If address format is invalid
    """
    if not address:
        raise InvalidAddressError("Address cannot be empty")
    
    # 总长度限制 (防止 DoS)
    if len(address) > 500:
        raise InvalidAddressError("Address too long (max 500 characters)")
    
    addr = address.strip()
    if not addr.lower().startswith("ai:"):
        raise InvalidAddressError("Address must start with 'ai:'")
    
    m = AAP_PATTERN.match(addr)
    if not m:
        raise InvalidAddressError(
            f"Invalid AAP address format: {address[:50]}... "
            "Expected: ai:owner~role#provider"
        )
    
    owner, role, provider = m.groups()
    
    # 验证各组件
    _validate_address_component(owner, "owner", MAX_OWNER_LENGTH)
    _validate_address_component(role, "role", MAX_ROLE_LENGTH)
    _validate_address_component(provider, "provider", MAX_PROVIDER_LENGTH, VALID_CHARS_PROVIDER)
    
    return AAPAddress(owner=owner, role=role, provider=provider.strip().lower())


def is_valid_address(address: str) -> bool:
    """Check if a string is a valid AAP address."""
    try:
        parse_address(address)
        return True
    except InvalidAddressError:
        return False


@dataclass
class ResolveResult:
    """Result of resolving an AAP address."""
    version: str
    aap: str
    public_key: str
    receive: Dict[str, str]
    capabilities: Optional[Dict[str, bool]] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> "ResolveResult":
        return cls(
            version=data.get("version", "0.03"),
            aap=data.get("aap", ""),
            public_key=data.get("public_key", ""),
            receive=data.get("receive", {}),
            capabilities=data.get("capabilities")
        )


@dataclass
class MessageEnvelope:
    """AAP message envelope."""
    from_addr: str
    to_addr: str
    message_type: str = "private"
    reply_to: Optional[str] = None
    content_type: str = "text/plain"
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat() + "Z"
    
    def to_dict(self) -> Dict:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class MessagePayload:
    """AAP message payload."""
    content: str
    metadata: Optional[Dict] = None
    
    def to_dict(self) -> Dict:
        data = {"content": self.content}
        if self.metadata:
            data["metadata"] = self.metadata
        return data


class AAPClient:
    """
    Main AAP Client for interacting with Providers.
    
    Usage:
        client = AAPClient()
        
        # Resolve an address
        info = client.resolve("ai:tom~novel#molten.com")
        
        # Send a message
        client.send_message(
            from_addr="ai:alice~main#provider.com",
            to_addr="ai:tom~novel#molten.com",
            content="Hello!"
        )
        
        # Receive messages
        messages = client.fetch_inbox("ai:tom~novel#molten.com", api_key="...")
    """
    
    def __init__(
        self,
        timeout: int = 10,
        verify_ssl: bool = True,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY
    ):
        """
        Initialize AAP Client.
        
        Args:
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates (set to False for local testing)
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def _request_with_retry(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with retry logic.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            url: Request URL
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            ProviderError: If all retries fail
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                r = requests.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    verify=self.verify_ssl,
                    **kwargs
                )
                r.raise_for_status()
                return r
            except requests.RequestException as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    sleep(self.retry_delay * (attempt + 1))  # 指数退避
                    continue
                raise ProviderError(
                    f"Provider unreachable after {self.max_retries} attempts: {url}"
                ) from last_error
        
        raise ProviderError(f"Request failed: {last_error}")
    
    def _get_url(self, provider: str, path: str) -> str:
        """Get URL, using http for localhost."""
        if "localhost" in provider or "127.0.0.1" in provider:
            return f"http://{provider}{path}"
        return f"https://{provider}{path}"
    
    def _resolve_provider(self, address: str) -> dict:
        """
        Resolve Provider endpoints from AAP address (v0.04 Stage 1: Direct).
        
        This method extracts the provider from an AAP address and returns
        the known endpoints. Stage 1 uses direct connection (domain-based URL).
        
        Future stages may add DNS SRV discovery with fallback to direct.
        
        Args:
            address: AAP address string
        
        Returns:
            dict with provider info:
                - provider: provider domain
                - resolve_url: resolve API URL
                - inbox_url: inbox API URL (base)
                - discovery_method: "direct"
        """
        addr = parse_address(address)
        provider = addr.provider
        base_url = self._get_url(provider, "")
        
        return {
            "provider": provider,
            "resolve_url": f"{base_url}/api/v1/resolve",
            "inbox_url": f"{base_url}/api/v1/inbox",
            "discovery_method": "direct"
        }
    
    def get_provider_info(self, provider: str) -> dict:
        """
        Get Provider info (optional endpoint).
        
        Calls /api/v1/providers/info if available.
        
        Args:
            provider: Provider domain
        
        Returns:
            dict with provider info, or None if endpoint not available
        """
        url = self._get_url(provider, "/api/v1/providers/info")
        
        try:
            r = requests.get(url, timeout=self.timeout, verify=self.verify_ssl)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()
        except requests.RequestException:
            return None
    
    def resolve(self, address: str) -> ResolveResult:
        """
        Resolve an AAP address to get provider info.
        
        Args:
            address: AAP address to resolve
        
        Returns:
            ResolveResult with provider endpoints
        
        Raises:
            InvalidAddressError: If address is invalid
            ResolveError: If resolve fails
        """
        addr = parse_address(address)
        url = self._get_url(addr.provider, "/api/v1/resolve")
        params = {"address": str(addr)}
        
        try:
            r = self._request_with_retry("GET", url, params=params)
            data = r.json()
            return ResolveResult.from_dict(data)
        except ProviderError as e:
            raise ResolveError(f"Failed to resolve {address}: {e}")
    
    def send_message(
        self,
        from_addr: str,
        to_addr: str,
        content: str,
        message_type: str = "private",
        reply_to: Optional[str] = None,
        content_type: str = "text/plain",
        metadata: Optional[Dict] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict:
        """
        Send a message to another Agent.
        
        Args:
            from_addr: Sender's AAP address
            to_addr: Recipient's AAP address
            content: Message content
            message_type: "private" or "public" (default: private)
            reply_to: Original message ID if replying
            content_type: MIME type (default: text/plain)
            metadata: Optional metadata dict
            idempotency_key: Optional key to prevent duplicate messages
        
        Returns:
            API response dict
        
        Raises:
            MessageError: If send fails
        """
        from_parsed = parse_address(from_addr)
        to_parsed = parse_address(to_addr)
        
        resolve_info = self.resolve(to_addr)
        inbox_url = resolve_info.receive.get("inbox_url")
        
        if not inbox_url:
            raise MessageError(f"No inbox URL for {to_addr}")
        
        envelope = MessageEnvelope(
            from_addr=str(from_parsed),
            to_addr=str(to_parsed),
            message_type=message_type,
            reply_to=reply_to,
            content_type=content_type
        )
        
        payload = MessagePayload(content=content, metadata=metadata)
        
        body = {
            "envelope": envelope.to_dict(),
            "payload": payload.to_dict()
        }
        
        # 添加幂等性 key
        headers = {"Content-Type": "application/json"}
        if idempotency_key:
            headers["X-Idempotency-Key"] = idempotency_key
        elif message_type == "private":
            headers["X-Idempotency-Key"] = secrets.token_urlsafe(16)
        
        try:
            r = self._request_with_retry(
                "POST",
                inbox_url,
                json=body,
                headers=headers
            )
            return r.json()
        except ProviderError as e:
            raise MessageError(f"Failed to send message: {e}")
    
    def fetch_inbox(
        self,
        address: str,
        api_key: str,
        limit: int = 20
    ) -> List[Dict]:
        """
        Fetch messages from inbox.
        
        Args:
            address: Your AAP address
            api_key: Your API key
            limit: Max messages to fetch
        
        Returns:
            List of message dicts
        """
        addr = parse_address(address)
        url = self._get_url(addr.provider, "/api/v1/inbox")
        
        headers = {"Authorization": f"Bearer {api_key}"}
        params = {"limit": limit}
        
        try:
            r = self._request_with_retry("GET", url, headers=headers, params=params)
            return r.json().get("messages", [])
        except ProviderError as e:
            raise MessageError(f"Failed to fetch inbox: {e}")
    
    def publish(
        self,
        from_addr: str,
        content: str,
        content_type: str = "text/plain",
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Publish to public feed.
        
        Args:
            from_addr: Sender's AAP address
            content: Post content
            content_type: MIME type
            metadata: Optional metadata
        
        Returns:
            API response dict
        """
        return self.send_message(
            from_addr=from_addr,
            to_addr="ai:feed~public#" + parse_address(from_addr).provider,
            content=content,
            message_type="public",
            content_type=content_type,
            metadata=metadata
        )


def create_client() -> AAPClient:
    """Create a new AAP client instance."""
    return AAPClient()


# Convenience functions
resolve = lambda addr: create_client().resolve(addr)
send = lambda from_addr, to_addr, content: create_client().send_message(from_addr, to_addr, content)
