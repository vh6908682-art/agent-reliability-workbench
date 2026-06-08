# Ticket 031 — Final Repo Consistency and Demo Readiness Pass

## Goal

Do a final lightweight consistency pass so Agent Reliability Workbench feels clean, coherent, and demo-ready.

This ticket should fix documentation path inconsistencies, verify that public-facing docs point to the right files, and run the main validation commands.

This is not a feature ticket.

---

## Context

Recent tickets added:

- polished README and demo story
- backend smoke tests
- sample benchmark output JSON files
- eval comparison/config metadata coverage

There may now be multiple demo script paths, including:

- docs/DEMO_SCRIPT.md
- docs/architecture/demo-script.md

The repo should have one clear public-facing demo script path, and README links should point to the correct file.

---

## Files likely involved

- README.md
- docs/DEMO_SCRIPT.md
- docs/architecture/demo-script.md
- docs/ROADMAP.md
- docs/PROJECT_VISION.md
- docs/examples/*.json
- docs/tickets/

Only edit docs unless a small test/validation issue reveals an obvious typo.

---

## Required work

### 1. Normalize demo script location

Inspect both possible demo script files:

- docs/DEMO_SCRIPT.md
- docs/architecture/demo-script.md

Choose one canonical public-facing demo script.

Preferred canonical path:

text docs/DEMO_SCRIPT.md 

Then either:

- move/merge useful content into docs/DEMO_SCRIPT.md, or
- update README to point to the existing canonical file if the repo already strongly uses another convention.

Avoid duplicate/conflicting demo scripts.

If keeping both, make one clearly point to the other and explain why.

---

### 2. Check README links

Verify README links work for:

- demo script
- project vision
- roadmap
- sample agent run
- sample trace
- sample eval run
- sample eval comparison

Fix broken or inconsistent paths.

---

### 3. Check naming consistency

Use one project name consistently in public docs.

Preferred name:

text Agent Reliability Workbench 

Avoid mixing too many names like:

- AgentOps Workbench
- agentsOps
- Agent Reliability Workbench

It is okay to mention prior/internal naming only if needed, but public docs should use the preferred name.

---

### 4. Check roadmap honesty

Ensure roadmap items are clearly future-facing.

Future items should not sound implemented:

- LangGraph/workflow orchestration
- hosted demo
- real production integrations
- exportable reports
- richer benchmark suites
- advanced scoring rubrics

---

### 5. Validate sample JSON files

Run JSON validation for:

text docs/examples/sample-agent-run.json docs/examples/sample-trace.json docs/examples/sample-eval-run.json docs/examples/sample-eval-comparison.json 

---

### 6. Run main validation suite

Run:

bash cd apps/api && python -m pytest 

Also run frontend typecheck if frontend was not recently validated:

bash cd apps/web && npm run typecheck 

If frontend typecheck fails because of pre-existing issues unrelated to this ticket, report clearly and do not perform a large refactor.

---

## Acceptance criteria

- README has no obvious broken internal doc links.
- There is one clear canonical demo script.
- Public-facing docs consistently use Agent Reliability Workbench.
- Future features are clearly marked as roadmap/future.
- All sample JSON files are valid JSON.
- Backend tests pass.
- Frontend typecheck passes, or any unrelated failure is clearly reported.
- No app feature behavior is changed.
- No new dependencies are added.

---

## Validation commands

bash python -m json.tool docs/examples/sample-agent-run.json python -m json.tool docs/examples/sample-trace.json python -m json.tool docs/examples/sample-eval-run.json python -m json.tool docs/examples/sample-eval-comparison.json cd apps/api && python -m pytest cd ../web && npm run typecheck git diff --check git status --short 

---

## Guardrails for Codex

- This is a cleanup and validation ticket.
- Do not add new features.
- Do not refactor backend or frontend code.
- Do not introduce a new docs structure.
- Prefer small, surgical edits.
- Keep public docs strong but honest.
- If two docs conflict, merge the useful content and remove/redirect duplication.
- Report any untracked ticket files in the final summary.