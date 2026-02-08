#!/usr/bin/env python3
"""
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
