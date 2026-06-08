# Codex Workflow

Codex CLI should be used as the implementation engineer, not the architect.

The architecture, product scope, and tickets should be written by us first. Codex should then implement small, testable slices.

## Rules

- Do not ask Codex to build the whole project in one prompt.
- Do not ask Codex to rewrite many files at once unless the ticket requires it.
- Keep every ticket small.
- Ask for a plan before code changes when the task touches multiple files.
- Review diffs before accepting.
- Run tests or smoke checks after each ticket.
- Commit after each clean working slice.

## Preferred ticket format

Each ticket should include:

- Goal
- Context
- Files likely involved
- Acceptance criteria
- Commands to run
- Out of scope

## Good Codex prompt shape

Use prompts like:

Implement Ticket 001 only.

Read:
- AGENTS.md
- README.md
- docs/product/mvp-scope.md
- docs/architecture/system-overview.md
- docs/architecture/api-contract.md

Goal:
Create a minimal FastAPI app with a health endpoint.

Acceptance criteria:
- GET /api/health returns status and service.
- App starts locally.
- Keep changes small.
- Do not implement unrelated endpoints.

After changes:
- Show changed files.
- Show commands to run.
- Do not continue to the next ticket.

## Bad Codex prompt shape

Avoid prompts like:

- Build the whole Agent Reliability Workbench.
- Create backend, frontend, database, evals, and UI.
- Make it production ready.
- Add everything from the docs.

These prompts are too broad and increase the chance of incorrect code.

## Working loop

1. Pick one ticket.
2. Paste ticket into Codex.
3. Let Codex inspect the repo.
4. Ask Codex for a short implementation plan if needed.
5. Approve the plan.
6. Let Codex edit files.
7. Run the listed commands.
8. Fix errors within the same ticket.
9. Commit the working slice.
10. Move to the next ticket.

## Suggested commit style

Use small commits:

- docs: add architecture command center
- chore: add docker compose postgres
- feat(api): add health endpoint
- feat(api): add run model
- feat(web): add runs page
- feat(eval): add eval case runner

## When to stop Codex

Stop and re-center if Codex:

- creates unrelated files
- changes architecture without asking
- skips acceptance criteria
- removes existing docs
- adds unnecessary frameworks
- writes placeholder code without saying so
- implements multiple future tickets at once

## Principle

The repo should grow like a real production project: one reviewed, working slice at a time.
