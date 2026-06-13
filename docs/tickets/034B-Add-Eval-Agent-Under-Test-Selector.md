# Ticket 034B — Add eval Agent Under Test selector and result identity display

## Goal

Let users choose which Agent Target to benchmark from the frontend eval runner.

Ticket 034A added the Agent Targets panel where users can list, create, and test agent targets. Ticket 033B already added backend support for passing agent_target_id to /evals/run.

This ticket connects the frontend eval flow to that backend capability.

After this ticket, the user should be able to:

text id="6uyvnl" 1. View available Agent Targets. 2. Choose an Agent Under Test in the eval runner. 3. Run benchmark evals against that selected target. 4. See which agent was evaluated in the result/comparison UI. 

This completes the MVP “bring your own agent endpoint” story.

---

## Product story after this ticket

ARW should now clearly support:

text id="goyd0n" ReferenceIncidentAgent Built-in sample agent for local demos.  HTTP JSON Agent Target External user-provided agent endpoint. 

The benchmark flow should feel like:

text id="btot7p" Select Agent Under Test         ↓ Run benchmark suite         ↓ ARW sends cases to selected agent         ↓ ARW validates / guardrails / scores         ↓ Results show which agent was benchmarked 

The demo should no longer feel like ARW is evaluating itself.

---

## Current state

Already implemented:

### Ticket 032

- AgentUnderTest boundary
- AgentTask
- AgentResult
- AgentIdentity
- ReferenceIncidentAgent
- eval runner uses adapter boundary
- agent identity included in backend eval/run output

### Ticket 033A

- backend AgentTarget registry
- GET /agent-targets
- POST /agent-targets
- GET /agent-targets/{target_id}
- default ReferenceIncidentAgent target

### Ticket 033B

- HttpJsonAgent
- POST /agent-targets/{target_id}/test
- /evals/run accepts optional agent_target_id
- default behavior preserved when no agent_target_id is passed

### Ticket 034A

- frontend Agent Targets panel
- frontend can list/create/test targets
- eval behavior unchanged
- /evals/run currently still only sends prompt_version

Now update the eval UI.

---

## Required frontend implementation

## 1. Update eval run API client payload

Update frontend API types/client.

Likely files:

text id="8mx492" apps/web/src/lib/api.ts apps/web/src/types.ts 

or wherever eval API types are defined.

Current /evals/run probably sends something like:

json id="oox6ai" {   "prompt_version": "v1" } 

Update it to optionally send:

json id="3sz7p1" {   "prompt_version": "v1",   "agent_target_id": 2 } 

Rules:

- agent_target_id should be optional.
- If no target is selected, preserve old behavior.
- Do not break existing eval run behavior.
- Use number id, not name.

---

## 2. Load Agent Targets in eval runner UI

Wherever the eval runner controls live, fetch available Agent Targets.

Likely existing components/files:

text id="1385zj" apps/web/src/app/page.tsx apps/web/src/components/EvalRunner.tsx apps/web/src/components/EvalPanel.tsx 

Use the API method added in Ticket 034A:

ts id="g10v8q" listAgentTargets() 

The eval runner should display a selector:

text id="dyx2wp" Agent Under Test [ReferenceIncidentAgent v1 — built-in sample ▼] 

Options should include:

- default/reference target
- all registered http_json targets

Option labels should be clear:

text id="vju5y5" ReferenceIncidentAgent v1 — built-in sample My External Incident Agent v1 — HTTP JSON endpoint 

If target list fails to load:

- show a small warning/error
- preserve current eval behavior
- do not block old default eval path if possible

---

## 3. Default selection behavior

Default should be the backend default reference target.

Suggested behavior:

- If a target has is_default: true, select it by default.
- Otherwise select the first reference target.
- Otherwise leave selection empty and let backend default apply.

Important:

- Existing users should still be able to run evals even if target loading fails.
- If selected target is reference/default, it is okay to send its id or omit id.
- Simpler: send selected agent_target_id whenever one is selected.
- If no target is selected, omit agent_target_id.

---

## 4. Send selected agent_target_id to /evals/run

When the user runs evals, include selected target id.

Example:

ts id="yf2394" await runEvals({   prompt_version: selectedPromptVersion,   agent_target_id: selectedAgentTargetId ?? undefined, }); 

Do not change other eval params.

Do not add new backend behavior.

---

## 5. Show selected agent identity in eval results

Backend should already return agent identity from Ticket 033B.

Update frontend result rendering to show:

text id="5kpiac" Agent Under Test: My External Incident Agent Type: HTTP JSON Version: v1 

or:

text id="f8v6i6" Agent Under Test: ReferenceIncidentAgent Type: Built-in sample Version: v1 

Where to show:

- near eval summary/result header
- or inside eval result details
- wherever current eval run output is shown

