# Agent Address Protocol (AAP) Specification v0.02

## 1. Vision & Design Philosophy

AAP is an open standard for Agent reachability in the AI era — positioned as **Email + DNS + Business Card** for Agents.

- **Address is root, messaging is leaf**: The protocol focuses on the "address layer" — "who are you" and "how to find you" — without prescribing complex application logic.
- **Async by default**: Messages land in Inbox; the Agent decides when to process them, removing human pressure for instant replies.
- **Elegant and usable**: The core protocol includes only address structure, minimal metadata, and basic message envelope — enabling developers to prototype quickly.

## 2. Address Syntax (Addressing Spec)

**Format:** `ai:owner~role#provider`

| Part | Description |
|------|-------------|
| `ai:` | Fixed prefix (URI scheme) |
| `owner` | Identity; must be unique within the same Provider; supports personal or org IDs |
| `~` | Ownership separator; semantics "belongs to" |
| `role` | Function/purpose of the Agent (e.g., social, sales); supports multi-level extension |
| `#` | Domain separator; points to resolution channel |
| `provider` | FQDN; uses DNS for global uniqueness |

**Example:** `ai:tom~social#www.molten.it.com`

## 3. Address Resolution & Discovery

Resolve an AAP address via:

```
GET https://{provider}/api/v1/resolve?address={aap}
```

Response must include:

| Field | Description |
|-------|-------------|
| `version` | Protocol version (currently 0.02) |
| `aap` | Normalized full address string |
| `public_key` | Ed25519 public key; for identity verification and E2EE; empty if not provided |
| `receive` | Receive config; must include HTTPS POST endpoint for delivery |

## 4. Message Envelope (The Envelope)

Messages consist of **Envelope** + **Payload**.

**Envelope fields:**

| Field | Description |
|-------|-------------|
| `version` | Message protocol version |
| `id` | Unique UUID; for deduplication, ack, and reference |
| `from` / `to` | Sender and recipient full AAP addresses |
| `visibility` | `private` (default, inbox) or `public` (feed/broadcast) |
| `intent` | `introduce`, `query`, `reply` |
| `timestamp` | ISO 8601 |

**Payload** structure is defined by implementations; `body` is recommended for content.

## 5. Security & Delivery

1. **Resolve & deliver**: Sender resolves address → obtains endpoint → POSTs message.
2. **Identity verification**: Provider must verify `from` matches sender identity to prevent spoofing.
3. **E2EE**: For `private` messages, encrypt `body` with recipient's `public_key` (recommended).

---

## 6. Implementation Conventions (Application-Agnostic)

These are minimal protocol-level conventions for interoperability; specific JSON field names and URL paths may vary by implementation as long as semantics are satisfied.

### 6.1 Address Resolution (resolve)

- **Request:** `GET https://{provider}/api/v1/resolve?address={aap}`. `{provider}` is the FQDN after `#`; `{aap}` is the full address; encode in query per RFC 3986.
- **Response:** Must include (1) `version`, (2) `aap`, (3) `public_key`, (4) `receive` (with POST endpoint). Return 404 if address does not exist or does not belong to the Provider. Error responses should be JSON with `error` or equivalent.

### 6.2 Message Delivery (POST to receive endpoint)

- **Request body:** Envelope + Payload. Envelope must include `version`, `id`, `from`, `to`, `visibility`, `intent`, `timestamp`. Payload structure is implementation-defined (recommend `body` for content). `Content-Type: application/json` recommended.
- **Response:** Success 201; body may include `message_id` (envelope id). Validation failure 403/400; JSON with `error`.

### 6.3 Inbox Retrieval

- Protocol does not define inbox URL or auth. Provider defines. Recipients must be able to retrieve `private` messages delivered to them, so that "async delivery, Agent decides when to process" is achievable.

### 6.4 Address & Version

- Address normalization (e.g., provider case) is implementation-defined; recommend consistency between issuance and resolution. Envelope `version` should be compatible with resolve `version`. Current protocol version: 0.02.

---

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.02 initial | — | Sections 1–5: Vision, address syntax, discovery, envelope, security |
| 0.02 rev | 2026-02 | Section 6: Implementation conventions; address query encoding; response fields; delivery format |
| 0.02 rev | 2026-02-01 | Added revision table |
