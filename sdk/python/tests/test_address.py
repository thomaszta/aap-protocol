import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import aap
from aap import (
    AAPAddress,
    parse_address,
    is_valid_address,
    InvalidAddressError,
    ResolveError,
    MessageError,
    ProviderError,
    AAPClient
)


class TestAddressParsing:
    """Test address parsing and validation."""
    
    def test_parse_valid_address(self):
        """Test parsing valid AAP address."""
        addr = parse_address("ai:tom~novel#molten.com")
        
        assert isinstance(addr, AAPAddress)
        assert addr.owner == "tom"
        assert addr.role == "novel"
        assert addr.provider == "molten.com"
    
    def test_parse_address_with_subdomain(self):
        """Test parsing address with subdomain."""
        addr = parse_address("ai:writer~main#fiction.molten.it.com")
        
        assert addr.owner == "writer"
        assert addr.role == "main"
        assert addr.provider == "fiction.molten.it.com"
    
    def test_parse_address_case_insensitive(self):
        """Test that parsing is case insensitive."""
        addr = parse_address("AI:TOM~NOVEL#Molten.Com")
        
        assert addr.owner == "TOM"
        assert addr.role == "NOVEL"
        assert addr.provider == "molten.com"  # normalized to lowercase
    
    def test_parse_invalid_no_prefix(self):
        """Test that missing 'ai:' prefix raises error."""
        with pytest.raises(InvalidAddressError) as exc:
            parse_address("tom~novel#molten.com")
        assert "must start with 'ai:'" in str(exc.value)
    
    def test_parse_invalid_empty_owner(self):
        """Test that empty owner raises error."""
        with pytest.raises(InvalidAddressError):
            parse_address("ai:~novel#molten.com")
    
    def test_parse_invalid_empty_role(self):
        """Test that empty role raises error."""
        with pytest.raises(InvalidAddressError):
            parse_address("ai:tom~#molten.com")
    
    def test_parse_invalid_empty_provider(self):
        """Test that empty provider raises error."""
        with pytest.raises(InvalidAddressError):
            parse_address("ai:tom~novel#")
    
    def test_parse_invalid_no_role_separator(self):
        """Test that missing ~ raises error."""
        with pytest.raises(InvalidAddressError):
            parse_address("ai:tom#molten.com")
    
    def test_parse_invalid_no_provider_separator(self):
        """Test that missing # raises error."""
        with pytest.raises(InvalidAddressError):
            parse_address("ai:tom~novelmolten.com")
    
    def test_address_to_string(self):
        """Test address to string conversion."""
        addr = AAPAddress(owner="tom", role="novel", provider="molten.com")
        
        assert str(addr) == "ai:tom~novel#molten.com"
    
    def test_address_length_limit_owner(self):
        """Test owner length limit."""
        long_owner = "a" * 65  # MAX_OWNER_LENGTH is 64
        
        with pytest.raises(InvalidAddressError) as exc:
            parse_address(f"ai:{long_owner}~role#provider.com")
        assert "too long" in str(exc.value).lower()
    
    def test_address_length_limit_total(self):
        """Test total address length limit."""
        long_address = "ai:" + "a" * 500 + "~role#provider.com"
        
        with pytest.raises(InvalidAddressError) as exc:
            parse_address(long_address)
        assert "too long" in str(exc.value).lower()
    
    def test_invalid_characters(self):
        """Test that invalid characters are rejected."""
        with pytest.raises(InvalidAddressError) as exc:
            parse_address("ai:tom<script>~novel#molten.com")
        assert "invalid" in str(exc.value).lower()


class TestAddressValidation:
    """Test address validation functions."""
    
    def test_is_valid_address_true(self):
        """Test valid address returns True."""
        assert is_valid_address("ai:tom~novel#molten.com") is True
    
    def test_is_valid_address_false(self):
        """Test invalid address returns False."""
        assert is_valid_address("invalid") is False
        assert is_valid_address("") is False
    
    def test_is_valid_address_edge_cases(self):
        """Test edge cases."""
        # Valid edge cases
        assert is_valid_address("ai:a~b#c.d") is True
        assert is_valid_address("ai:a-b~c_d#e.f") is True


class TestAAPClient:
    """Test AAP Client."""
    
    def test_client_init_defaults(self):
        """Test client initialization with defaults."""
        client = AAPClient()
        
        assert client.timeout == 10
        assert client.verify_ssl is True
        assert client.max_retries == 3
    
    def test_client_init_custom(self):
        """Test client initialization with custom values."""
        client = AAPClient(
            timeout=30,
            verify_ssl=False,
            max_retries=5
        )
        
        assert client.timeout == 30
        assert client.verify_ssl is False
        assert client.max_retries == 5
    
    def test_resolve_invalid_address(self):
        """Test resolve with invalid address raises error."""
        client = AAPClient()
        
        with pytest.raises(InvalidAddressError):
            client.resolve("invalid")
    
    def test_get_provider_info_invalid(self):
        """Test get_provider_info with invalid address."""
        client = AAPClient()
        
        result = client._resolve_provider("ai:tom~novel#molten.com")
        
        assert result["provider"] == "molten.com"
        assert "resolve_url" in result
        assert "inbox_url" in result
        assert result["discovery_method"] == "direct"


class TestAddressEdgeCases:
    """Test address edge cases."""
    
    def test_localhost_provider(self):
        """Test localhost provider."""
        addr = parse_address("ai:tom~main#localhost:5000")
        
        assert addr.provider == "localhost:5000"
    
    def test_ip_provider(self):
        """Test IP address as provider."""
        addr = parse_address("ai:tom~main#192.168.1.1")
        
        assert addr.provider == "192.168.1.1"
    
    def test_dash_in_owner(self):
        """Test dash in owner/role."""
        addr = parse_address("ai:my-agent~social#provider.com")
        
        assert addr.owner == "my-agent"
        assert addr.role == "social"
    
    def test_underscore_in_role(self):
        """Test underscore in role."""
        addr = parse_address("ai:tom~main_role#provider.com")
        
        assert addr.role == "main_role"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
