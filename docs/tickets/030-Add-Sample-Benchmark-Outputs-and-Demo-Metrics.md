# Ticket 030 — Add Sample Benchmark Outputs and Demo Metrics

## Goal

Add lightweight sample benchmark outputs that make Agent Reliability Workbench easier to demo, explain, and present.

This ticket should create static/sample artifacts only. The goal is to show what a benchmark run and eval comparison look like without requiring someone to run the whole app first.

This makes the README, demo script, and eventual GitHub presentation stronger.

---

## Context

The project now has:

- agent run creation
- trace persistence
- structured output validation
- guardrail/governance checks
- seeded eval execution
- eval comparison across prompt/config metadata
- backend smoke tests proving the core flow works

The next step is to make the project more presentable by adding realistic sample outputs.

These samples should be honest representations of the existing system, not fabricated claims about unsupported features.

---

## Files likely involved

- docs/examples/
- docs/examples/sample-agent-run.json
- docs/examples/sample-trace.json
- docs/examples/sample-eval-run.json
- docs/examples/sample-eval-comparison.json
- README.md
- docs/DEMO_SCRIPT.md

Create docs/examples/ if it does not exist.

---

## Required sample artifacts

### 1. Sample agent run output

Create:

text docs/examples/sample-agent-run.json 

Include a representative successful incident investigation run.

It should include fields such as:

- run id or placeholder id
- task / incident prompt
- answer or diagnosis
- structured output
- validation status
- guardrail result
- approval status
- model/config metadata:
  - model_name
  - prompt_version
  - workflow_type
  - toolset_name
  - guardrail_mode
- latency / token / cost metadata if supported

Use actual field names from the current API where possible.

---

### 2. Sample trace output

Create:

text docs/examples/sample-trace.json 

Include a compact trace showing the main steps:

- retrieval/context step
- LLM/diagnosis step
- structured validation step
- guardrail step
- final response step

Do not include huge prompts or noisy blobs. Keep it readable.

---

### 3. Sample eval run output

Create:

text docs/examples/sample-eval-run.json 

Include representative eval results across seeded benchmark cases.

Include fields such as:

- eval run id or placeholder id
- total cases
- case results
- pass/fail or score
- expected signals
- actual diagnosis summary
- latency/cost metadata if supported
- config metadata

Use realistic but concise values.

---

### 4. Sample eval comparison output

Create:

text docs/examples/sample-eval-comparison.json 

Show comparison across at least two prompt/config variants.

Example comparison dimensions:

- prompt_version v1
- prompt_version v2

Include aggregate fields such as:

- total cases
- passed
- failed
- pass rate
- average score
- average latency
- average cost
- guardrail failures
- config metadata

Use actual field names from the current comparison API where possible.

---

## README updates

Update README.md to link to the example files.

Add a short section like:

md ## Example Outputs  Sample outputs are available in `docs/examples/`:  - sample agent run - sample trace - sample eval run - sample eval comparison 

Keep it brief.

---

## Demo script updates

Update docs/DEMO_SCRIPT.md to mention that the sample outputs can be used when explaining the project without running the app live.

Do not make the demo script longer than necessary.

---

## Acceptance criteria

- docs/examples/ exists.
- Sample JSON files are valid JSON.
- Samples reflect the actual current product capabilities.
- Samples use realistic incident-investigation content.
- README links to the sample outputs.
- Demo script mentions sample outputs as fallback/reference artifacts.
- No application code is changed.
- No tests are required unless existing docs validation exists.

---

## Validation commands

bash python -m json.tool docs/examples/sample-agent-run.json python -m json.tool docs/examples/sample-trace.json python -m json.tool docs/examples/sample-eval-run.json python -m json.tool docs/examples/sample-eval-comparison.json git diff --check git status --short 

Optional:

bash cd apps/api && python -m pytest 

---

## Guardrails for Codex

- Do not edit backend code.
- Do not edit frontend code.
- Do not add dependencies.
- Keep JSON samples compact and readable.
- Do not overclaim unsupported features.
- Prefer current API field names where possible.
- Mark placeholder IDs clearly if needed.
- Do not include secrets, API keys, real customer data, or real internal data.