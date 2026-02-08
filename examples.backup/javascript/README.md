<<<<<<< HEAD
# JavaScript AAP Examples

JavaScript/Node.js implementation examples for the Agent Address Protocol (AAP).

## 📦 Installation

### Node.js
```bash
npm install axios
# or
yarn add axios
```

### Browser
```html
<script src="https://unpkg.com/axios/dist/axios.min.js"></script>
```

## 🚀 Quick Start

### 1. AAP Address Utilities

```javascript
// aap-address.js
class AapAddress {
  /**
   * Parse and validate an AAP address.
   * @param {string} address - AAP address string
   */
  constructor(address) {
    const match = address.match(/^ai:([^~]+)~([^#]+)#(.+)$/);
    if (!match) {
      throw new Error(`Invalid AAP address: ${address}`);
    }
    
    this.owner = match[1];
    this.role = match[2];
    this.provider = match[3];
    this.fullAddress = address;
  }
  
  /**
   * Create an AAP address from components.
   * @param {string} owner - Identity owner
   * @param {string} role - Function/purpose role
   * @param {string} provider - FQDN provider
   * @returns {AapAddress}
   */
  static create(owner, role, provider) {
    // Validate components
    if (!owner || owner.includes('~') || owner.includes('#')) {
      throw new Error(`Invalid owner: ${owner}`);
    }
    if (!role || role.includes('~') || role.includes('#')) {
      throw new Error(`Invalid role: ${role}`);
    }
    if (!provider || provider.includes('#')) {
      throw new Error(`Invalid provider: ${provider}`);
    }
    
    const address = `ai:${owner}~${role}#${provider}`;
    return new AapAddress(address);
  }
  
  /**
   * Parse an AAP address, returning null if invalid.
   * @param {string} address - AAP address string
   * @returns {AapAddress|null}
   */
  static parse(address) {
    try {
      return new AapAddress(address);
    } catch (error) {
      return null;
    }
  }
  
  /**
   * Check if a string is a valid AAP address.
   * @param {string} address - String to check
   * @returns {boolean}
   */
  static isValid(address) {
    return /^ai:[^~]+~[^#]+#[^ ]+$/.test(address);
  }
  
  /**
   * Normalize the address (lowercase).
   * @returns {AapAddress}
   */
  normalize() {
    const normalizedOwner = this.owner.toLowerCase();
    const normalizedRole = this.role.toLowerCase();
    const normalizedProvider = this.provider.toLowerCase();
    
    if (normalizedOwner === this.owner && 
        normalizedRole === this.role && 
        normalizedProvider === this.provider) {
      return this;
    }
    
    return AapAddress.create(normalizedOwner, normalizedRole, normalizedProvider);
  }
  
  toString() {
    return this.fullAddress;
  }
  
  toJSON() {
    return this.fullAddress;
  }
}

// Usage
const address = new AapAddress('ai:alice~social#example.com');
console.log(`Owner: ${address.owner}`);      // alice
console.log(`Role: ${address.role}`);        // social
console.log(`Provider: ${address.provider}`); // example.com

// Validation
console.log(AapAddress.isValid('ai:bob~main#test.org')); // true
console.log(AapAddress.isValid('invalid-address'));      // false
```

### 2. Resolve AAP Address

```javascript
// resolve.js
const axios = require('axios');

/**
 * Resolve an AAP address to get endpoint information.
 * @param {string} address - AAP address
 * @returns {Promise<object>} Resolution result
 */
async function resolveAapAddress(address) {
  // Validate address
  if (!AapAddress.isValid(address)) {
    throw new Error(`Invalid AAP address: ${address}`);
  }
  
  // Parse to get provider
  const aap = new AapAddress(address);
  
  // URL encode the address
  const encodedAddress = encodeURIComponent(address);
  
  // Make the request
  const url = `https://${aap.provider}/api/v1/resolve?address=${encodedAddress}`;
  const response = await axios.get(url);
  
  if (response.status === 200) {
    return response.data;
  } else if (response.status === 404) {
    throw new Error(`AAP address not found: ${address}`);
  } else {
    throw new Error(`Resolution failed: ${response.status}`);
  }
}

