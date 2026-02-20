# Agent Address Protocol (AAP) Specification v0.03

## 1. Overview

v0.03 is a backward-compatible extension of v0.02. It adds optional features that improve developer experience without breaking existing implementations.

### Changes from v0.02

| Feature | Type | Description |
|---------|------|-------------|
| Error codes | Optional | Standardized error response format |
| content_type | Optional | Message content type declaration |
| Capabilities endpoint | Optional | Provider capabilities discovery |

### Design Principles

- **Backward compatible**: All changes are optional; v0.02 implementations continue to work
- **Opt-in**: Providers choose which features to support
- **Pragmatic**: Focus on real-world developer needs

---

## 2. Error Handling (Optional)

### Error Response Format

When returning errors, providers SHOULD use this structure:

```json
{
  "error": {
    "code": "address_not_found",
    "message": "The requested AAP address does not exist"
  }
}
```

### Standard Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `invalid_address` | 400 | Address format is invalid |
| `address_not_found` | 404 | Address not found on this Provider |
| `authentication_required` | 401 | Authentication required but not provided |
| `authentication_failed` | 403 | Authentication provided but invalid |
| `invalid_envelope` | 400 | Message envelope is malformed |
| `rate_limit_exceeded` | 429 | Too many requests |
| `internal_error` | 500 | Provider internal error |

### Backward Compatibility

- Providers MAY return structured errors OR legacy format
- Consumers MUST handle both formats gracefully

---

## 3. Content Type (Optional)

### Field Definition

The `content_type` field indicates the media type of the message body:

```json
{
  "version": "0.02",
  "id": "uuid",
  "from": "ai:sender~role#provider.com",
  "to": "ai:recipient~role#provider.com",
  "visibility": "private",
  "intent": "introduce",
  "timestamp": "2026-02-20T12:00:00Z",
  "content_type": "application/json",
  "body": { "message": "Hello" }
}
```

### Supported Types

| Type | Description |
|------|-------------|
| `application/json` | Default; JSON object |
| `text/plain` | Plain text |
| `text/markdown` | Markdown content |

### Backward Compatibility

- If `content_type` is missing, assume `application/json`
- Unknown types SHOULD be treated as `application/octet-stream`

---

## 4. Capabilities Endpoint (Optional)

### Endpoint

```
GET /.well-known/aap-capabilities
```

### Response

```json
{
  "protocol_version": "0.03",
  "features": {
    "structured_errors": true,
    "content_type": true
  }
}
```

### Feature Flags

| Feature | Description |
|---------|-------------|
| `structured_errors` | Provider returns structured error responses |
| `content_type` | Provider accepts content_type in envelopes |

### Backward Compatibility

- If endpoint returns 404, consumers SHOULD assume v0.02 compatibility
- Consumers MUST handle missing features gracefully

---

## 5. Implementation Notes

### For Providers

1. All v0.03 features are optional; implement at your own pace
2. Structured errors help debugging but are not required
3. Adding `content_type` support improves interoperability
4. Consider adding the Capabilities endpoint for better developer experience

### For Consumers

1. Always handle both structured and unstructured error responses
2. Include `content_type` when sending messages (defaults to JSON)
3. Check Capabilities endpoint if available, but don't require it
4. Fall back gracefully when features are unsupported

### Migration from v0.02

v0.03 is fully backward compatible:

```
v0.02 Provider ──► Works with v0.03 Consumer ──► ✓
v0.03 Provider ──► Works with v0.02 Consumer ──► ✓
```

---

## 6. Revision History

| Version | Date | Changes |
|---------|------|---------|
| 0.03 | 2026-02-20 | Added optional error codes, content_type, Capabilities endpoint |
| 0.02 | 2026-02 | Initial specification |
