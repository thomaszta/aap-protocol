# AAP Code Examples

This directory contains runnable examples for working with the Agent Address Protocol (AAP).

## Contents

| Language   | Description                    | Entry |
|-----------|---------------------------------|-------|
| **Python**  | Parse, validate, and format AAP addresses; optional resolve | [python/README.md](python/README.md) |
| **JavaScript** | Parse and validate AAP addresses in Node or browser | [javascript/README.md](javascript/README.md) |

## Quick usage

- **Resolve an address** (any language): `GET https://{provider}/api/v1/resolve?address={aap}` (encode `address` per RFC 3986).
- **Send a message**: POST Envelope + Payload to the `receive` endpoint returned by resolve. See [spec/aap-v0.03.md](../spec/aap-v0.03.md).

## Adding examples

We welcome examples in other languages (Go, Rust, etc.) or for specific flows (e.g., resolve + POST in one script). Add a subfolder and a README that explains how to run and what the example does.

## Resources

- [AAP Specification](../spec/aap-v0.03.md)
- [Provider Guide](../docs/provider-guide.md)
- [Consumer Guide](../docs/consumer-guide.md)
- [FAQ](../docs/faq.md)
