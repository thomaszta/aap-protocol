# Contributing to AAP

Thank you for your interest in contributing to the Agent Address Protocol (AAP)! We welcome contributions from everyone.

## Quick Links

- [Bug Reports](.github/ISSUE_TEMPLATE/bug-report.md)
- [Feature Requests](.github/ISSUE_TEMPLATE/feature-request.md)
- [Protocol Proposals](.github/ISSUE_TEMPLATE/protocol-proposal.md)
- [GitHub Discussions](https://github.com/thomaszta/aap-protocol/discussions)

## How to Contribute

### Reporting Bugs

1. Check if the bug already exists in [Issues](https://github.com/thomaszta/aap-protocol/issues)
2. Use the [Bug Report template](.github/ISSUE_TEMPLATE/bug-report.md)
3. Include:
   - AAP version (e.g., 0.03)
   - Steps to reproduce
   - Expected vs actual behavior

### Suggesting Enhancements

1. Use the [Feature Request template](.github/ISSUE_TEMPLATE/feature-request.md)
2. Describe:
   - The problem you're solving
   - Proposed solution
   - Alternatives considered
   - Impact on existing implementations

### Protocol Proposals

For changes to the AAP specification:

1. **Discuss first** in [GitHub Discussions](https://github.com/thomaszta/aap-protocol/discussions)
2. Use the [Protocol Proposal template](.github/ISSUE_TEMPLATE/protocol-proposal.md)
3. Consider:
   - Backward compatibility
   - Impact on existing adopters
   - Implementation complexity

### Improving Documentation

We welcome improvements to:
- Protocol specification clarity
- Implementation guides
- Code examples
- FAQ entries

## Development Workflow

### 1. Find an Issue

- Look for issues labeled `good first issue` or `help wanted`
- Comment on the issue to let others know you're working on it

### 2. Create a Branch

```bash
git checkout -b type/description
# Examples:
# git checkout -b docs/fix-typos
# git checkout -b spec/add-example
# git checkout -b adopters/add-new-platform
```

### 3. Make Your Changes

- Follow the Style Guide below
- Update documentation if needed

### 4. Commit Your Changes

```bash
git add .
git commit -m "type: description"
# Examples:
# git commit -m "docs: fix typos in provider guide"
# git commit -m "spec: add address validation example"
```

### 5. Push and Create PR

```bash
git push origin your-branch-name
```

Then create a Pull Request using the [PR template](.github/PULL_REQUEST_TEMPLATE.md).

## Style Guide

### Markdown Files

- Use proper heading hierarchy
- Keep lines under 100 characters
- Use tables for structured data
- Include code examples where helpful

### Specification Changes

- Be clear and unambiguous
- Include examples
- Consider edge cases
- Maintain backward compatibility
- Document migration path

### Commit Messages

Use conventional commit format:

```
type: description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature (for spec)
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Formatting
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

### Code Examples

- See [examples/](examples/) for Python and JavaScript samples
- New examples are welcome

## Pull Request Process

1. Fork the repo
2. Create a branch (`git checkout -b feature/your-change`)
3. Make your changes
4. Ensure any new spec text is clear and backward-compatible
5. Submit a PR with a concise description
6. CI will run (markdown and structure checks); address any failures
7. Address review feedback

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## Security

See [SECURITY.md](.github/SECURITY.md) for how to report vulnerabilities.

---

Thank you for contributing to AAP!
