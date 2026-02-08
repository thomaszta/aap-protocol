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
