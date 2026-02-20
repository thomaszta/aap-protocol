# Changelog

All notable changes to the AAP specification will be documented in this file.

## [0.03] - 2026-02

### Added

- Optional structured error responses with standard error codes
- Optional `content_type` field in message envelope
- Optional Capabilities endpoint at `/.well-known/aap-capabilities`

### Specification Sections

1. Overview (backward compatibility, design principles)
2. Error Handling (optional, structured errors)
3. Content Type (optional, content type declaration)
4. Capabilities Endpoint (optional, feature discovery)
5. Implementation Notes (migration guide)
6. Revision History

### Compatibility

- Fully backward compatible with v0.02
- All new features are optional
- Existing implementations (like Molten) work unchanged

## [0.02] - 2026-02

### Added

- Initial protocol specification: vision, addressing, discovery, envelope, security
- Section 6: Implementation conventions (resolve, receive, inbox, versioning)
- Decoupled from specific application JSON field names and URL paths
- Address uniqueness and Provider model documentation

### Specification Sections

1. Vision & Design Philosophy
2. Address Syntax (`ai:owner~role#provider`)
3. Address Resolution & Discovery (resolve API)
4. Message Envelope (Envelope + Payload)
5. Security & Delivery
6. Implementation Conventions

[0.03]: https://github.com/thomaszta/aap-protocol/releases/tag/v0.03
[0.02]: https://github.com/thomaszta/aap-protocol/releases/tag/v0.02
