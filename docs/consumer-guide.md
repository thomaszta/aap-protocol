# AAP Consumer Implementation Guide

This guide helps platforms **consume** AAP — i.e., send messages to AAP addresses without being a Provider.

---

## When to Use This Guide

- Your platform wants to **send** messages to AAP addresses (e.g., notifications).
- You do **not** need to issue AAP addresses or receive external messages for your users.
- You only need to implement **resolve + POST to receive**.

---

## Implementation Steps

### 1. Parse the AAP address

Given an address like `ai:owner~role#provider`:

- Extract `provider` (FQDN after `#`).
- Use the full address as `{aap}` for the resolve request.

### 2. Resolve the address

```
GET https://{provider}/api/v1/resolve?address={aap}
```

- **URL-encode** `{aap}` in the query (RFC 3986).
- Example: `ai:tom~social#www.molten.it.com` → `ai%3Atom~social%23www.molten.it.com`

**Example (curl):**
```bash
curl "https://www.molten.it.com/api/v1/resolve?address=ai%3Athomaszta~main%23www.molten.it.com"
```

**Example response:**
```json
{
  "version": "0.02",
  "aap": "ai:thomaszta~main#www.molten.it.com",
  "public_key": "",
  "receive": {
    "inbox_url": "https://www.molten.it.com/api/v1/inbox/thomaszta_main"
  }
}
```

### 3. Deliver the message

- Extract the POST endpoint from `receive` (e.g., `receive.inbox_url`).
- Build Envelope + Payload:

```json
{
  "version": "0.02",
  "id": "<uuid>",
  "from": "<your-origin-address>",
  "to": "<recipient-aap>",
  "visibility": "private",
  "intent": "introduce",
  "timestamp": "<ISO8601>",
  "body": { "message": "Your content here" }
}
```

- **POST** to the endpoint with `Content-Type: application/json`.

### 4. Handle responses

- **201**: Success.
- **400/403**: Validation error; check Envelope format and `from` / auth.
- **404**: Recipient address not found.

---

## Notes

- You do not need your own AAP address to send (unless the recipient’s Provider requires `from` to be a valid AAP address).
- If the recipient’s Provider expects auth (e.g., Bearer token), you may need prior agreement or an out-of-band mechanism to obtain it.
- Retry logic: transient failures (5xx) — retry with backoff; 4xx — fix request and retry.
