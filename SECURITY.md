# Security Policy

MetaEcosystemSuite handles Meta Graph/Marketing API access tokens and
advertising data, so security issues here are treated as high priority.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1   | :x:                |

Until a 1.0 release, only the latest `main` branch and the most
recent tagged release receive security fixes.

## Reporting a Vulnerability

**Please do not open a public GitHub issue for security vulnerabilities.**

Instead, report it privately by emailing **contact@localpulse.dev**
with:

- A description of the vulnerability and its potential impact.
- Steps to reproduce (a minimal repro is enormously helpful).
- The affected version/commit.
- Any suggested mitigation, if you have one.

You should receive an acknowledgment within **3 business days**. We
aim to provide an initial assessment (severity + rough remediation
timeline) within **10 business days** of acknowledgment. We'll keep
you updated as a fix is developed and will credit you in the
[CHANGELOG](CHANGELOG.md) (unless you'd prefer to stay anonymous).

## Scope & Known Sensitive Areas

Given what this project does, the following are especially relevant
to flag:

- **Credential handling** — `META_ACCESS_TOKEN`, `META_APP_SECRET`,
  and `SLACK_WEBHOOK_URL` in `config.py` / `.env`. If you find a path
  where these could leak (logs, error messages, stack traces,
  exception payloads), that's a valid report.
- **The Ad Library extractor** (`dsa_auditor/extractor.py`) — sends
  `access_token` as a query parameter to `graph.facebook.com`, per
  Meta's API contract. This means the token can end up in access
  logs, proxy logs, or browser history if requests are replayed
  manually. Treat any additional exposure surface (e.g. token
  appearing in a written report, in `reports/*.json` output, or in
  retry/error logging) as in-scope.
- **Third-party dependencies** — run `pip-audit` locally
  (`pip-audit` is included in the `dev` extra) before reporting a
  dependency CVE that's already fixed upstream; otherwise, reports of
  vulnerable transitive dependencies are welcome.
- **Injection via ad copy** — the Ad Policy Linter (`policy_linter/`)
  processes third-party-supplied ad text. Reports of ways to make the
  linter mis-evaluate, crash, or leak internal state via crafted
  input are in scope.

## Out of Scope

- Vulnerabilities requiring a compromised Meta developer account or
  physical access to a machine with a valid `.env` file already
  present.
- Denial-of-service reports based purely on volume against a
  self-hosted instance (rate-limit configuration is the deployer's
  responsibility).

## Disclosure

This is proprietary software (see [LICENSE](LICENSE)); please
coordinate disclosure timing with us rather than publishing details
independently. We're happy to agree on a public writeup once a fix
has shipped.
