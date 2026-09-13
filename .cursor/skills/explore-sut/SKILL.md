---
name: explore-sut
version: 1.0.0
description: Explore-first Playwright MCP session against a live SUT. Produces sanitized artifacts/evidence/<run_id>/ plus assets/explore capability notes. Use when learning a web SUT, mapping pages/buttons, or gathering evidence before any .feature exists. Do NOT use when the user already has a feature to implement — use run-feature-playwright-mcp instead.
---

# Explore SUT (Playwright MCP)

## Scope

- **Primary goal**: walk a live web SUT, record what exists (pages, controls, APIs), persist evidence.
- **Write scope**: `artifacts/evidence/<run_id>/` (required); `assets/explore/<app>/*.md` (capability notes).
- **Must follow**: `docs/spec/sut-self-learning.md`, `docs/spec/bdd-run-gherkin-in-playwrightMCP.md`.
- **Out of scope**: freezing API/page objects (hand off to `freeze-api-objects` / `maintain-page-objects`); writing `.feature` (hand off to `feature-authoring`).

## Safety (live SUT)

- Prefer **read / create-on-throwaway-data**. Do not delete production-looking records without an explicit user OK.
- Do not submit payments, change other users' permissions, or hit admin destructive actions.
- Stop on captcha / SSO / OTP and report the blocker.
- Never persist secrets (same sanitizer as `run-feature-playwright-mcp`).

## Steps

1. Read `INDEX.md` and `INDEX.project.md` if present. Note base URLs from `config`.
2. Pick a **vertical slice** (e.g. workspace → project → issue), not a full-site crawl.
3. Navigate with Playwright MCP. After each meaningful action, dump network + snapshot.
4. Persist:
   - `artifacts/evidence/<run_id>/run_summary.md`
   - `artifacts/evidence/<run_id>/network.jsonl` (sanitized)
   - optional `actions.jsonl` / `snapshots/`
5. Write/update `assets/explore/<app>/<slice>.md` with front-matter
   (`domain/source/date/version/confidence/evidence`) listing:
   - pages visited (url pattern, title)
   - primary actions (button labels)
   - APIs observed (method + path only)
   - blockers / i18n / env notes
6. Stop. Do **not** freeze objects in this skill — tell the caller which run_id to freeze.

## Output checklist

- `run_id` and evidence directory exist.
- Sanitizer applied statement in `run_summary.md`.
- Explore note cites `evidence`.
- Next-step suggestion: freeze / derive-design / author feature.
