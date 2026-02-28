"""
AAP (Agent Address Protocol) Python SDK
https://github.com/thomaszta/aap-protocol

Usage:
    pip install aap-sdk
"""

import re
import urllib.parse
import json
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime

import requests

__version__ = "0.1.0"

AAP_PATTERN = re.compile(
    r"^ai:([^~#]+)~([^#]+)#(.+)$",
    re.IGNORECASE
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
    
    addr = address.strip()
    if not addr.lower().startswith("ai:"):
        raise InvalidAddressError("Address must start with 'ai:'")
    
    m = AAP_PATTERN.match(addr)
    if not m:
        raise InvalidAddressError(
            f"Invalid AAP address format: {address}. "
            "Expected: ai:owner~role#provider"
        )
    
    owner, role, provider = m.groups()
    if not owner or not role or not provider:
        raise InvalidAddressError("Owner, role, and provider cannot be empty")
    
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
    
    def __init__(self, timeout: int = 10, verify_ssl: bool = True):
        """
        Initialize AAP Client.
        
        Args:
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates (set to False for local testing)
        """
        self.timeout = timeout
        self.verify_ssl = verify_ssl
    
    def _get_url(self, provider: str, path: str) -> str:
        """Get URL, using http for localhost."""
        if "localhost" in provider or "127.0.0.1" in provider:
            return f"http://{provider}{path}"
        return f"https://{provider}{path}"
    
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
            r = requests.get(url, params=params, timeout=self.timeout, verify=self.verify_ssl)
            r.raise_for_status()
            data = r.json()
            return ResolveResult.from_dict(data)
        except requests.RequestException as e:
            raise ResolveError(f"Failed to resolve {address}: {e}")
    
    def send_message(
        self,
        from_addr: str,
        to_addr: str,
        content: str,
        message_type: str = "private",
        reply_to: Optional[str] = None,
        content_type: str = "text/plain",
        metadata: Optional[Dict] = None
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
        
        try:
            r = requests.post(
                inbox_url,
                json=body,
                headers={"Content-Type": "application/json"},
                timeout=self.timeout,
                verify=self.verify_ssl
            )
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
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
            r = requests.get(url, headers=headers, params=params, timeout=self.timeout, verify=self.verify_ssl)
            r.raise_for_status()
            return r.json().get("messages", [])
        except requests.RequestException as e:
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
