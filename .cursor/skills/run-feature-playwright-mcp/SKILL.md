---
name: run-feature-playwright-mcp
version: 1.1.0
description: Runs behave Gherkin scenarios (or records an explore session) via Playwright MCP with Run→Capture→Freeze workflow and strict sanitization. Evidence always lands under artifacts/evidence/<run_id>/. Do NOT require this skill when the user explicitly requests pytest-only work with no MCP capture need.
---

# Run Feature via Playwright MCP (Run → Capture)

## Scope

- **Primary goal**: execute a scenario **or explore session** and persist structured, sanitized network evidence.
- **Write scope**: `artifacts/evidence/<run_id>/` (`run_summary.md` required; `network.jsonl` required; optional `actions.jsonl` / `snapshots/`).
- **Must follow**: `bdd-run-gherkin-in-playwrightMCP.md`. Explore-first sessions are valid evidence (no `.feature` required).

## Hard requirement (do not skip)

- If the user request is “generate automation assets” (steps/page/api objects / design notes), you **must** run at least one representative scenario **or explore session** via Playwright MCP and persist sanitized evidence under `artifacts/evidence/<run_id>/`.
- If MCP execution cannot proceed (captcha/SSO/OTP/manual permission prompts/unreachable env), you must **stop** and report:
  - where it blocked (page/url)
  - what human action is needed
  - what evidence was collected (snapshot/network summary)
  - what assets can/cannot be generated without capture

## Run → Capture requirements

- Capture **minimum fields** per request/response:
  - scenario_id, run_id, timestamp
  - request: method, url (for parsing), host, path, query, headers, body
  - response: status, headers, body_sample (allow truncation)
- Compute (for downstream freeze):
  - method, normalized_path, query_keys, body_keys, content_type
  - fingerprint = method + normalized_path + sorted(query_keys) + sorted(body_keys)

## Sanitization (hard rules)

- Never persist forbidden header keys (case-insensitive):
  - Authorization, Cookie, Set-Cookie, X-Token, *token*, *secret*, *password*, *session*
- Mask sensitive values in query/body/response_sample:
  - JWT/long tokens: keep only head/tail 4–6 chars, mask middle
  - phone/email/id: mask
  - signatures/keys: replace with `***`

## Output artifacts

- **`artifacts/evidence/<run_id>/run_summary.md`** (required):
  - scenarios / explore intent, pass/fail + high-level failure class (UI/API/env/script)
  - captured routes list (method/path)
  - intended api_objects create/update list (by method/path + version intent)
  - sanitizer applied statement
- **`artifacts/evidence/<run_id>/network.jsonl`** (required, sanitized):
  - one capture per request (see spec minimum fields)
- **`artifacts/evidence/<run_id>/actions.jsonl`** / `snapshots/` (optional)

## Verification checklist (must include in result)

- The run_summary explicitly states:
  - captured routes (method + path only; no host)
  - sanitizer applied (no Authorization/Cookie/*token*/*password* keys persisted)
  - whether freeze should create/update which `packages/api_objects/**`

## Must not do

- Do not write any real token/cookie into repo (including captures).
- Do not directly create `packages/api_objects/` here; freezing is handled by `freeze-api-objects`.
