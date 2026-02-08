# Security Policy

## Supported Versions

<<<<<<< HEAD
=======
We release patches for the current major specification version. Security-related clarifications are documented in the spec and changelog.

>>>>>>> 6b67a4cffcf7cc30e01f8845ccca823dedef6025
| Version | Supported          |
| ------- | ------------------ |
| 0.02.x  | :white_check_mark: |
| < 0.02  | :x:                |

## Reporting a Vulnerability

<<<<<<< HEAD
**Please do NOT report security vulnerabilities through public GitHub issues.**

If you believe you have found a security vulnerability in AAP protocol or its implementations, please report it to us privately:

**Email**: security@thomaszta.com (or use GitHub's private vulnerability reporting if enabled)

### What to include in your report

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)
- Your contact information

### Response timeline

- **Initial response**: Within 48 hours
- **Assessment**: Within 7 days
- **Fix development**: Depends on severity
- **Public disclosure**: Coordinated with reporter

## Security Considerations for AAP Implementations

### Provider Security
1. **Validate `from` addresses** to prevent spoofing
2. **Use HTTPS** for all endpoints
3. **Implement rate limiting** to prevent abuse
4. **Secure API key storage** and rotation

### Message Security
1. **Consider E2EE** for private messages using recipient's `public_key`
2. **Validate message integrity** (signatures if implemented)
3. **Sanitize message content** to prevent injection attacks

### Address Security
1. **Prevent address squatting** with appropriate registration policies
2. **Implement address verification** mechanisms
3. **Monitor for malicious addresses**

## Best Practices

### For Providers
- Regularly audit your AAP implementation
- Keep dependencies updated
- Implement logging and monitoring
- Have a security incident response plan

### For Consumers
- Verify resolved addresses before sending messages
- Implement retry logic with exponential backoff
- Validate message responses
- Keep your implementation updated

## Acknowledgments

We thank all security researchers who responsibly disclose vulnerabilities in AAP implementations.
=======
If you believe you have found a security issue in the **protocol specification** or in **documentation** that could lead to misuse (e.g., spoofing, privacy leaks), please report it responsibly:

1. **Do not** open a public GitHub issue for security-sensitive findings.
2. Open a **private security advisory**: [GitHub Security Advisories](https://github.com/thomaszta/aap-protocol/security/advisories/new).
3. Or email the maintainers if you prefer (see repository profile).

We will acknowledge your report and work on a fix or clarification. For protocol-level issues we may publish an errata or patch version and credit you (unless you prefer to remain anonymous).

Thank you for helping keep AAP and its implementations safe.
>>>>>>> 6b67a4cffcf7cc30e01f8845ccca823dedef6025
