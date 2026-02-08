#!/usr/bin/env python3
"""
<<<<<<< HEAD
AAP Address Parser and Validator

This module provides tools for working with AAP (Agent Address Protocol) addresses.
"""

import re
from typing import Optional, Tuple
from dataclasses import dataclass


@dataclass
class AapAddress:
    """AAP address representation."""
    
    owner: str
    role: str
    provider: str
    full_address: str
    
    # AAP address pattern: ai:owner~role#provider
    PATTERN = re.compile(r'^ai:([^~]+)~([^#]+)#(.+)$')
    
    def __init__(self, address: str):
        """
        Parse an AAP address.
        
        Args:
            address: AAP address string (e.g., "ai:owner~role#provider")
        
        Raises:
            ValueError: If the address format is invalid
        """
        match = self.PATTERN.match(address)
        if not match:
            raise ValueError(f"Invalid AAP address format: {address}")
        
        self.owner = match.group(1)
        self.role = match.group(2)
        self.provider = match.group(3)
        self.full_address = address
    
    @classmethod
    def create(cls, owner: str, role: str, provider: str) -> 'AapAddress':
        """
        Create a new AAP address from components.
        
        Args:
            owner: Identity owner
            role: Function/purpose role
            provider: FQDN provider
        
        Returns:
            AapAddress instance
        """
        # Basic validation
        if not owner or '~' in owner or '#' in owner:
            raise ValueError(f"Invalid owner: {owner}")
        if not role or '~' in role or '#' in role:
            raise ValueError(f"Invalid role: {role}")
        if not provider or '#' in provider:
            raise ValueError(f"Invalid provider: {provider}")
        
        address = f"ai:{owner}~{role}#{provider}"
        return cls(address)
    
    @classmethod
    def parse(cls, address: str) -> Optional['AapAddress']:
        """
        Parse an AAP address, returning None if invalid.
        
        Args:
            address: AAP address string
        
        Returns:
            AapAddress or None if invalid
        """
        try:
            return cls(address)
        except ValueError:
            return None
    
    def is_valid(self) -> bool:
        """Check if this address is valid."""
        return bool(self.PATTERN.match(self.full_address))
    
    def components(self) -> Tuple[str, str, str]:
        """Get address components as a tuple."""
        return (self.owner, self.role, self.provider)
    
    def normalize(self) -> 'AapAddress':
        """
        Normalize the address (lowercase, etc.).
        
        Returns:
            Normalized AapAddress
        """
        normalized_owner = self.owner.lower()
        normalized_role = self.role.lower()
        normalized_provider = self.provider.lower()
        
        if (normalized_owner == self.owner and 
            normalized_role == self.role and 
            normalized_provider == self.provider):
            return self
        
        return self.create(normalized_owner, normalized_role, normalized_provider)
    
    def __str__(self) -> str:
        return self.full_address
    
    def __repr__(self) -> str:
        return f"AapAddress('{self.full_address}')"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, AapAddress):
            return False
        return self.normalize().full_address == other.normalize().full_address
    
    def __hash__(self) -> int:
        return hash(self.normalize().full_address)


def is_valid_aap_address(address: str) -> bool:
    """
    Check if a string is a valid AAP address.
    
    Args:
        address: String to check
    
    Returns:
        True if valid AAP address
    """
    return bool(AapAddress.PATTERN.match(address))


def parse_aap_address(address: str) -> Optional[Tuple[str, str, str]]:
    """
    Parse AAP address into components.
    
    Args:
        address: AAP address string
    
    Returns:
        Tuple of (owner, role, provider) or None if invalid
    """
    aap = AapAddress.parse(address)
    return aap.components() if aap else None


def create_aap_address(owner: str, role: str, provider: str) -> str:
    """
    Create an AAP address from components.
    
    Args:
        owner: Identity owner
        role: Function/purpose role
        provider: FQDN provider
    
    Returns:
        AAP address string
    """
    return str(AapAddress.create(owner, role, provider))


