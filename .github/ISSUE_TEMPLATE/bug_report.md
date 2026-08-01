---
name: Bug report
about: Something in MetaEcosystemSuite isn't working as expected
title: "[BUG] "
labels: bug
assignees: ""
---

**⚠️ If this is a security vulnerability, do not file it here.** See
[SECURITY.md](../../SECURITY.md) for the private reporting process.

## Describe the bug

A clear, concise description of what's wrong.

## Which module?

- [ ] DSA Auditor (`dsa_auditor/`)
- [ ] Metrics Migrator (`metrics_migrator/`)
- [ ] Ad Policy Linter (`policy_linter/`)
- [ ] Status Sentinel (`status_sentinel/`)
- [ ] CLI (`cli.py`)
- [ ] Other / not sure

## Steps to reproduce

1. Run '...'
2. With input '...'
3. See error

## Expected behavior

What you expected to happen instead.

## Actual behavior

What actually happened. Include the full traceback if there is one.

```
paste traceback here
```

## Environment

- MetaEcosystemSuite version / commit: 
- Python version: 
- OS: 
- Installed via: `uv` / `pip` / other

## Additional context

Anything else that might help — e.g. does this only happen against
live Meta API traffic, or does it reproduce with mocked responses too?

**Please make sure any pasted logs/output have real access tokens,
API keys, and webhook URLs redacted before submitting.**
