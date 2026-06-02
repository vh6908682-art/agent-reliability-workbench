## Ticket 019 — Add docs structure and system-of-record docs

Goal  
Create focused project docs under docs/ so future Codex work does not bloat AGENTS.md.

Files likely involved
- docs/PROJECT_VISION.md
- docs/ARCHITECTURE.md
- docs/BENCHMARK_SPEC.md
- docs/EVAL_METHODOLOGY.md
- docs/DEMO_SCRIPT.md
- docs/CODEX_WORKFLOW.md
- docs/ROADMAP.md

Acceptance criteria
- docs/ folder exists.
- All seven docs are created.
- Docs are concise and practical.
- Docs explain the new positioning: benchmarking, observability, and governance for tool-using AI agents.
- Docs distinguish implemented MVP features from planned future features.
- No app behavior changes.

Validation commands
- git status
- No backend/frontend tests required if markdown-only.

Notes / guardrails for Codex
- Do not edit AGENTS.md.
- Do not edit README.md unless absolutely necessary.
- Do not change backend or frontend code.
- Do not add dependencies.
- Do not over-document.
- Do not claim LangGraph/comparison features already exist.


