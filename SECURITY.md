# Security Policy

Agent Reliability Workbench is a local-first MVP and research tool. It is not yet hardened for hostile multi-tenant use, untrusted users, or production exposure.

## Secrets

- Do not commit API keys, tokens, credentials, private URLs, or real production data.
- Use `.env.example` as the template for local configuration.
- Keep real `.env` files local and out of git.
- Rotate any secret that is accidentally exposed.

## External Agent Endpoints

External HTTP JSON agent endpoints should be local or trusted by default. Only point the workbench at remote or untrusted endpoints when you intentionally want to test that integration path and understand the data being sent.

## Reporting Vulnerabilities

Please report suspected vulnerabilities through GitHub issues or by contacting the repository owner. Include:

- A concise description of the issue.
- Steps to reproduce, if available.
- Expected impact.
- Any relevant logs or screenshots, with secrets removed.

Avoid posting real secrets, private customer data, or exploitable payloads in public reports.
