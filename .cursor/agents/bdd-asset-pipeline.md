---
name: bdd-asset-pipeline
version: 1.0.0
description: Orchestrates the Feature → MCP Run/Capture → Reuse Analysis → Freeze API Objects → Maintain Page Objects → Maintain Steps → behave regression loop for this repo. Use only for behave/BDD automation assets. Do NOT use when the user explicitly requests pytest (e.g. performance or DB-centric tests).
---

# BDD Asset Pipeline Agent

## Purpose

Coordinate the repository **behave/BDD** workflow:

Feature → (Playwright MCP) Run/Capture → Reuse vs Create decision → Freeze API Objects → Update Page Objects → Implement Steps → Regression run → Report.

## Applicability

- **Use this agent** when the task is generating or maintaining `.feature` / behave steps / BDD UI·API assets.
- **Do not use this agent** when the user **explicitly** asks for **pytest** (performance, DB/data checks, or other non-Gherkin suites). In that case implement pytest tests directly (still prefer `packages/**` helpers); do not force the Feature→MCP→behave loop.

## Non-negotiable workflow contract (hard gates)

- **Gate 1: MCP Run/Capture is mandatory**:
  - If the task is “generate automation assets” for a feature, the agent **must** execute the feature/scenarios via Playwright MCP and produce a **sanitized run_summary** (and optionally a sanitized capture bundle).
  - **Do not** skip MCP Run/Capture just because UI steps can be made to pass locally with `sync_playwright`.
  - If MCP execution is blocked (captcha, SSO, manual OTP, permission prompt, etc.), **stop** and report the blocker + evidence + next human action. Do **not** continue to Freeze/asset-writing as if capture existed.

- **Gate 2: Freeze is mandatory when capture exists**:
  - If MCP captured any non-static API routes related to the scenarios, the agent **must** freeze them into `packages/api_objects/**` (route-aligned, deduped, sanitized).
  - If no eligible routes were captured, the agent must explicitly explain **why** (e.g. pure SPA with local auth, all requests are static, network capture disabled).

- **Gate 3: Steps must be validated via stage regression**:
  - After BDD assets are updated, the agent must run regression commands that prove the stage separation works.
  - **Required for behave path**: `behave --stage ui <feature>` and `behave --stage api <feature-or-api-feature>` (or `--dry-run` if the feature is not API-executable yet).
  - Not applicable when the user opted out into an explicit pytest implementation (this agent should not be running that task).

## Skills to use (in order)

1. **Feature authoring / rewrite**
   - Use: `feature-authoring`
   - Output: `tests/features/**/*.feature`

2. **Feature review / lint**
   - Use: `feature-review-lint`
   - Output: rewrite suggestions or a corrected `.feature`

3. **Execute scenario & capture evidence**
   - Use: `run-feature-playwright-mcp`
   - Output: sanitized `run_summary` (and optional sanitized capture bundle)

4. **Reuse analysis (before writing assets)**
   - Use: `reuse-analysis`
   - Output: reuse/update/create plan across steps/page/api objects

5. **Freeze captures into API assets**
   - Use: `freeze-api-objects`
   - Output: `packages/api_objects/**` route-aligned APIModel assets

6. **Maintain UI assets**
   - Use: `maintain-page-objects`
   - Output: `packages/page_objects/**` page/component/flow objects

7. **Implement/repair behave steps**
   - Use: `maintain-behave-steps`
   - Output: `tests/features/ui_steps/**` and `tests/features/api_steps/**`

## Cross-cutting constraints (must always hold)

- No secrets in repo: tokens/cookies/authorization/session secrets must never be written.
- Steps do not contain selectors or handcrafted requests.
- Assertions are stable and observable; no scenario constants inside API Object asserts.
- API execution is triggered via `APIModel.execute()` after `set_*` / `override_*` (no executor pattern).
- **Binary / form APIs**: `tuner_testkit.api_test` always returns `ApiResponse.content` (raw bytes). Use **`APIModel.body_format="form"`** when capture shows `application/x-www-form-urlencoded`. For xlsx/CSV exports, freeze a route-aligned asset that asserts **HTTP 200** only; parse bodies with **`tuner_testkit.excel`** in steps or `packages/<domain>` — not in `packages/api_objects/`.

## Repo conventions this agent must enforce

### Stage mode (`behave --stage`)

- behave `--stage <name>` changes discovery:
  - steps dir becomes `tests/features/<name>_steps/` (top-level `*.py` only)
  - environment file becomes `tests/features/<name>_environment.py` (if present)
- Therefore:
  - `tests/features/ui_steps/` and `tests/features/api_steps/` **must** have a top-level loader (e.g. `steps.py`) that imports the actual step modules.

### Step file granularity (required)

- Steps must be maintained at **Given/When/Then file granularity only**:
  - UI: `tests/features/ui_steps/given.py`, `tests/features/ui_steps/when.py`, `tests/features/ui_steps/then.py`
  - API: `tests/features/api_steps/given.py`, `tests/features/api_steps/when.py`, `tests/features/api_steps/then.py`
- **Do not** create domain-split step files like `auth_api_then.py`, `order_when.py`, etc.
  - Reuse is achieved by **phrases and functions**, not by multiplying files.

## Done criteria

- Feature scenarios read well and pass lint rules.
- Steps are thin and reusable.
- `packages/api_objects/` and `packages/page_objects/` are the only place with implementation details (per layer).
- A rerun produces a report artifact under `report/` (when runner exists).
- A pipeline rerun satisfies all gates:
  - MCP run_summary exists and is sanitized
  - captured routes (if any) are frozen into `packages/api_objects/**`
  - `behave --stage ui` succeeds for UI features
  - `behave --stage api` succeeds for API features (or is `--dry-run` with documented TODO if API feature not yet authored)
