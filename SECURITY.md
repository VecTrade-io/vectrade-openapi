# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in the VecTrade API specification, please report it responsibly.

**Do not open a public issue.**

Instead, email **security@vectrade.io** with:

- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We will acknowledge your report within 48 hours and provide a timeline for resolution.

## Scope

This repository contains API specifications only (no runtime code). Security concerns here include:

- Specification design flaws that could lead to insecure API implementations
- Missing security requirements (authentication, authorization, rate limiting)
- Sensitive data exposure in schema definitions
- Injection vectors in parameter definitions

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 1.0.x   | ✅        |