Use whatever fields backend actually returns, such as:

text id="2kbc5k" agent_under_test agent_name agent_type agent_version agent_identity 

Match current API response shape.

Do not create a huge UI redesign.

---

## 6. Show agent identity in comparison table if already available

If the existing eval comparison API response includes agent identity/config metadata, update the comparison table to include:

text id="ev8exf" Agent Agent Type Agent Version 

or a compact single column:

text id="5mvz86" Agent Under Test ReferenceIncidentAgent v1 

If comparison API does not expose the data yet, do not do a backend refactor in this ticket unless it is tiny and clearly additive.

Minimum requirement:

- eval run result must show selected agent identity

Nice-to-have:

- comparison table shows agent identity

---

## 7. Keep Agent Targets panel and eval runner loosely coupled

Do not overbuild global state.

Options:

- Agent Targets panel manages its own list/create/test state.
- Eval runner separately fetches targets.
- Or parent page fetches targets and passes to both if already clean.

Prefer the simplest approach consistent with current app architecture.

If creating a new target in Agent Targets panel does not immediately appear in eval selector until refresh, that is acceptable for MVP, but better if easy to refresh.

Do not spend too much time on shared state.

---

## UI copy requirements

Use clear product language.

Eval selector label:

text id="ez49v7" Agent Under Test 

Helper text:

text id="yyz70n" Choose the agent target ARW should benchmark. The ReferenceIncidentAgent is the built-in sample target; HTTP JSON targets are external agents you registered. 

For reference target:

text id="qz27o3" Built-in sample 

For HTTP target:

text id="9txvsx" External HTTP JSON 

Result label:

text id="lfzh72" Benchmarked agent 

or:

text id="7gkns9" Agent Under Test 

Avoid vague wording like “model” because this is not only model comparison. It is agent benchmarking.

---

## Non-goals

Do not implement in Ticket 034B:

- create/edit/delete Agent Targets
- changing default target
- token reveal/masking UI beyond 034A
- arbitrary agent code upload
- file upload
- LangGraph UI
- SDK
- CLI
- full plugin marketplace
- auth improvements
- WebSocket/streaming evals
- major dashboard redesign
- new frontend dependencies

---

## Acceptance criteria

### Eval selector

- Eval UI shows an Agent Under Test selector.
- Selector loads targets from GET /agent-targets.
- Default selected target is ReferenceIncidentAgent or backend is_default target.
- Selector includes HTTP JSON targets created through 034A.
- UI clearly distinguishes:
  - built-in sample agent
  - external HTTP JSON agent

### Eval execution

- Running eval sends selected agent_target_id to /evals/run.
- If no target is selected, eval still works using backend default.
- Existing prompt version selection still works.
- Existing eval behavior is preserved.

### Result display

- Eval result displays which agent was benchmarked.
- At minimum show:
  - agent name
  - agent type
  - version if available
- Reference agent is labeled as built-in sample.
- HTTP JSON agent is labeled as external HTTP JSON.

### Comparison display

- If backend comparison data includes agent identity, comparison UI shows it.
- If not available, do not block the ticket.

### Compatibility

- Existing Agent Targets panel from 034A still works.
- Existing run/trace/guardrail/approval UI still works.
- No new frontend dependencies.
- Frontend typecheck passes.
- Backend tests pass.

---

## Testing / validation

Run:

bash id="8847rk" cd apps/web && npm run typecheck 

Expected:

text id="txvztm" passes 

Run backend tests:

bash id="e7t37w" cd apps/api && python -m pytest 

Current backend baseline:

text id="i7gdpa" 79 passed 

Expected:

text id="ny0gxl" all backend tests pass 

Manual checks:

1. Start backend and frontend.
2. Open web app.
3. Confirm Agent Targets panel still loads.
4. Confirm eval runner shows Agent Under Test selector.
5. Confirm ReferenceIncidentAgent is selected by default.
6. Run eval with reference target.
7. Confirm eval result shows ReferenceIncidentAgent.
8. Add or use an existing HTTP JSON target.
9. Select the HTTP JSON target in eval runner.
10. Run eval.
11. Confirm request sends agent_target_id.
12. Confirm eval result shows the external target identity.
13. Confirm existing prompt version selection still works.
14. Confirm comparison table still renders.

For HTTP JSON manual testing, use a tiny local fake agent endpoint if needed.

---

## Implementation guardrails for Codex

- Keep this frontend-focused.
- Use existing API methods and component style from 034A.
- Do not redesign the dashboard.
- Do not add new dependencies.
- Do not add backend functionality unless a tiny additive schema/type fix is required.
- Do not change Agent Targets create/test behavior.
- Preserve default eval flow.
- Make the “Agent Under Test” concept obvious in the UI.
- Keep the implementation MVP-level and readable.

---

