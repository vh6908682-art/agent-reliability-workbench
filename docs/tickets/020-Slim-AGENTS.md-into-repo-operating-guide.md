## Ticket 020 — Slim AGENTS.md into repo operating guide

Goal  
Refactor AGENTS.md into a short table of contents and operating guide that points to the new docs.

Files likely involved
- AGENTS.md
- Possibly README.md only if there is an obvious broken reference.

Acceptance criteria
- AGENTS.md is short and not bloated.
- Includes project identity.
- Includes backend/frontend/test commands.
- Includes docs map.
- Includes ticket discipline.
- Includes rule: do not implement unrelated changes.
- Includes rule: update docs only when behavior changes.
- Points deeper project context to docs/.

Validation commands
- git status
- No tests required if markdown-only.

Notes / guardrails for Codex
- Do not paste full project vision into AGENTS.md.
- Do not rewrite all docs.
- Do not change application code.
- Keep it useful for Codex, not marketing-heavy.



