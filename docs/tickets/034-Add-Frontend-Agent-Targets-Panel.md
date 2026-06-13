# Ticket 034A — Add frontend Agent Targets panel

## Goal

Add a frontend panel for viewing, creating, and testing Agent Targets.

Backend support already exists:

- Ticket 032: AgentUnderTest boundary and ReferenceIncidentAgent
- Ticket 033A: backend AgentTarget registry
- Ticket 033B: HttpJsonAgent adapter and connection test endpoint

This ticket makes the Agent Target registry visible in the web portal.

After this ticket, the user should be able to see:

text id="mrmhgj" Agent Targets - ReferenceIncidentAgent - External HTTP JSON agents 

And create/test an external HTTP JSON agent endpoint from the UI.

Do not update eval runner agent selection in this ticket.  
That belongs to Ticket 034B.

---

## Product reason

ARW is positioned as an agent benchmarking tool.

The backend can now register and call external HTTP JSON agents, but the frontend still does not clearly show the “agent under test” concept.

This ticket makes the product story visible:

> ARW benchmarks explicit Agent Targets. The built-in ReferenceIncidentAgent is the default sample target. Users can register their own HTTP JSON agent endpoint.

---

## Current backend API

Use the existing backend endpoints from Tickets 033A/033B:

http id="jt67ym" GET /agent-targets POST /agent-targets GET /agent-targets/{target_id} POST /agent-targets/{target_id}/test 

Expected target shape is approximately:

json id="nux7ww" {   "id": 1,   "name": "ReferenceIncidentAgent",   "agent_type": "reference",   "endpoint_url": null,   "auth_type": "none",   "version": "v1",   "description": "Built-in sample incident-response agent used for local demos.",   "is_default": true,   "has_auth_token": false,   "created_at": "...",   "updated_at": "..." } 

HTTP JSON target create request:

json id="8i3y2v" {   "name": "My External Incident Agent",   "agent_type": "http_json",   "endpoint_url": "http://host.docker.internal:9000/run",   "auth_type": "none",   "auth_token": null,   "version": "v1",   "description": "Local external agent endpoint" } 

Connection test response is approximately:

json id="epubvn" {   "ok": true,   "agent_target_id": 2,   "agent_name": "My External Incident Agent",   "agent_type": "http_json",   "message": "Agent target responded with a valid structured result." } 

or:

json id="3tb8bq" {   "ok": false,   "agent_target_id": 2,   "agent_name": "My External Incident Agent",   "agent_type": "http_json",   "message": "Agent target returned invalid JSON.",   "error": "..." } 

Adjust field names only if the backend uses slightly different names.

---

## Required frontend implementation

### 1. Add frontend API client methods

Update the frontend API client/types.

Likely files:

text id="ire0i8" apps/web/src/lib/api.ts apps/web/src/types.ts 

or existing equivalents.

Add types:

ts id="ev7ry6" export type AgentTarget = {   id: number;   name: string;   agent_type: "reference" | "http_json";   endpoint_url?: string | null;   auth_type: "none" | "bearer";   version?: string | null;   description?: string | null;   is_default: boolean;   has_auth_token?: boolean;   created_at?: string;   updated_at?: string; };  export type AgentTargetCreate = {   name: string;   agent_type: "http_json";   endpoint_url: string;   auth_type: "none" | "bearer";   auth_token?: string | null;   version?: string | null;   description?: string | null; };  export type AgentTargetTestResult = {   ok: boolean;   agent_target_id: number;   agent_name: string;   agent_type: "reference" | "http_json";   message: string;   error?: string | null; }; 

Add API methods:

ts id="o0ogkv" listAgentTargets() createAgentTarget(payload) testAgentTarget(targetId) 

Use existing frontend fetch/error-handling style.

---

### 2. Add AgentTargetsPanel component

Create a new component.

Likely file:

text id="agkycx" apps/web/src/components/AgentTargetsPanel.tsx 

or wherever existing dashboard panels live.

The panel should show:

text id="2znszj" Agent Targets 

Short explanatory copy:

text id="ppnhzy" ARW benchmarks explicit Agent Targets. The ReferenceIncidentAgent is the built-in sample target for local demos. Add an HTTP JSON endpoint to benchmark your own agent. 

Display list of targets:

For each target show:

text id="945lsc" Name Type: reference/http_json Version Default badge if is_default Endpoint URL for http_json Description if present Auth: none/bearer Token configured: yes/no if has_auth_token exists 

