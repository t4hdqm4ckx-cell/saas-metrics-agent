# Contributing to FlowSync SaaS Metrics Agent

Thank you for your interest in contributing! This document covers how to set up the project, the development workflow, and contribution standards.

---

## Development Setup

```bash
git clone https://github.com/t4hdqm4ckx-cell/saas-metrics-agent.git
cd saas-metrics-agent

# Install Python dependencies (agent only)
pip install numpy>=1.24

# Regenerate data and validate
make data
make validate

# Run tests
make test

# Open dashboard
make dashboard
```

**No Node.js, no npm, no build step required.**

---

## Project Structure (Quick Reference)

```
agent/       — Python data generation and metrics computation
dashboard/   — Static HTML/CSS/JS dashboard
data/        — Generated JSON data files
docs/        — Executive deck, architecture, schema docs
skills/      — Agent capability definitions (Markdown)
logs/        — Agent run logs
```

---

## Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | Use |
|--------|-----|
| `feat:` | New feature, metric, or chart |
| `fix:` | Bug fix |
| `data:` | Data generation change (may alter synthetic data output) |
| `docs:` | Documentation only |
| `test:` | New or updated tests |
| `chore:` | Build, config, dependencies, maintenance |
| `refactor:` | Code restructure without behavior change |

Example: `feat(dashboard): add forecast overlay on MRR trend chart`

---

## Data Contract Rules

1. **Schema changes require version bump** in `VERSION_CONTROL.md` and `docs/version_control.md`
2. **Regenerate `synthetic_data.json`** if `data_generator.py` changes: `make data`
3. **Update inline JS arrays** in `dashboard/index.html` to match new JSON fields
4. **All tests must pass** after any change to the agent layer: `make test`

---

## Pull Request Process

1. Branch: `git checkout -b feat/your-feature-name`
2. Make changes, following conventions above
3. Run `make test` and ensure all pass
4. Open a PR using the PR template (`.github/pull_request_template.md`)
5. At least one review required before merge

---

## Reporting Bugs

See [BUG_REPORTING.md](BUG_REPORTING.md) for the full triage process.

For **security vulnerabilities**, see [SECURITY.md](SECURITY.md) — do NOT open a public issue.

---

## Code Standards

- **Python**: PEP 8, type hints on public functions, no `eval()` or `exec()`
- **JavaScript**: ES6+, no `eval()` or `innerHTML` with dynamic content
- **CSS**: Use CSS custom properties from `:root`, no inline styles in HTML
- **Tests**: Every bug fix must include a regression test

---

*This project is MIT licensed. See LICENSE.*
