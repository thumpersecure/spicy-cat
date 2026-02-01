# Security Policy

## Scope

spicy-cat is an educational privacy tool. It generates fictional identities and simulates network traffic patterns. It is **not** a security tool and should not be relied upon for protection against determined adversaries.

## Known Limitations

### Identity Storage

- **With `cryptography` library**: Identities are encrypted using Fernet (AES-128-CBC with HMAC).
- **Without `cryptography` library**: Identities are stored with XOR obfuscation only. This provides no real security and is intended only to prevent casual inspection.

If you store sensitive data in identity files, install the cryptography library:

```bash
pip install cryptography
```

### Browser Fingerprinting

Firefox profiles created by spicy-cat enable `privacy.resistFingerprinting` and disable WebGL/WebRTC, but this does not defeat all fingerprinting techniques. For high-stakes anonymity, use [Tor Browser](https://www.torproject.org/) instead.

### Network Traffic Simulation

The traffic simulation features (`spicy-cat traffic` and `--malware` mode) make real network connections to external endpoints (httpstat.us, httpbin.org, badssl.com). These connections may:

- Appear in network logs
- Trigger IDS/IPS alerts (especially malware simulation mode)
- Be visible to network administrators

**Do not run traffic simulation on networks you do not control without authorization.**

## Reporting a Vulnerability

If you discover a security issue in spicy-cat:

1. **Do not** open a public GitHub issue for security vulnerabilities.
2. Email details to the repository maintainer (check GitHub profile for contact).
3. Include:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

You can expect an initial response within 7 days.

## Security Best Practices

When using spicy-cat:

1. Install `cryptography` for proper identity encryption
2. Do not mix real and fake identities
3. Do not access personal accounts while using a generated identity
4. Use Tor Browser or Tails OS for high-stakes anonymity
5. Run traffic simulation only in controlled environments
6. Review generated identity details before using them online

## Threat Model

spicy-cat is designed to:

- Reduce data broker collection effectiveness
- Provide training personas for OSINT exercises
- Generate test data for privacy research

spicy-cat is **not** designed to protect against:

- Law enforcement with legal authority
- Nation-state adversaries
- Advanced persistent threats
- Network-level surveillance (use VPN/Tor)
- Physical security threats