// Usage
async function example() {
  try {
    const result = await resolveAapAddress('ai:thomaszta~main#www.molten.it.com');
    console.log('Inbox URL:', result.receive.inbox_url);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

example();
```

### 3. Send AAP Message

```javascript
// send-message.js
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

/**
 * Send a message to an AAP address.
 * @param {string} fromAddress - Sender's AAP address
 * @param {string} toAddress - Recipient's AAP address
 * @param {object} body - Message content
 * @param {string} [apiKey] - Optional API key for authentication
 * @param {string} [visibility='private'] - 'private' or 'public'
 * @param {string} [intent='introduce'] - Message intent
 * @returns {Promise<object>} Delivery result
 */
async function sendAapMessage({
  fromAddress,
  toAddress,
  body,
  apiKey,
  visibility = 'private',
  intent = 'introduce'
}) {
  // Validate addresses
  if (!AapAddress.isValid(fromAddress)) {
    throw new Error(`Invalid from address: ${fromAddress}`);
  }
  if (!AapAddress.isValid(toAddress)) {
    throw new Error(`Invalid to address: ${toAddress}`);
  }
  
  // First resolve the recipient address
  const resolution = await resolveAapAddress(toAddress);
  const deliveryUrl = resolution.receive.inbox_url;
  
  // Create message envelope
  const envelope = {
    version: '0.02',
    id: uuidv4(),
    from: fromAddress,
    to: toAddress,
    visibility,
    intent,
    timestamp: new Date().toISOString(),
    body
  };
  
  // Prepare headers
  const headers = {
    'Content-Type': 'application/json'
  };
  
  if (apiKey) {
    headers.Authorization = `Bearer ${apiKey}`;
  }
  
  // Send the message
  const response = await axios.post(deliveryUrl, envelope, { headers });
  
  if (response.status === 201) {
    return response.data;
  } else {
    throw new Error(`Delivery failed: ${response.status}`);
  }
}

// Usage
async function example() {
  try {
    const result = await sendAapMessage({
      fromAddress: 'ai:sender~main#example.com',
      toAddress: 'ai:thomaszta~main#www.molten.it.com',
      body: {
        greeting: 'Hello!',
        text: 'Testing AAP from JavaScript'
      }
    });
    
    console.log('Message delivered:', result.message_id);
  } catch (error) {
    console.error('Error:', error.message);
  }
}

example();
```

## 📁 Complete Examples

### Simple AAP Client Class

```javascript
// aap-client.js
class AapClient {
  /**
   * Create an AAP client.
   * @param {string} address - Client's AAP address
   * @param {string} [apiKey] - Optional API key
   */
  constructor(address, apiKey = null) {
    this.address = address;
    this.apiKey = apiKey;
  }
  
  /**
   * Resolve an AAP address.
   * @param {string} targetAddress - Address to resolve
   * @returns {Promise<object>}
   */
  async resolve(targetAddress) {
    return await resolveAapAddress(targetAddress);
  }
  
  /**
   * Send a message.
   * @param {string} toAddress - Recipient address
   * @param {object} body - Message body
   * @param {object} [options] - Additional options
   * @returns {Promise<object>}
   */
  async send(toAddress, body, options = {}) {
    return await sendAapMessage({
      fromAddress: this.address,
      toAddress,
      body,
      apiKey: this.apiKey,
      ...options
    });
  }
  
  /**
   * Validate an AAP address.
   * @param {string} address - Address to validate
   * @returns {boolean}
   */
  validateAddress(address) {
    return AapAddress.isValid(address);
  }
}

// Usage
const client = new AapClient(
  'ai:js-client~main#example.com',
  'your-api-key-here'
);

// Send a message
client.send(
  'ai:thomaszta~main#www.molten.it.com',
  { message: 'Hello from JavaScript AAP client!' }
).then(result => {
  console.log('Sent:', result);
}).catch(error => {
  console.error('Error:', error);
});
```

### React Component for AAP Addresses

```jsx
// AapAddressDisplay.jsx
import React, { useState } from 'react';

function AapAddressDisplay({ address }) {
  const [resolved, setResolved] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  const handleResolve = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await resolveAapAddress(address);
      setResolved(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };
  
  const isValid = AapAddress.isValid(address);
  
  return (
    <div className="aap-address-display">
      <div className="address-header">
        <code>{address}</code>
        <span className={`status-badge ${isValid ? 'valid' : 'invalid'}`}>
          {isValid ? '✓ Valid' : '✗ Invalid'}
        </span>
      </div>
      
      {isValid && (
        <div className="address-actions">
          <button 
            onClick={handleResolve}
            disabled={loading}
          >
            {loading ? 'Resolving...' : 'Resolve Address'}
          </button>
        </div>
      )}
      
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
      
      {resolved && (
        <div className="resolution-result">
          <h4>Resolution Result:</h4>
          <pre>{JSON.stringify(resolved, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default AapAddressDisplay;
```

### Browser-Compatible AAP Client

```javascript
// browser-client.js
// Works in both Node.js and browser environments

class BrowserAapClient {
  constructor(address, apiKey = null) {
    this.address = address;
    this.apiKey = apiKey;
  }
  
  async resolve(targetAddress) {
    // Use fetch API which works in both environments
    const encodedAddress = encodeURIComponent(targetAddress);
    const aap = new AapAddress(targetAddress);
    const url = `https://${aap.provider}/api/v1/resolve?address=${encodedAddress}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error(`AAP address not found: ${targetAddress}`);
      }
      throw new Error(`Resolution failed: ${response.status}`);
    }
    
    return await response.json();
  }
  
  async send(toAddress, body, options = {}) {
    const resolution = await this.resolve(toAddress);
    const deliveryUrl = resolution.receive.inbox_url;
    
    const envelope = {
      version: '0.02',
      id: crypto.randomUUID(), // Available in modern browsers
      from: this.address,
      to: toAddress,
      visibility: options.visibility || 'private',
      intent: options.intent || 'introduce',
      timestamp: new Date().toISOString(),
      body
    };
    
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (this.apiKey) {
      headers.Authorization = `Bearer ${this.apiKey}`;
    }
    
    const response = await fetch(deliveryUrl, {
      method: 'POST',
      headers,
      body: JSON.stringify(envelope)
    });
    
    if (response.status === 201) {
      return await response.json();
    } else {
      throw new Error(`Delivery failed: ${response.status}`);
    }
  }
}

// Usage in browser
if (typeof window !== 'undefined') {
  window.AapClient = BrowserAapClient;
  window.AapAddress = AapAddress;
}
```

## 🧪 Testing

### Jest Tests

```javascript
// aap-address.test.js
const { AapAddress } = require('./aap-address');

describe('AapAddress', () => {
  test('valid address parsing', () => {
    const address = new AapAddress('ai:alice~social#example.com');
    expect(address.owner).toBe('alice');
    expect(address.role).toBe('social');
    expect(address.provider).toBe('example.com');
  });
  
  test('invalid address throws error', () => {
    expect(() => new AapAddress('invalid')).toThrow();
  });
  
  test('isValid method', () => {
    expect(AapAddress.isValid('ai:bob~main#test.org')).toBe(true);
    expect(AapAddress.isValid('invalid')).toBe(false);
  });
  
  test('address creation', () => {
    const address = AapAddress.create('charlie', 'support', 'help.com');
    expect(address.toString()).toBe('ai:charlie~support#help.com');
  });
});
```

## 📚 Advanced Examples

### WebSocket Integration

```javascript
// websocket-client.js
class AapWebSocketClient {
  constructor(providerUrl, onMessage) {
    this.ws = new WebSocket(providerUrl);
    this.onMessage = onMessage;
    
    this.ws.onmessage = (event) => {
      const message = JSON.parse(event.data);
      this.onMessage(message);
    };
    
    this.ws.onopen = () => {
      console.log('AAP WebSocket connected');
    };
  }
  
  sendMessage(envelope) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(envelope));
      return true;
    }
    return false;
  }
  
  close() {
    this.ws.close();
  }
}

// Usage with real-time updates
const wsClient = new AapWebSocketClient(
  'wss://example.com/aap/ws',
  (message) => {
    console.log('New message:', message);
    // Update UI, notify user, etc.
  }
);
```

### Command Line Interface

```javascript
#!/usr/bin/env node
// cli.js
const { program } = require('commander');
const { AapClient } = require('./aap-client');

program
  .name('aap-cli')
  .description('AAP Command Line Interface')
  .version('1.0.0');

program
  .command('resolve <address>')
  .description('Resolve an AAP address')
  .action(async (address) => {
    try {
      const client = new AapClient('ai:cli~tool#example.com');
      const result = await client.resolve(address);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

program
  .command('send <to> <message>')
  .description('Send a message to an AAP address')
  .option('-k, --key <apiKey>', 'API key')
  .action(async (to, message, options) => {
    try {
      const client = new AapClient('ai:cli~tool#example.com', options.key);
      const result = await client.send(to, { text: message });
      console.log(`Message sent: ${result.message_id}`);
    } catch (error) {
      console.error('Error:', error.message);
      process.exit(1);
    }
  });

program.parse();
```

## 🔗 Resources

- [AAP Specification](../../spec/aap-v0.02.md)
- [Axios HTTP Client](https://axios-http.com/)
- [Full Example Code](https://github.com/thomaszta/aap-protocol/tree/main/examples/javascript)
=======
# AAP JavaScript / Node Examples

## Usage

- **Node**: run with `node` or add to your project; no build required for basic parsing.
- **Browser**: use the same regex/parse logic; resolve via `fetch` to the provider.

## Parse and validate an AAP address

AAP format: `ai:owner~role#provider`

```javascript
const AAP_PATTERN = /^ai:([^~#]+)~([^#]+)#(.+)$/i;

function parseAAP(address) {
  if (!address || !address.trim().toLowerCase().startsWith("ai:")) return null;
  const m = address.trim().match(AAP_PATTERN);
  if (!m) return null;
  const [, owner, role, provider] = m;
  return { owner, role, provider: provider.toLowerCase() };
}

function isValidAAP(address) {
  return parseAAP(address) !== null;
}

// Example
console.log(parseAAP("ai:tom~social#www.molten.it.com"));
// { owner: 'tom', role: 'social', provider: 'www.molten.it.com' }
```

## Resolve (fetch)

```javascript
async function resolveAAP(address) {
  const a = parseAAP(address);
  if (!a) return null;
  const url = `https://${a.provider}/api/v1/resolve?address=${encodeURIComponent(`ai:${a.owner}~${a.role}#${a.provider}`)}`;
  const res = await fetch(url);
  if (!res.ok) return null;
  return res.json();
}
```

## Spec

See [spec/aap-v0.02.md](https://github.com/thomaszta/aap-protocol/blob/main/spec/aap-v0.02.md) for the full protocol.
>>>>>>> 6b67a4cffcf7cc30e01f8845ccca823dedef6025