# Example usage
if __name__ == "__main__":
    # Test valid addresses
    test_addresses = [
        "ai:alice~social#example.com",
        "ai:bob~main#test.org",
        "ai:charlie~sales#company.co.uk",
    ]
    
    print("Testing AAP address validation:")
    for addr in test_addresses:
        is_valid = is_valid_aap_address(addr)
        print(f"  {addr}: {'✓' if is_valid else '✗'}")
        
        if is_valid:
            aap = AapAddress(addr)
            print(f"    Owner: {aap.owner}")
            print(f"    Role: {aap.role}")
            print(f"    Provider: {aap.provider}")
    
    # Test invalid addresses
    invalid_addresses = [
        "invalid",
        "ai:owner#provider",  # missing role
        "ai:owner~role",      # missing provider
        "ai:~role#provider",  # missing owner
    ]
    
    print("\nTesting invalid addresses:")
    for addr in invalid_addresses:
        is_valid = is_valid_aap_address(addr)
        print(f"  {addr}: {'✓' if is_valid else '✗' (expected)}")
    
    # Test creation
    print("\nTesting address creation:")
    new_addr = create_aap_address("david", "support", "help.example.com")
    print(f"  Created: {new_addr}")
    
    # Test normalization
    print("\nTesting normalization:")
    mixed_case = AapAddress("ai:Alice~MAIN#Example.COM")
    normalized = mixed_case.normalize()
    print(f"  Original: {mixed_case}")
    print(f"  Normalized: {normalized}")
    print(f"  Equal: {mixed_case == normalized}")
=======
AAP (Agent Address Protocol) address parsing, validation, and optional resolve.
Spec: https://github.com/thomaszta/aap-protocol/blob/main/spec/aap-v0.02.md
"""

import re
import urllib.parse
import json
from dataclasses import dataclass
from typing import Optional, Tuple


AAP_PATTERN = re.compile(
    r"^ai:([^~#]+)~([^#]+)#(.+)$",
    re.IGNORECASE
)


@dataclass
class AAPAddress:
    """Parsed AAP address: ai:owner~role#provider."""
    owner: str
    role: str
    provider: str

    def __str__(self) -> str:
        return f"ai:{self.owner}~{self.role}#{self.provider}"


def parse_aap(address: str) -> Optional[AAPAddress]:
    """
    Parse an AAP address string into owner, role, provider.
    Returns None if invalid.
    """
    if not address or not address.strip().lower().startswith("ai:"):
        return None
    m = AAP_PATTERN.match(address.strip())
    if not m:
        return None
    owner, role, provider = m.groups()
    if not owner or not role or not provider:
        return None
    return AAPAddress(owner=owner, role=role, provider=provider.strip().lower())


def is_valid_aap(address: str) -> bool:
    """Return True if the string is a valid AAP address."""
    return parse_aap(address) is not None


def format_aap(addr: AAPAddress) -> str:
    """Return normalized AAP string (provider lowercased)."""
    return str(addr)


def resolve_aap(address: str) -> Optional[dict]:
    """
    Resolve an AAP address via GET https://{provider}/api/v1/resolve?address={aap}.
    Requires 'requests'. Returns the JSON response or None on failure.
    """
    addr = parse_aap(address)
    if not addr:
        return None
    try:
        import requests
    except ImportError:
        return None
    url = f"https://{addr.provider}/api/v1/resolve"
    params = {"address": str(addr)}
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return None


def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage: python aap_address.py <aap_address> [--resolve]")
        sys.exit(1)
    raw = sys.argv[1]
    do_resolve = "--resolve" in sys.argv
    addr = parse_aap(raw)
    if not addr:
        print("Invalid AAP address", file=sys.stderr)
        sys.exit(2)
    print("Parsed:", format_aap(addr))
    if do_resolve:
        out = resolve_aap(raw)
        if out:
            print("Resolve response:", json.dumps(out, indent=2))
        else:
            print("Resolve failed", file=sys.stderr)
            sys.exit(3)


if __name__ == "__main__":
    main()
>>>>>>> 6b67a4cffcf7cc30e01f8845ccca823dedef6025
