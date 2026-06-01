# SECURITY.md — FlowSync SaaS Metrics Agent

## Security Policy

### Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x (current) | ✅ Active security support |
| 0.x (pre-release) | ❌ No security support |

---

## Reporting a Vulnerability

**Do NOT open a public GitHub Issue for security vulnerabilities.**

### Preferred Channels (in order of preference)

1. **GitHub Security Advisory**: Navigate to the repo → Security → Advisories → New draft advisory
2. **Email**: security@flowsync.example.com *(placeholder — update with real address before production)*

### What to Include
- Description of the vulnerability
- Steps to reproduce (detailed)
- Potential impact and affected versions
- Any proof-of-concept code (mark as sensitive)
- Your preferred contact for follow-up

### Response SLA
| Severity | Acknowledgment | Patch Target |
|----------|---------------|-------------|
| Critical | 24 hours | 72 hours |
| High | 48 hours | 7 days |
| Medium | 5 days | 30 days |
| Low | 10 days | Next release |

We will confirm receipt, assess severity, and keep you updated through resolution. We credit researchers in our release notes unless they prefer anonymity.

---

## Security Architecture

### Data Handling
- **All data is synthetic**: No real user data, PII, or financial data is stored in this repository.
- `data/synthetic_data.json` contains procedurally generated fictional metrics only.
- The dashboard is a static HTML file — no form submissions, no cookies, no localStorage.

### No Attack Surface (Current Scope)
Since v1.0 is a local dashboard with synthetic data, the current attack surface is minimal:
- No server, no authentication, no session tokens
- No user input beyond tab/filter clicks (all sanitized by Chart.js)
- No external API calls from the dashboard (all data is inline)
- Agent runs locally; no network exposure

### Future Production Considerations
If this project is extended to a live SaaS dashboard, the following controls MUST be implemented before deployment:

#### Authentication & Authorization
- [ ] Implement OAuth 2.0 / OIDC (not basic auth)
- [ ] Role-based access control (read-only analyst vs. admin)
- [ ] MFA required for all admin accounts
- [ ] Session tokens: HTTP-only, Secure, SameSite=Strict cookies
- [ ] Token expiry ≤ 8 hours; refresh token rotation

#### Data Security
- [ ] Encrypt all PII at rest (AES-256)
- [ ] Encrypt data in transit (TLS 1.3 minimum)
- [ ] Never log PII or tokens
- [ ] Implement data retention policies
- [ ] GDPR/CCPA compliance review before launch

#### API Security (if added)
- [ ] Rate limiting on all endpoints
- [ ] Input validation and schema enforcement (Pydantic)
- [ ] Parameterized queries (no raw SQL string building)
- [ ] CORS policy restricted to known origins
- [ ] Security headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options

#### Infrastructure
- [ ] Dependency scanning (Dependabot or Snyk)
- [ ] SAST scanning in CI (Bandit for Python, ESLint security plugin)
- [ ] Container scanning if Dockerized
- [ ] Secrets never committed to git (use `.gitignore` + pre-commit hooks)
- [ ] Principle of least privilege for all service accounts

---

## Dependency Security

### Python Dependencies
Scan with:
```bash
pip install safety
safety check -r requirements.txt
```

### JavaScript Dependencies
The dashboard uses Chart.js via CDN. In a production deployment:
- Pin the CDN version (do not use `@latest`)
- Use Subresource Integrity (SRI) hashes:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"
        integrity="sha384-[hash]"
        crossorigin="anonymous"></script>
```

---

## Secrets Management

### Current State (v1.0)
- No secrets in this repository
- No `.env` files committed
- No API keys, tokens, or credentials

### Policy
- All secrets MUST be stored in environment variables or a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault)
- `.env` files are in `.gitignore` — never commit them
- Pre-commit hook enforces no secret patterns:
```bash
# .git/hooks/pre-commit (install with: cp .githooks/pre-commit .git/hooks/)
grep -rn "AKIA\|sk-\|password\s*=" --include="*.py" --include="*.js" --include="*.json" . \
    && echo "Possible secret detected — aborting commit" && exit 1 || exit 0
```

---

## Secure Coding Standards

### Python
- No use of `eval()` or `exec()` with external input
- No `pickle` for deserialization of untrusted data (use `json`)
- Validate all external inputs before processing
- Use `subprocess` with `shell=False` and explicit arg lists

### JavaScript
- No `innerHTML` assignment with user-controlled data (use `textContent`)
- No `eval()` or `Function()` constructors with dynamic strings
- All chart data flows through Chart.js APIs (never injected as raw HTML)

---

## Audit & Compliance

See [AUDIT.md](AUDIT.md) for the full audit log and compliance posture.

---

## Security Contacts

| Role | Contact |
|------|---------|
| Security Lead | security@flowsync.example.com |
| Engineering Lead | eng-lead@flowsync.example.com |
| Data Protection Officer | dpo@flowsync.example.com *(required if handling real PII)* |

---

*Last updated: 2026-06-01 | Review cycle: Quarterly*
