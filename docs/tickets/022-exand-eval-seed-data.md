## Ticket 022 — Expand eval seed data to 12 benchmark incidents

Goal  
Turn the eval suite from a small MVP demo into a realistic incident benchmark set.

Files likely involved
- Eval seed data files
- Mock logs
- Mock payloads
- Mock service configs
- Mock runbooks
- Eval case definitions
- Tests for eval seed loading / runner behavior

Acceptance criteria
- Add or update benchmark cases for:
  1. Kafka duplicate key retry exhaustion
  2. Missing required payload field
  3. Schema version mismatch
  4. Downstream timeout
  5. Database unique constraint violation
  6. Poison message / DLQ growth
  7. Bad service config
  8. Stale runbook
  9. High-risk remediation recommendation
  10. PII leakage risk
  11. Ambiguous evidence case
  12. Multi-symptom root cause case
- Each case includes realistic mock evidence.
- Each case includes expected diagnosis / expected evidence / safe next steps.
- Each case includes scoring checks.
- Eval runner can run all cases.

Validation commands
- cd apps/api && python -m pytest
- Run existing eval endpoint manually if local app is available.
- git status

Notes / guardrails for Codex
- Do not redesign eval scoring in this ticket unless required.
- Do not add LangGraph.
- Do not build comparison UI.
- Keep incidents realistic but compact.
- Avoid massive mock files.