Important UI language:

- For ReferenceIncidentAgent, label it clearly as:

text id="pgd9ab" Built-in sample agent 

- For http_json, label it as:

text id="qcwo9d" External HTTP JSON agent 

This makes the subject under test obvious.

---

### 3. Add create HTTP JSON target form

Inside the panel, add a small form.

Fields:

text id="8v9fga" Name Endpoint URL Version Description Auth Type: none/bearer Auth Token optional, only relevant for bearer 

Defaults:

text id="dkxx4h" agent_type = http_json auth_type = none version = v1 

Behavior:

- submit calls POST /agent-targets
- on success, refresh target list
- clear form or keep reasonable defaults
- show success message
- show backend validation errors clearly
- prevent empty name
- prevent empty endpoint URL

Do not overbuild validation.

---

### 4. Add Test Connection button

For each Agent Target row/card, add a button:

text id="j7pfnr" Test Connection 

Behavior:

- calls POST /agent-targets/{id}/test
- shows result inline near that target
- success should be visually clear
- failure should show message and error if present

For the ReferenceIncidentAgent, the backend may return success without external HTTP call. Display that normally.

For http_json, the user should understand the endpoint must be running.

Example inline result:

text id="48eyzd" Connection test passed: Agent target responded with a valid structured result. 

or:

text id="v67jxm" Connection test failed: Agent target returned invalid JSON. 

---

### 5. Add panel to main dashboard/page

Add AgentTargetsPanel to the existing main page/dashboard.

Likely files:

text id="bju2zo" apps/web/src/app/page.tsx 

or wherever the current dashboard is assembled.

Place it somewhere visible but not disruptive.

Suggested placement:

text id="iz985w" near eval controls 

or after the existing run/eval panels.

Do not redesign the whole page.

---

## Non-goals

Do not implement in Ticket 034A:

- eval runner Agent Under Test dropdown
- sending agent_target_id to /evals/run
- comparison table changes
- editing existing targets
- deleting targets
- setting a new default target
- masking/revealing stored tokens
- complex auth UI
- file upload
- arbitrary code upload
- LangGraph UI
- SDK/CLI docs
- major dashboard redesign

Those belong to later tickets.

Ticket 034B will add eval target selection.

---

## Acceptance criteria

### API client

- Frontend can fetch agent targets.
- Frontend can create an HTTP JSON agent target.
- Frontend can test an agent target connection.
- Types match backend response shape.

### UI

- Agent Targets panel is visible in the web app.
- Default ReferenceIncidentAgent appears in the list.
- It is clearly labeled as the built-in sample agent.
- HTTP JSON targets are clearly labeled as external HTTP JSON agents.
- User can create a new HTTP JSON target.
- User can test a target connection.
- Loading, error, and success states are handled.
- Existing dashboard functionality still works.

### Compatibility

- Existing eval UI continues to work.
- No eval request behavior changes in this ticket.
- No new frontend dependencies unless absolutely necessary.
- Keep styling consistent with current app.

---

## Testing / validation

Run:

bash id="3vbv7j" cd apps/web && npm run typecheck 

Expected:

text id="1xuamg" passes 

Run backend tests to ensure no accidental API breakage:

bash id="4k4fib" cd apps/api && python -m pytest 

Current backend baseline:

text id="jwt9tz" 79 passed 

Expected:

text id="uj1jtb" all backend tests pass 

Manual checks:

1. Start backend and frontend.
2. Open web app.
3. Confirm Agent Targets panel appears.
4. Confirm ReferenceIncidentAgent appears as default/built-in sample.
5. Add an HTTP JSON target.
6. Confirm it appears in the list.
7. Click Test Connection.
8. Confirm success/failure message renders cleanly.
9. Confirm existing run/eval panels still work as before.

---

## Implementation guardrails for Codex

- Keep this frontend-only unless tiny backend type mismatch fixes are unavoidable.
- Do not implement eval target selector yet.
- Do not send agent_target_id to /evals/run yet.
- Do not redesign the dashboard.
- Do not add new UI dependencies.
- Use existing component styling patterns.
- Keep the panel readable and MVP-level.
- Make the product story obvious: ARW benchmarks explicit Agent Targets.
- Clearly label ReferenceIncidentAgent as the built-in sample target.
- Clearly label HTTP JSON targets as external agents.

---

