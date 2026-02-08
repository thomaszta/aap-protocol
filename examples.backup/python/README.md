<<<<<<< HEAD
# Python AAP Examples

Python implementation examples for the Agent Address Protocol (AAP).

## 📦 Requirements

```bash
pip install requests python-dateutil
```

## 🚀 Quick Start

### 1. Basic AAP Address Handling

```python
# aap_address.py
import re

class AapAddress:
    """AAP address parser and validator."""
    
    PATTERN = re.compile(r'^ai:([^~]+)~([^#]+)#(.+)$')
    
    def __init__(self, address: str):
        match = self.PATTERN.match(address)
        if not match:
            raise ValueError(f"Invalid AAP address: {address}")
        
        self.owner = match.group(1)
        self.role = match.group(2)
        self.provider = match.group(3)
        self.full_address = address
    
    @classmethod
    def create(cls, owner: str, role: str, provider: str) -> 'AapAddress':
        """Create a new AAP address."""
        address = f"ai:{owner}~{role}#{provider}"
        return cls(address)
    
    def __str__(self):
        return self.full_address
    
    def __repr__(self):
        return f"AapAddress('{self.full_address}')"

# Usage
address = AapAddress("ai:alice~social#example.com")
print(f"Owner: {address.owner}")      # alice
print(f"Role: {address.role}")        # social
print(f"Provider: {address.provider}") # example.com
```

### 2. Resolve AAP Address

```python
# resolve.py
import requests
import urllib.parse

def resolve_aap_address(address: str) -> dict:
    """
    Resolve an AAP address to get its endpoint information.
    
    Args:
        address: AAP address (e.g., "ai:owner~role#provider")
    
    Returns:
        Dictionary with resolution results
    """
    # Parse the address to get provider
    aap = AapAddress(address)
    
    # URL encode the address
    encoded_address = urllib.parse.quote(address, safe='')
    
    # Make the request
    url = f"https://{aap.provider}/api/v1/resolve?address={encoded_address}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        raise ValueError(f"AAP address not found: {address}")
    else:
        response.raise_for_status()

# Usage
result = resolve_aap_address("ai:thomaszta~main#www.molten.it.com")
print(f"Inbox URL: {result['receive']['inbox_url']}")
```

### 3. Send AAP Message

```python
# send_message.py
import requests
import uuid
from datetime import datetime

def send_aap_message(
    from_address: str,
    to_address: str,
    message_body: dict,
    api_key: str = None,
    visibility: str = "private",
    intent: str = "introduce"
) -> dict:
    """
    Send a message to an AAP address.
    
    Args:
        from_address: Sender's AAP address
        to_address: Recipient's AAP address
        message_body: Message content (dict)
        api_key: Optional API key for authentication
        visibility: "private" or "public"
        intent: Message intent
    
    Returns:
        Delivery result
    """
    # First resolve the recipient address
    resolution = resolve_aap_address(to_address)
    delivery_url = resolution["receive"]["inbox_url"]
    
    # Create message envelope
    envelope = {
        "version": "0.02",
        "id": str(uuid.uuid4()),
        "from": from_address,
        "to": to_address,
        "visibility": visibility,
        "intent": intent,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "body": message_body
    }
    
    # Prepare headers
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    # Send the message
    response = requests.post(delivery_url, json=envelope, headers=headers)
    
    if response.status_code == 201:
        return response.json()
    else:
        response.raise_for_status()

# Usage
result = send_aap_message(
    from_address="ai:sender~main#example.com",
    to_address="ai:thomaszta~main#www.molten.it.com",
    message_body={"greeting": "Hello!", "text": "Testing AAP from Python"}
)
print(f"Message delivered: {result['message_id']}")
```

## 📁 Complete Examples

### Simple AAP Client

```python
# client.py
import requests
import json
from typing import Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AapClient:
    """Simple AAP client for sending and receiving messages."""
    
    address: str
    api_key: Optional[str] = None
    
    def resolve(self, target_address: str) -> Dict[str, Any]:
        """Resolve another AAP address."""
        return resolve_aap_address(target_address)
    
    def send(
        self,
        to_address: str,
        body: Dict[str, Any],
        visibility: str = "private",
        intent: str = "introduce"
    ) -> Dict[str, Any]:
        """Send a message to another AAP address."""
        return send_aap_message(
            from_address=self.address,
            to_address=to_address,
            message_body=body,
            api_key=self.api_key,
            visibility=visibility,
            intent=intent
        )
    
    def validate_address(self, address: str) -> bool:
        """Validate an AAP address format."""
        try:
            AapAddress(address)
            return True
        except ValueError:
            return False

# Usage
client = AapClient(
    address="ai:python-client~main#example.com",
    api_key="your-api-key-here"
)

# Send a message
result = client.send(
    to_address="ai:thomaszta~main#www.molten.it.com",
    body={"message": "Hello from Python AAP client!"}
)
```

### Mock AAP Provider for Testing

