---
name: maintain-page-objects
version: 1.0.0
description: Creates or updates Python Playwright Page Objects under packages/page_objects/ following page-objects-syntax.md. Use when UI steps fail due to locators, new UI flows are needed, or selector leakage must be removed from steps.
---

# Maintain Page Objects (Python + Playwright)

## Scope

- **Primary goal**: encapsulate UI locators & interactions for stable reuse.
- **Write scope**: `packages/page_objects/**` only.
- **Must follow**: `page-objects-syntax.md`.

## Hard rules

- Steps must not contain selectors; selectors must live only inside page objects.
- Prefer locator priority:
  1) get_by_role / get_by_label / get_by_text
  2) get_by_test_id
  3) structured CSS (minimal)
  4) XPath (last resort; avoid in phase 1)
- Do not use fixed sleeps; wait by conditions inside action/assert methods.
- Separate actions and assertions; expose only business-level methods.
- Do not hardcode environment host; accept `base_url`/config.

## Output expectations

- Organize by pages/components (and optional flows):
  - `packages/page_objects/pages/`
  - `packages/page_objects/components/`
  - optional `packages/page_objects/flows/` for cross-page orchestration (no selectors inside flows)
- Public API is actions (`open/login/submit/...`) and assertions (`assert_*`).

## Quick validation

- No locator objects leaked to steps.
- No `nth()`/index-based core locators unless explicitly justified by constraints.

## Pipeline expectation (required)

- Page Objects updates must be driven by evidence:
  - Prefer Playwright MCP snapshots and/or run_summary findings when available.
  - If MCP evidence is missing, state the uncertainty explicitly and avoid overfitting selectors.
