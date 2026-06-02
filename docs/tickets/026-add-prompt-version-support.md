## Ticket 026 — Add Prompt Version Support for Runs and Evals

### Goal

Allow agent runs and eval runs to use different prompt versions so the system can benchmark behavior across Prompt v1, Prompt v2, and future prompt variants.

This is the next step in making Agent Reliability Workbench a true benchmarking and governance platform: the system should not only compare models or configs, but also compare how prompt changes affect correctness, trace quality, latency, cost, and guardrail outcomes.

This ticket should keep prompt versioning simple and MVP-level. Do not build a full prompt management product yet.

---

### Context

The project is evolving around this core loop:

run → trace → validate → govern → evaluate → compare

Previous tickets added or planned support for tracking configuration metadata and comparing eval results. Prompt version support is needed so eval comparisons can answer questions like:

- Did Prompt v2 improve diagnosis accuracy?
- Did Prompt v2 reduce hallucinated tool usage?
- Did Prompt v2 increase latency or cost?
- Did Prompt v2 handle guardrails better?
- Which prompt version should become the default benchmark prompt?

For now, prompt versions should be defined in code/config files, not in a database-backed prompt registry.

---

### Files likely involved

Backend:

- Prompt template/config module
- Agent loop / agent runner
- Run creation schema
- Run service
- Eval runner
- Eval API route schemas
- Agent run database model if prompt version metadata is not already persisted
- Tests for run creation
- Tests for eval execution
- Possibly seed/default config files

Frontend, only if needed:

- Frontend API types
- Run creation request type
- Eval run request type

Docs, only if needed:

- Small update to eval or benchmark documentation explaining prompt version selection

---

### Requirements

#### 1. Define at least two prompt versions

Add a simple prompt version registry/config that supports at least:

- incident_triage_v1
- incident_triage_v2

The names can be adjusted if the existing project already has a naming convention, but there must be at least two distinct versions.

Each prompt version should include:

- A stable prompt version ID
- The actual prompt template/content
- A default prompt version constant

Prompt v2 does not need to be dramatically different. It can be a slightly more structured version of v1 that emphasizes:

- grounding in tool evidence
- avoiding unsupported conclusions
- returning a clear final diagnosis
- respecting guardrail and approval behavior

Keep this file/config based.

Do not add a prompt database table unless the current architecture already clearly supports it.

---

#### 2. Run creation should support prompt version selection

Update run creation flow so a user/API caller can optionally provide a prompt version.

Behavior:

- If no prompt version is provided, use the default prompt version.
- If a valid prompt version is provided, use that prompt version.
- If an invalid prompt version is provided, return a clear validation error.

The selected prompt version must be passed into the agent loop and used when constructing the agent/system prompt.

---

#### 3. Persist prompt version on agent runs

Each agent run should record the prompt version that was used.

This may already be covered by Ticket 023 configuration tracking. If that field already exists, reuse it.

Expected behavior:

- Run metadata includes prompt_version.
- Run detail API exposes prompt_version.
- Trace/eval comparison logic can later use this field.

Do not duplicate metadata fields if one already exists.

---

#### 4. Eval runner should support prompt version selection

Update eval runner so eval runs can be executed with a selected prompt version.

Behavior:

- If no prompt version is provided, use the default prompt version.
- If a valid prompt version is provided, use it for every agent run created by that eval run.
- Eval result/run metadata should preserve the prompt version used, either directly or through the linked agent run metadata.

This enables later comparison of:

- same benchmark cases + Prompt v1
- same benchmark cases + Prompt v2

---

#### 5. API schemas should expose prompt version cleanly

Update backend request/response schemas as needed.

Likely places:

- create run request
- run response/detail
- create eval run request
- eval run/result response if applicable

Keep names simple:

text prompt_version 

Do not introduce complex prompt objects in API responses yet.

---

#### 6. Tests

Add or update tests to verify:

- run creation uses default prompt version when omitted
- run creation uses explicit prompt version when provided
- invalid prompt version is rejected clearly
- eval runner uses default prompt version when omitted
- eval runner uses explicit prompt version when provided
- created runs persist the selected prompt version

Tests should focus on behavior, not implementation details.

---

### Acceptance Criteria

- At least two prompt versions are defined.
- There is a clear default prompt version.
- Run creation can select a prompt version or fall back to default.
- Eval runner can select a prompt version or fall back to default.
- Agent run metadata records the prompt version used.
- API responses expose the run prompt version.
- Invalid prompt versions produce a clear validation error.
- Tests cover default and explicit prompt version behavior.
- Existing MVP demo flow still works without requiring prompt version input.

---

### Validation Commands

Run backend tests:

bash cd apps/api && python -m pytest 

If frontend types are touched:

bash cd apps/web && npm run typecheck 

---

### Guardrails for Codex

- Do not build a full prompt management UI.
- Do not add a prompt registry database table unless already explicitly aligned with existing architecture.
- Do not over-engineer prompt lifecycle states like draft, active, archived, approval, rollback, etc.
- Do not introduce new frontend UI unless needed for type safety or existing forms.
- Keep prompt versions file/config based.
- Keep the implementation small and benchmark-oriented.
- Reuse existing run metadata/config tracking from Ticket 023 if available.
- Preserve existing MVP demo behavior.
- Do not redesign eval APIs beyond adding prompt version selection.
- Do not add new dependencies unless absolutely necessary.

---

### Implementation Hint

A good simple shape is:

text prompt_versions.py   DEFAULT_PROMPT_VERSION = "incident_triage_v1"    PROMPT_VERSIONS = {       "incident_triage_v1": "...",       "incident_triage_v2": "...",   }    get_prompt_template(prompt_version: str | None) -> str 

Then the run/eval flow can resolve the prompt version once, validate it, persist the resolved version, and pass the prompt content into the agent loop.

Codex should adapt this to the existing project structure instead of forcing this exact file name.