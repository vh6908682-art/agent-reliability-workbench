# Ticket 018 — CI / Quality Gates

## Goal

Add basic CI checks so AgentOps Workbench has a reliable quality gate before changes are merged.

This makes the project feel like a real production-grade engineering platform instead of a local-only demo.

## Why this matters

A production agent platform should have confidence checks for:

- Backend formatting
- Backend linting
- Backend tests
- Frontend formatting
- Frontend linting
- Frontend build
- Basic repository health

This ticket creates the first version of that quality gate.

## Scope

Add GitHub Actions workflow files for backend and frontend checks.

Keep the setup simple and aligned with the current monorepo structure.

## Suggested workflow location

    .github/workflows/ci.yml

## Backend CI requirements

Run backend checks such as:

    install Python dependencies
    run formatting check
    run linting
    run tests

Use the tools already chosen in earlier tickets.

If exact tools are not finalized yet, prefer simple defaults:

    ruff
    pytest

Do not add a complex test matrix.

## Frontend CI requirements

Run frontend checks such as:

    install Node dependencies
    run linting
    run build

Use the package manager already present in the project.

If the frontend package manager is not obvious, infer from existing lockfiles.

## Database dependency

If backend tests require Postgres, add a Postgres service to the GitHub Actions workflow.

Suggested defaults:

    POSTGRES_USER=agentops
    POSTGRES_PASSWORD=agentops
    POSTGRES_DB=agentops_workbench

If tests can run without Postgres, keep CI simpler and avoid the service.

## Makefile integration

Confirm that the Makefile has useful local commands, such as:

    make test
    make lint
    make format
    make ci

If needed, add or adjust a small number of Makefile targets.

The goal is for local checks and CI checks to be similar.

## Acceptance criteria

- GitHub Actions CI workflow exists.
- CI runs on pull requests.
- CI runs on pushes to main.
- Backend tests run in CI.
- Backend linting runs in CI.
- Frontend linting runs in CI.
- Frontend build runs in CI.
- CI uses simple environment variables from .env.example where appropriate.
- Local Makefile commands remain usable.
- No secrets are committed.

## Out of scope

- Deployment.
- Preview environments.
- Docker image publishing.
- Full security scanning.
- Code coverage gates.
- End-to-end browser tests.
- Multi-version test matrix.
- Release automation.

## Suggested Codex prompt

Implement Ticket 018 using the existing monorepo structure.

Add a simple GitHub Actions CI workflow that runs backend tests/linting and frontend linting/build on pull requests and pushes to main.

Use existing project commands where possible. If needed, add small Makefile targets so local quality checks match CI.

Keep the workflow simple. Do not add deployment, coverage gates, Docker publishing, or release automation.
