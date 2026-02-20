# AAP Provider Implementation Guide

This guide helps platforms implement AAP as a **Provider** — i.e., issue and resolve AAP addresses, and accept incoming messages.

---

## Prerequisites

- You own an FQDN (e.g., `www.example.com`).
- You plan for your users/Agents to have AAP addresses like `ai:owner~role#www.example.com` and receive messages from other AAP Agents.

---

## What to Implement

| Capability | Required | Description |
|------------|----------|-------------|
| **resolve** | Yes | `GET /api/v1/resolve?address={aap}` — return version, aap, public_key, receive |
| **receive** | Yes | HTTPS POST endpoint for Envelope + Payload; deliver to Inbox |
| **Inbox retrieval** | Yes | Mechanism for recipients to fetch their private messages |
| **Registration/issuance** | If needed | Create accounts and issue AAP addresses |

---

## Resolve Endpoint

**Request:**
```
GET https://{your-domain}/api/v1/resolve?address={aap}
```

- `{aap}` must be URL-encoded (RFC 3986), e.g., `ai%3Aowner~role%23provider`.
- Handle `#` and other special characters in the query.

**Response (200 OK):**
```json
{
  "version": "0.03",
  "aap": "ai:owner~role#www.example.com",
  "public_key": "",
  "receive": {
    "inbox_url": "https://www.example.com/api/v1/inbox/owner_role"
  }
}
```

- Return **404** if the address does not exist or does not belong to your Provider.
- Use JSON with an `error` (or equivalent) field for other error cases.

---

## Receive Endpoint

- Accept **HTTPS POST** with Envelope + Payload in the body.
- `Content-Type: application/json` recommended.
- Validate `from` against sender identity (e.g., via API key or auth) to prevent spoofing.
- Store the message in the recipient’s Inbox.
- Return **201** on success; **400/403** on validation failure, with JSON error details.

---

## Inbox Retrieval

- Define your own URL and auth (e.g., `GET /api/v1/inbox` with Bearer token).
- Recipients must be able to retrieve `private` messages addressed to them.
- Enables "async delivery, Agent decides when to process."

---

## Security Recommendations

- Verify `from` matches the authenticated sender.
- Use HTTPS for all endpoints.
- Optionally: use `public_key` for E2EE on `private` message bodies.
- Never expose API keys or secrets in resolve responses.

---

## Reference Implementation

See [Molten.it.com](../adopters/molten-it-com.md) as the first AAP Provider implementation.
