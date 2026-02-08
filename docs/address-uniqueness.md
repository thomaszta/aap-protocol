# AAP Address Uniqueness & Who Can Be a Provider

Based on the [aap-v0.02.md](../spec/aap-v0.02.md) specification.

---

## 1. How is AAP address uniqueness guaranteed?

The protocol ensures global uniqueness at **two layers**:

| Layer | Protocol | Meaning |
|-------|----------|---------|
| **Provider (#)** | Provider follows **FQDN**. Uses DNS for global uniqueness. | Whoever owns the domain owns the namespace. DNS ensures FQDNs are globally unique. |
| **Owner (# before)** | Owner must be unique **within the same Provider**. | Within one Provider, owner (and optional role) is assigned or constrained, ensuring domain-unique IDs. |

Thus:

- **Full AAP address** = `ai:owner~role#provider`
- **Globally unique** = (Provider via FQDN globally unique) × (Owner unique within Provider)

Similar to Email: `user@gmail.com` is unique because `gmail.com` is globally unique (DNS), and `user` is unique within Gmail.

---

## 2. Can any platform be a Provider?

**Yes.** The protocol does not define a "single official Provider" or centralized registry.

- The protocol only states: **provider is FQDN**, and resolve is `GET https://{provider}/api/v1/resolve?address={aap}`.
- Therefore: **any entity with an FQDN that implements resolve (and receive, etc.) can act as a Provider**, issuing and resolving AAP addresses for its domain.

Analogy:

- **Email**: No single global mail server; each org can run mail on its own domain (Provider).
- **AAP**: No single AAP authority; each platform/company can be an AAP Provider; the domain after `#` is under your control.

---

## 3. Won’t addresses collide? e.g., `ai:tom~social#xxx` on two platforms?

No, because **provider differs**:

- `ai:tom~social#www.molten.it.com` → Resolved by www.molten.it.com’s Provider; one identity.
- `ai:tom~social#other.com` → Resolved by other.com’s Provider; different identity.

These are different addresses, like `tom@gmail.com` vs `tom@yahoo.com`. Uniqueness is defined by **provider (FQDN)**; within the same FQDN, **owner (and role)** ensures domain-level uniqueness.

---

## 4. Summary

| Question | Answer |
|----------|--------|
| How is AAP address unique? | Provider (FQDN, DNS) + Owner unique within Provider → full address is globally unique. |
| Must one entity implement Provider? | No. Protocol does not require a single official Provider. |
| Can any platform be a Provider? | Yes. With an FQDN and a resolve (and receive) implementation, you can be a Provider. |

---

## 5. What must a platform implement to support AAP?

### Role A: Sending messages only

Platform **does not** need to be a Provider, but must **consume** AAP:

- **Resolve addresses**: `GET https://{provider}/api/v1/resolve?address={aap}` (address URL-encoded per RFC 3986).
- **Deliver to recipient**: Take endpoint from `receive` in the response; build Envelope + Payload; **HTTPS POST** to that endpoint.

Implementing **resolve + POST to receive** is enough to send messages; no need for resolve/receive on your side.

### Role B: Your Agents receive external messages (have AAP addresses)

Platform must act as an **AAP Provider** and implement at least:

- **resolve**: `GET https://{your-domain}/api/v1/resolve?address={aap}` returning `version`, `aap`, `public_key`, `receive`.
- **receive**: HTTPS POST endpoint accepting Envelope + Payload, delivering to the correct Inbox.
- **Inbox retrieval** (spec 6.3): URL and auth are Provider-defined; recipients must be able to retrieve `private` messages.

Only then can other platforms’ Agents resolve your addresses and POST messages to you.

### Summary

| Goal | AAP capabilities to implement |
|------|-------------------------------|
| Send to other AAP addresses | Resolve + POST to recipient’s receive endpoint |
| Receive messages (interop) | Provider: **resolve + receive + inbox retrieval** (details up to you) |

---

## 6. Must platforms implement AAP registration and issuance?

**Not necessarily.** Whether you implement registration and issuance depends on your **product goals**, not on "using AAP."

| Platform role | Need registration + issuance? | AAP capabilities needed |
|---------------|------------------------------|--------------------------|
| **Consume AAP only** (e.g., send notifications) | No | Resolve + POST to receive |
| **Your Agents have AAP addresses** and receive external messages | Yes | Provider: registration + issuance + resolve + receive + inbox retrieval |

**Conclusion:** Only platforms that need to give their users/Agents externally-addressable AAP addresses need to implement registration, issuance, and full Provider behavior.
