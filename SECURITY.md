# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in AILang, please report it privately
by opening a security advisory on GitHub:

<https://github.com/akpersonal4/ailang-lang-AILang/security/advisories/new>

Do **not** report security vulnerabilities through public GitHub issues,
discussions, or pull requests.

## What to Include

- A description of the vulnerability
- Steps to reproduce it
- Affected versions (if known)
- Any potential mitigations

## Response Timeline

- **Acknowledgement**: Within 48 hours
- **Initial assessment**: Within 1 week
- **Fix release**: Within 30 days for critical issues

## Scope

The following are in scope:
- The AILang compiler and runtime (`compiler/`)
- The standard library (`stdlib/`)
- Official tooling (`ail` CLI, formatter)

The following are out of scope:
- Third-party extensions
- User-written AILang programs
- VS Code extension (report separately)
