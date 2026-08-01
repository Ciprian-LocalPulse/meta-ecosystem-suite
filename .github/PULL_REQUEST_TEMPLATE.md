## Summary

What does this PR do, and why?

## Which module(s) does this touch?

- [ ] DSA Auditor (`dsa_auditor/`)
- [ ] Metrics Migrator (`metrics_migrator/`)
- [ ] Ad Policy Linter (`policy_linter/`)
- [ ] Status Sentinel (`status_sentinel/`)
- [ ] CLI (`cli.py`)
- [ ] Shared HTTP/retry layer (`http.py`)
- [ ] Packaging / dependencies / CI
- [ ] Docs only

## Extra scrutiny checklist

Check any that apply — these areas get closer review because they
touch credentials, live network calls, or shared data definitions:

- [ ] Touches credential handling (`config.py`, `.env`, tokens, webhook URLs)
- [ ] Adds or changes a call to a Meta API endpoint
- [ ] Changes `rules.py` or `mappings.py` (data the linter/migrator depend on)
- [ ] Changes retry/backoff or rate-limit behavior in `http.py`

## How was this tested?

- [ ] Added/updated tests (network calls mocked with `respx` — see `tests/conftest.py`)
- [ ] Ran `pytest --cov=meta_ecosystem_suite --cov-report=term-missing` and coverage didn't regress
- [ ] Ran `ruff check .` and `mypy meta_ecosystem_suite` locally
- [ ] Manually tested against a live Meta API sandbox (only if relevant — describe below)

## Checklist

- [ ] `CHANGELOG.md` updated under `## [Unreleased]` (for user-facing changes)
- [ ] No secrets, tokens, or real ad data included in code, tests, or fixtures
- [ ] Docs (`README.md` / `docs/`) updated if behavior or config changed

## Related issues

Closes #
