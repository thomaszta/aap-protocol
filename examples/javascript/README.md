# AAP JavaScript / Node Examples

## Installation

### Node.js
```bash
npm install axios uuid
# or
yarn add axios uuid
```

### Browser
```html
<script src="https://unpkg.com/axios/dist/axios.min.js"></script>
```

## Quick Start

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

## Send a Message

```javascript
const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

async function sendAAPMessage(fromAddress, toAddress, body, apiKey = null) {
  const resolution = await resolveAAP(toAddress);
  const deliveryUrl = resolution.receive.inbox_url;
  
  const envelope = {
    version: '0.02',
    id: uuidv4(),
    from: fromAddress,
    to: toAddress,
    visibility: 'private',
    intent: 'introduce',
    timestamp: new Date().toISOString(),
    body
  };
  
  const headers = {
    'Content-Type': 'application/json'
  };
  
  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }
  
  const response = await axios.post(deliveryUrl, envelope, { headers });
  
  if (response.status === 201) {
    return response.data;
  } else {
    throw new Error(`Delivery failed: ${response.status}`);
  }
}
```

## Spec

See [spec/aap-v0.02.md](https://github.com/thomaszta/aap-protocol/blob/main/spec/aap-v0.02.md) for the full protocol.
