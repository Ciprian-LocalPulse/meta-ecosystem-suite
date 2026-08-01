# Contributing to MetaEcosystemSuite

Thanks for your interest in this project. Note that MetaEcosystemSuite
is distributed under a [proprietary license](LICENSE) — external
contributions are accepted at the maintainer's discretion, and by
submitting a pull request you agree that your contribution may be
incorporated into the Software under that same license.

## Before you start

- For anything beyond a trivial fix (typo, small bug), please open an
  issue first describing what you'd like to change and why. This
  avoids wasted effort on a PR that doesn't fit the project's
  direction.
- Security issues should **never** go through a public issue or PR —
  see [SECURITY.md](SECURITY.md).

## Development setup

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency
management and a committed `uv.lock` for reproducible installs.

```bash
git clone https://github.com/Ciprian-LocalPulse/meta-ecosystem-suite.git
cd meta-ecosystem-suite
uv venv
source .venv/bin/activate   # .venv\Scripts\activate on Windows
uv pip install -e ".[dev]"
cp .env.example .env         # fill in test credentials if you need live API access
```

Install the pre-commit hooks so lint/format/type checks run locally
before you push, not just in CI:

```bash
pre-commit install
```

## Running the test suite

```bash
pytest
```

All tests are fully offline: network calls to Meta's APIs are mocked
with [`respx`](https://lundberg.github.io/respx/), and
`tests/conftest.py` enforces this automatically — any un-mocked
request raises rather than silently hitting the network. If you add
a new function that calls out to `graph.facebook.com` or similar,
add a respx-mocked test alongside it rather than relying on a real
credential.

```bash
pytest --cov=meta_ecosystem_suite --cov-report=term-missing
```

## Code style & checks

Everything below runs in CI and also locally via pre-commit:

```bash
ruff check .          # linting
ruff format .         # formatting
mypy meta_ecosystem_suite
bandit -r meta_ecosystem_suite
pip-audit
```

Please don't submit a PR with `mypy` or `ruff` errors — CI will block
merge, and asking a reviewer to look past known lint failures wastes
their time.

## Commit / PR conventions

- Keep commits focused; one logical change per commit where
  reasonable.
- Write commit messages in the imperative mood ("Add retry logic to
  graph_client", not "Added" or "Adding").
- Update `CHANGELOG.md` under an `## [Unreleased]` heading for any
  user-facing change.
- Fill out the PR template — in particular, note whether your change
  touches credential handling, network calls, or the rules/mappings
  data files, since those get extra review scrutiny.
- Add or update tests for any behavior change. New network-facing
  code needs a respx-mocked test, not just a happy-path unit test.

## Adding a new rule / mapping

`policy_linter/rules.py` and `metrics_migrator/mappings.py` are
intentionally data, not code — if you're adding a new Ad Policy rule
or a new legacy/unified metric mapping, you almost certainly want to
add an entry there rather than branching in `linter.py` or
`normalizer.py`. Add a corresponding test in `tests/` that exercises
the new entry.

## Questions

Open a GitHub issue, or email contact@localpulse.dev for anything
you'd rather not discuss publicly.
