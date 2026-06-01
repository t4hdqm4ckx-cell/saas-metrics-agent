# Pull Request

## Summary
<!-- 2-3 bullet points describing what this PR does -->
-
-

## Type of Change
- [ ] `feat` — new feature
- [ ] `fix` — bug fix
- [ ] `data` — data generation change (may change synthetic data output)
- [ ] `docs` — documentation only
- [ ] `chore` — build, config, dependencies
- [ ] `test` — new or updated tests
- [ ] `refactor` — no behavior change

## Related Issues
Closes #

## Testing
- [ ] Tests pass (`python3 agent/tests/test_data_generator.py`)
- [ ] Dashboard opens without console errors
- [ ] All 4 dashboard tabs render correctly
- [ ] Executive deck opens without errors

## Data Contract
- [ ] No schema changes, OR
- [ ] Schema changed → VERSION_CONTROL.md and docs/version_control.md updated
- [ ] synthetic_data.json regenerated (if data_generator.py changed)
- [ ] dashboard/assets/data/metrics.json updated to match

## Security Checklist
- [ ] No secrets committed
- [ ] No `eval()` or `innerHTML` with dynamic content added
- [ ] New dependencies documented in AUDIT.md
