---
name: freeze-api-objects
version: 1.0.0
description: Freezes sanitized Playwright MCP network captures into route-aligned, deduped API Objects under packages/api_objects/ following api-objects-syntax.md and bdd-run-gherkin-in-playwrightMCP.md. Use when creating/updating APIModel assets.
---

# Freeze Captures → API Objects (route-aligned)

## Scope

- **Primary goal**: convert sanitized captures into reusable APIModel assets.
- **Write scope**: `packages/api_objects/**` only.
- **Must follow**:
  - `api-objects-syntax.md`
  - `bdd-run-gherkin-in-playwrightMCP.md`

## Hard rules (security & structure)

- **Never** persist real credentials or sensitive headers/values (Authorization/Cookie/_token_/_secret_/_password_/_session_).
- API Object **must be route-aligned**: one asset per `method + normalized_path` (unless version bump required).
- Steps must not craft requests; they must call API Objects.
- `path` must not include host.

## Hard requirement (pipeline gate)

- If a sanitized capture contains at least one eligible non-static route, you **must**:
  - dedupe/match existing assets
  - write/update `packages/api_objects/**` accordingly
  - report the created/updated assets list (method/path → file path)
- If you create **zero** API Objects, you **must** explicitly justify it in the output (e.g. capture had no eligible routes, blocked before login, all requests were static).

## Dedupe / match workflow

- Normalize path (dynamic segments → `{id}`/`{uuid}` per framework rule).
- Compute fingerprint:
  - method + normalized_path + sorted(query_keys) + sorted(body_keys) [+ files:<sorted file keys>]
- **Before creating** a new asset, search existing `packages/api_objects/**` for matching route/fingerprint intent.
- If compatible: update v1 (only additive/compatible changes).
- If incompatible: do not auto-create v2 silently; output “建议升 v2”的结论 and create v2 only when explicitly required by task.

## What to write into APIModel

- Identity (stable): id/name/description/method/path
- Contract (weak schema ok):
  - query_schema/body_schema (keys + type hint + required?)
  - response_hints for stable asserts/extracts
  - **`body_format`**:
    - **`"json"`**（默认）for JSON bodies
    - **`"form"`** when capture shows `Content-Type: application/x-www-form-urlencoded`
    - **`"multipart"`** when capture shows `Content-Type: multipart/form-data` (Excel import etc.)
  - **`files_schema`** (multipart only): file **field names** only — never file bytes or absolute paths. Text companions stay in `body_schema` / `set_json`.
  - headers_policy allowlist + forbidden
  - auth_policy (runtime injection only)
- Operations:
  - asserts: stable only (http status, $.code, key exists)
  - extracts: stable, named variables (avoid polluting global context)

### Multipart / Excel upload requests

- Freeze text parts → `body_schema`; file parts (have `filename`) → `files_schema`.
- Callers use `.set_json({...}).set_files({"file": "testdata/sample.xlsx"}).execute(...)`.
- Do **not** commit upload fixtures' secrets; sample files for local replay belong outside api_objects (or under clearly non-secret testdata).

### Binary / non-JSON responses (Excel, PDF, file streams)

- `tuner_testkit.api_test` stores the raw body on **`ApiResponse.content`** (bytes) for every call; `json` is set only when the body parses as JSON.
- For download routes, **assert HTTP success only** in the asset (e.g. `AssertOperation` on `$.http_status == 200`). Do **not** assert on `Content-Disposition` filenames, body length, or sheet row counts — those are scenario-specific and brittle.
- **Do not** rely on `extracts` with `jsonpath: $.data.*` when the response is not JSON; document in `description` that consumers read **`resp.content`** after `execute()`. Parsing xlsx/CSV belongs in **`tuner_testkit.excel`** (`ExcelWorkbook.from_bytes`, `first_sheet_rows`, etc.), not inside `packages/api_objects/`.

## Audit checklist (must pass)

- No forbidden header keys or raw tokens in file content.
- No host in APIModel path/url.
- No scenario-specific constants asserted in APIModel.
- File path follows route-tree naming and versioning: `<METHOD>.v<MAJOR>.py`.
