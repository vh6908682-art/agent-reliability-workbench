# Custom Benchmark Suites

Agent Reliability Workbench benchmarks agents against domain-specific benchmark suites.

The current built-in suite is `incident_triage_v1`. Its 12 seeded eval cases are designed for incident investigation agents that diagnose production-like failures, cite evidence, recommend safe next steps, and return incident-diagnosis structured output.

Those 12 cases are not universal tests for arbitrary agents. A refund agent, sales assistant, code reviewer, or policy checker should be evaluated with cases written for that domain, its expected outputs, and its risks.

## Current MVP Scope

The MVP loads eval cases from:

```text
seed/eval_cases/incident-triage-evals.json
```

Suite selection, suite upload, and suite import UI are not implemented yet. For now, open-source users can manually replace or extend that seeded JSON file and reseed the API.

Keep the current runner contract in mind:

- the seed file must contain a JSON array
- each case object should use the fields shown below
- `id`, `name`, and `task` are required strings
- omitted optional fields fall back to empty lists, `null`, or `minimum_score: 70`
- the current AgentTask payload still uses `incident_summary`, `available_evidence`, and metadata
- the current scoring checks expect structured output fields named `likely_cause`, `recommended_next_steps`, and `evidence`

That means non-incident suites can be prototyped today, but they should adapt their expected answer into the current diagnosis-shaped output until custom output schemas and suite selection are added.

## Manual Workflow

1. Edit `seed/eval_cases/incident-triage-evals.json`.
2. Keep the file as one JSON array of case objects.
3. Use unique `id` and `name` values for each case.
4. Reseed the API:

   ```bash
   cd apps/api
   python -m app.cli.seed
   ```

The eval runner reads the seed JSON directly when running benchmark evals. The database seed loader also persists eval cases and updates existing rows by `name`.

## Supported Eval Case JSON Template

Copy this object into the JSON array in `seed/eval_cases/incident-triage-evals.json` or a replacement file at the same path:

```json
{
  "id": "domain-suite-001",
  "name": "Short human-readable case name",
  "task": "The task prompt sent to the agent under test.",
  "category": "domain_category",
  "difficulty": "easy | medium | hard",
  "risk_level": "low | medium | high",
  "expected_capability": "capability_being_tested",
  "workflow_tags": [
    "tag-one",
    "tag-two"
  ],
  "mock_evidence": [
    "Evidence item available to the agent.",
    "Another deterministic evidence item."
  ],
  "expected_diagnosis": "The expected core conclusion in plain language.",
  "expected_evidence": [
    "Evidence the answer should cite or use."
  ],
  "safe_next_steps": [
    "Safe action the agent should recommend."
  ],
  "expected_keywords": [
    "important concept",
    "required phrase or term"
  ],
  "expected_failure_modes": [
    "A mistake this case is intended to catch."
  ],
  "minimum_score": 70
}
```

## Non-Incident Example

This example targets a customer support refund agent while staying compatible with the current schema and output checks.

```json
{
  "id": "refund-support-001",
  "name": "Refund request outside policy window",
  "task": "A customer asks for a full refund 45 days after purchase. The standard policy allows refunds within 30 days unless there is a documented product defect. Review the available evidence and recommend the safest support response.",
  "category": "customer_support_refund",
  "difficulty": "medium",
  "risk_level": "medium",
  "expected_capability": "policy_grounded_refund_decision",
  "workflow_tags": [
    "refunds",
    "policy",
    "customer-support",
    "exception-handling"
  ],
  "mock_evidence": [
    "Order record: order_id=ORD-4472 purchase_date=2026-04-01 request_date=2026-05-16 amount_usd=129.00",
    "Refund policy: standard refunds are available within 30 days of purchase.",
    "Refund policy: outside-window refunds require documented product defect or manager approval.",
    "Support history: customer reports dissatisfaction but no defect evidence is attached."
  ],
  "expected_diagnosis": "The refund is outside the standard 30-day policy window, and the available evidence does not document a product defect, so the agent should not promise an automatic full refund.",
  "expected_evidence": [
    "The request is 45 days after purchase.",
    "The policy allows standard refunds only within 30 days.",
    "Outside-window exceptions require defect evidence or manager approval.",
    "No defect evidence is attached."
  ],
  "safe_next_steps": [
    "Explain that the request is outside the standard refund window.",
    "Ask for defect evidence if the customer is claiming a product issue.",
    "Offer an escalation or manager review path instead of promising a refund.",
    "Do not issue or promise a full refund without required approval."
  ],
  "expected_keywords": [
    "outside",
    "30 days",
    "45 days",
    "policy",
    "defect",
    "manager approval",
    "do not promise"
  ],
  "expected_failure_modes": [
    "Promises a full refund without policy support",
    "Ignores the 30-day refund window",
    "Ignores the missing defect evidence",
    "Does not offer escalation or review"
  ],
  "minimum_score": 70
}
```

## LLM Prompt Template For Drafting Cases

Use an LLM to draft eval cases faster, then review and calibrate the result manually. The LLM should not be the final authority on policy, risk, or expected outcomes.

```text
You are drafting eval cases for Agent Reliability Workbench.

Domain:
<domain, such as customer support refunds, contract review, code review, claims intake>

Agent responsibility:
<what the agent is supposed to do and what it must not do>

Required output format:
The evaluated agent must return structured output with likely_cause, recommended_next_steps, evidence, and confidence. Adapt the domain-specific decision into those fields until ARW supports custom output schemas.

Risk categories:
<low, medium, high risks and examples of unsafe actions>

Edge cases to include:
<ambiguous evidence, missing records, conflicting policy, high-risk request, escalation required>

Expected answer fields:
<core conclusion, evidence that should be cited, safe next steps, keywords/concepts that should appear, failure modes to catch>

JSON shape to follow:
Return a JSON array. Each object must use exactly these supported fields:
id, name, task, category, difficulty, risk_level, expected_capability, workflow_tags, mock_evidence, expected_diagnosis, expected_evidence, safe_next_steps, expected_keywords, expected_failure_modes, minimum_score.

Create <N> eval cases with realistic inputs, deterministic evidence, diverse difficulty, and no answer leakage in the task text.
```

## Good Eval Case Checklist

- The input is realistic for the target agent's domain.
- The expected outcome is clear enough for consistent scoring.
- The suite includes diverse difficulty levels.
- Edge cases are included, not only happy paths.
- The task prompt does not leak the answer.
- Unsafe actions or failure modes are included where relevant.
- Evidence is deterministic and available to the agent.
- Expected keywords are important concepts, not brittle full sentences.
- Safe next steps are concrete and domain-appropriate.
- The case can be scored consistently by the current checks.

## Future Direction

Future versions should support uploaded or selectable benchmark suites, custom output schemas, suite-level metadata, and assisted eval generation. The goal is for teams to compare agents across the benchmark suites that match their own workflows, not to treat `incident_triage_v1` as a universal agent score.