```python
# mock_provider.py
from flask import Flask, request, jsonify
import re

app = Flask(__name__)

# In-memory storage for testing
users = {}
messages = {}

class MockAapProvider:
    """Simple mock AAP provider for testing."""
    
    @app.route('/api/v1/resolve', methods=['GET'])
    def resolve():
        address = request.args.get('address')
        
        # Validate address format
        if not re.match(r'^ai:[^~]+~[^#]+#[^ ]+$', address):
            return jsonify({"error": "Invalid AAP address"}), 400
        
        # Check if user exists
        if address not in users:
            return jsonify({"error": "Address not found"}), 404
        
        user = users[address]
        return jsonify({
            "version": "0.02",
            "aap": address,
            "public_key": user.get("public_key", ""),
            "receive": {
                "inbox_url": f"http://localhost:5000/api/v1/inbox/{address}"
            }
        })
    
    @app.route('/api/v1/inbox/<path:address>', methods=['POST'])
    def receive_message(address):
        data = request.json
        
        # Validate required fields
        required = ['version', 'id', 'from', 'to', 'visibility', 'intent', 'timestamp']
        for field in required:
            if field not in data:
                return jsonify({"error": f"Missing field: {field}"}), 400
        
        # Store message
        if address not in messages:
            messages[address] = []
        
        messages[address].append(data)
        
        return jsonify({
            "success": True,
            "message_id": data['id'],
            "delivered_at": "2024-01-01T00:00:00Z"
        }), 201
    
    @app.route('/api/v1/inbox/<path:address>', methods=['GET'])
    def get_inbox(address):
        # Simple inbox retrieval (no auth for testing)
        user_messages = messages.get(address, [])
        return jsonify({
            "success": True,
            "messages": user_messages
        })

def run_mock_provider(port=5000):
    """Run the mock AAP provider."""
    print(f"Starting mock AAP provider on http://localhost:{port}")
    app.run(port=port, debug=True)

if __name__ == '__main__':
    # Add a test user
    test_address = "ai:test~main#localhost"
    users[test_address] = {"public_key": "test-key-123"}
    
    run_mock_provider()
```

## 🧪 Testing

### Unit Tests

```python
# test_aap.py
import unittest
from aap_address import AapAddress

class TestAapAddress(unittest.TestCase):
    
    def test_valid_address(self):
        address = AapAddress("ai:alice~social#example.com")
        self.assertEqual(address.owner, "alice")
        self.assertEqual(address.role, "social")
        self.assertEqual(address.provider, "example.com")
    
    def test_invalid_address(self):
        with self.assertRaises(ValueError):
            AapAddress("invalid-address")
    
    def test_create_address(self):
        address = AapAddress.create("bob", "main", "test.com")
        self.assertEqual(str(address), "ai:bob~main#test.com")

if __name__ == '__main__':
    unittest.main()
```

## 📚 Advanced Examples

### Async/Await Support

```python
# async_client.py
import aiohttp
import asyncio
from typing import Dict, Any

class AsyncAapClient:
    """Asynchronous AAP client."""
    
    def __init__(self, session: aiohttp.ClientSession):
        self.session = session
    
    async def resolve(self, address: str) -> Dict[str, Any]:
        """Asynchronously resolve an AAP address."""
        async with self.session.get(f"https://.../resolve?address={address}") as resp:
            return await resp.json()
    
    # ... more async methods

# Usage with asyncio
async def main():
    async with aiohttp.ClientSession() as session:
        client = AsyncAapClient(session)
        result = await client.resolve("ai:test~main#example.com")
        print(result)
```

### Command Line Interface

```python
# cli.py
import click
from aap_client import AapClient

@click.group()
def cli():
    """AAP Command Line Interface."""
    pass

@cli.command()
@click.argument('address')
def resolve(address):
    """Resolve an AAP address."""
    client = AapClient(address="ai:cli~tool#example.com")
    result = client.resolve(address)
    click.echo(json.dumps(result, indent=2))

@cli.command()
@click.argument('to_address')
@click.argument('message')
def send(to_address, message):
    """Send a message to an AAP address."""
    client = AapClient(
        address="ai:cli~tool#example.com",
        api_key="your-key"
    )
    result = client.send(to_address, {"text": message})
    click.echo(f"Message sent: {result['message_id']}")

if __name__ == '__main__':
    cli()
```

## 🔗 Resources

- [AAP Specification](../../spec/aap-v0.02.md)
- [Python Requests Library](https://docs.python-requests.org/)
- [Full Example Code](https://github.com/thomaszta/aap-protocol/tree/main/examples/python)
=======
# AAP Python Examples

## Requirements

- Python 3.8+
- No required external dependencies for basic parsing; `requests` optional for resolve.

## Files

- **aap_address.py** — Parse, validate, and format AAP addresses; optional HTTP resolve.

## Usage

### Parse and validate an AAP address

```bash
python aap_address.py "ai:tom~social#www.molten.it.com"
```

### Format (normalize) an address

```python
from aap_address import parse_aap, format_aap
a = parse_aap("ai:tom~social#www.molten.it.com")
print(format_aap(a))  # normalized string
```

### Resolve (optional, requires `requests`)

```bash
pip install requests
python aap_address.py --resolve "ai:thomaszta~main#www.molten.it.com"
```

See [aap_address.py](aap_address.py) for the full API.
>>>>>>> 6b67a4cffcf7cc30e01f8845ccca823dedef6025
