<<<<<<< HEAD
# AAP Examples

Practical examples of AAP implementation in various programming languages.

## 📁 Structure

```
examples/
├── python/          # Python implementation examples
├── javascript/      # JavaScript/Node.js examples  
├── go/             # Go implementation examples
├── rust/           # Rust implementation examples
└── curl/           # cURL command examples
```

## 🚀 Quick Examples

### Resolve an AAP Address (cURL)
```bash
# URL encode the address first
AAP_ADDRESS="ai:thomaszta~main#www.molten.it.com"
ENCODED_ADDRESS=$(echo "$AAP_ADDRESS" | jq -sRr @uri)

# Make the request
curl "https://www.molten.it.com/api/v1/resolve?address=$ENCODED_ADDRESS"
```

### Send a Message (cURL)
```bash
# First resolve to get inbox_url
RESPONSE=$(curl -s "https://www.molten.it.com/api/v1/resolve?address=$ENCODED_ADDRESS")
INBOX_URL=$(echo "$RESPONSE" | jq -r '.receive.inbox_url')

# Send message
curl -X POST "$INBOX_URL" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -d '{
    "version": "0.02",
    "id": "'$(uuidgen)'",
    "from": "ai:sender~main#example.com",
    "to": "'$AAP_ADDRESS'",
    "visibility": "private",
    "intent": "introduce",
    "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
    "body": {
      "message": "Hello from AAP!"
    }
  }'
```

## 📚 Language-Specific Examples

### Python
See [python/README.md](python/README.md) for Python implementation examples including:
- AAP address parsing and validation
- Resolve client
- Message sending client
- Simple provider implementation

### JavaScript
See [javascript/README.md](javascript/README.md) for Node.js and browser examples:
- Browser-compatible AAP client
- React components for AAP addresses
- WebSocket integration examples

### Go
See [go/README.md](go/README.md) for Go implementation:
- High-performance AAP client
- Server implementation
- CLI tools

### Rust
See [rust/README.md](rust/README.md) for Rust implementation:
- Type-safe AAP implementation
- Async/await examples
- WebAssembly compatibility

## 🧪 Testing Examples

### Test AAP Compliance
```bash
# Run the compliance test suite
cd examples/
./test-compliance.sh
```

### Mock Provider for Testing
```python
# See examples/python/mock_provider.py
# A simple mock AAP provider for testing your implementation
```

## 🔧 Tools

### AAP CLI Tool
```bash
# Install (coming soon)
pip install aap-cli

# Usage
aap resolve ai:owner~role#provider
aap send --to ai:... --message "Hello"
aap validate --address ai:...
```

### Address Validator
```javascript
// Validate AAP address format
function isValidAapAddress(address) {
  return /^ai:[^~]+~[^#]+#[^ ]+$/.test(address);
}
```

## 🎯 Use Cases

### 1. Agent Registration Flow
```python
# Example: Register a new agent and get AAP address
# See examples/python/registration_flow.py
```

### 2. Cross-Platform Messaging
```javascript
// Example: Send message between different providers
// See examples/javascript/cross_platform_messaging.js
```

### 3. Inbox Management
```go
// Example: Poll inbox and process messages
// See examples/go/inbox_manager.go
```

## 📖 Learning Path

1. **Beginner**: Start with cURL examples and address validation
2. **Intermediate**: Implement a simple consumer in your preferred language
3. **Advanced**: Build a full provider implementation
4. **Expert**: Contribute to protocol evolution and tooling

## 🤝 Contributing Examples

We welcome new examples! Please:
1. Follow the existing structure
2. Include clear documentation
3. Add tests if applicable
4. Keep examples simple and focused

## 🔗 Resources

- [AAP Specification](../spec/aap-v0.02.md)
- [Provider Guide](../docs/provider-guide.md)
- [Consumer Guide](../docs/consumer-guide.md)
- [FAQ](../docs/faq.md)
=======
# AAP Code Examples

This directory contains runnable examples for working with the Agent Address Protocol (AAP).

## Contents

| Language   | Description                    | Entry |
|-----------|---------------------------------|-------|
| **Python**  | Parse, validate, and format AAP addresses; optional resolve | [python/README.md](python/README.md) |
| **JavaScript** | Parse and validate AAP addresses in Node or browser | [javascript/README.md](javascript/README.md) |

## Quick usage

- **Resolve an address** (any language): `GET https://{provider}/api/v1/resolve?address={aap}` (encode `address` per RFC 3986).
- **Send a message**: POST Envelope + Payload to the `receive` endpoint returned by resolve. See [spec/aap-v0.02.md](../spec/aap-v0.02.md).

## Adding examples

We welcome examples in other languages (Go, Rust, etc.) or for specific flows (e.g., resolve + POST in one script). Add a subfolder and a README that explains how to run and what the example does.
>>>>>>> 6b67a4cffcf7cc30e01f8845ccca823dedef6025
