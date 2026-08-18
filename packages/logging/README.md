# packages.logging

A small, dependency-free logging toolkit for test automation and CLI tools.
Drop it into any project's `packages/` folder and you get:

- One time-stamped log file per process (`logs/<entrypoint>-YYYYMMDD-HHMMSS.log`)
- Optional **feature / scenario / step** boundary lines (when wired via behave hooks)
- A consistent, greppable line format tagged with **stage / scope / kind**
- Semantic helpers: `log_data_setup`, `log_api_call`, `log_ui_action`, `log_assertion`
- Optional **per-scenario** log file for easy handoff when a single test fails
- Safe on Windows GBK consoles (files are UTF-8; the hooks don't touch stdout)

The package depends on nothing outside the Python stdlib. It does not import
`behave`, `playwright`, or `requests`, so it is trivially portable.

---

## 1. Install

Copy the whole folder into your project:

```
your-project/
  packages/
    logging/           # <-- drop the whole package here
      __init__.py
      core.py
      context.py
      hooks.py
      helpers.py
      scenario_file.py
```

That's it — no `pip install`, no transitive deps.

> The package is named `logging`. In Python 3 absolute imports are the
> default, so internal `import logging` still resolves to the stdlib. The
> only rule: always import the kit by its full path,
> `from packages.logging import ...`.

---

## 2. Wire into behave (optional, 10 lines)

Add the imports and call the hooks from your `environment.py`
(or your per-stage `<stage>_environment.py`):

```python
# tests/features/ui_environment.py  (or api_environment.py)
from packages.logging import hooks as log_hooks

def before_all(context):        log_hooks.on_run_begin(context)
def after_all(context):         log_hooks.on_run_end(context)
def before_feature(ctx, f):     log_hooks.on_feature_begin(ctx, f)
def after_feature(ctx, f):      log_hooks.on_feature_end(ctx, f)
def before_scenario(ctx, s):    log_hooks.on_scenario_begin(ctx, s)
def after_scenario(ctx, s):     log_hooks.on_scenario_end(ctx, s)
def before_step(ctx, st):       log_hooks.on_step_begin(ctx, st)
def after_step(ctx, st):        log_hooks.on_step_end(ctx, st)
```

`stage` is read from `context.config.stage` (i.e. the
`behave --stage=ui|api|...` CLI flag). No extra userdata section is required.

For **pytest** or plain scripts, skip the hooks and just call the helpers
(or `get_logger()`). The log filename stem defaults to the entry-point name
(`pytest-...`, `dump_ddl-...`, `behave-...`).

---

## 3. Use inside steps / scripts

```python
from packages.logging import (
    log_data_setup, log_api_call, log_assertion, log_warn,
)

log_data_setup("seed_users", count=len(users),
               sample=[u.name for u in users[:3]])

resp = client.get("/api/v1/items", params={"page": 1})
log_api_call("GET", "/api/v1/items",
             status=resp.status_code, total=resp.json()["total"], page=1)

log_assertion("count_equal",
              expected=expected, actual=resp.json()["total"],
              passed=(expected == resp.json()["total"]))
```

There is exactly one log line per helper call; formatting and level are
chosen for you (`log_assertion` emits `ERROR` when `passed=False`, `INFO`
otherwise — so `grep 'ASSERT.*FAIL'` surfaces every failed check).

---

## 4. Log line format

```
YYYY-MM-DD HH:MM:SS.mmm LEVEL [stage] [feature::scenario] [kind   ] message
```

Example excerpt (one scenario, API stage):

```
2026-04-22 13:57:01.213 INFO  [api] [订单查询::按状态筛选]           [RUN-BGN] run started stage=api log_file=... argv=behave --stage=api ...
2026-04-22 13:57:01.213 INFO  [api] [订单查询]                        [FEA-BGN] feature begin tags=@regression
2026-04-22 13:57:01.214 INFO  [api] [订单查询::按状态筛选]           [SCE-BGN] scenario begin tags=-
2026-04-22 13:57:01.214 INFO  [api] [订单查询::按状态筛选]           [STP-BGN] Given 测试库中存在若干订单
2026-04-22 13:57:01.214 INFO  [api] [订单查询::按状态筛选]           [DATA   ] prepared seed_orders count=12 sample=['ORD-1', ...]
2026-04-22 13:57:01.322 INFO  [api] [订单查询::按状态筛选]           [STP-END] status=passed duration=0.108s
2026-04-22 13:57:01.322 INFO  [api] [订单查询::按状态筛选]           [STP-BGN] When 按状态查询订单列表
2026-04-22 13:57:02.885 INFO  [api] [订单查询::按状态筛选]           [API    ] GET /api/v1/orders -> 200 total=12 page=1
2026-04-22 13:57:02.886 INFO  [api] [订单查询::按状态筛选]           [ASSERT ] count_equal expected=12 actual=12 -> PASS
```

`kind` takes one of:

| Lifecycle     | Activity  | Level-generic |
|---------------|-----------|---------------|
| `RUN-BGN/END` | `DATA`    | `INFO`        |
| `FEA-BGN/END` | `API`     | `WARN`        |
| `SCE-BGN/END` | `UI`      | `ERROR`       |
| `STP-BGN/END` | `ASSERT`  |               |

---

## 5. Environment variables

All knobs default to sensible values; you only change them when needed.

| Variable                 | Default                         | Purpose                                                         |
|--------------------------|---------------------------------|-----------------------------------------------------------------|
| `TEST_LOG_DIR`           | `logs`                          | Output directory (resolved relative to the working directory)   |
| `TEST_LOG_NAME`          | *(entry-point stem, else `run`)* | Main-log filename stem                                         |
| `TEST_LOG_LEVEL`         | `INFO`                          | Threshold (`DEBUG/INFO/WARNING/ERROR`)                          |
| `TEST_LOG_PER_SCENARIO`  | `0`                             | `1` adds a per-scenario file under `logs/scenarios/`            |
| `TEST_LOG_ECHO_ERRORS`   | `1`                             | `1` mirrors `ERROR+` records to stderr as well                  |
| `TEST_LOG_CAPTURE_ROOT`  | `0`                             | `1` also captures stdlib `root` logger records (3rd-party libs) |

Example run:

```powershell
$env:TEST_LOG_PER_SCENARIO = "1"
$env:TEST_LOG_LEVEL = "DEBUG"
behave --stage=api tests/features/example.feature
```

Force a custom stem (optional):

```powershell
$env:TEST_LOG_NAME = "nightly-regression"
```

---

## 6. FAQ

**Q: Why not use `behave --logging-level` / `--logcapture`?**  
Behave's capture is a good debugging aid (dumps captured logs on failure), but
it writes to stdout/stderr only and offers no per-feature/scenario/step
structure. This kit is additive: the shared logger sets `propagate=False`, so
behave's capture is untouched — you can use both.

**Q: Does it conflict with `logging.getLogger(__name__)` elsewhere?**  
No. The kit uses a dedicated `packages.logging` logger with `propagate=False`.
Third-party libraries that log via the stdlib `root` remain isolated. Set
`TEST_LOG_CAPTURE_ROOT=1` if you explicitly want to pull them into the file.

**Q: Windows console shows `?` instead of Chinese characters.**  
The on-disk file is UTF-8 already. Console rendering is a separate concern —
wire UTF-8 stdio in your host entrypoint if needed.

**Q: Can I use it without behave?**  
Yes — just import `get_logger()` / the helpers. The `hooks` submodule is the
only part that assumes behave-shaped objects (feature/scenario/step), and
even there only `getattr(...)` is used, never a `behave` import. The default
log filename follows the process entry point (`dump_ddl-...`, `pytest-...`).

**Q: How do I rotate/archive old log files?**  
Out of scope. Treat `logs/` as ephemeral CI artefact — archive via your CI
system, or add a standalone cleanup script. The kit intentionally does not
ship a rotating handler so the file boundary stays aligned with a single run.

---

## 7. Public API reference

```python
from packages.logging import (
    # lazy run-scope logger
    get_logger,
    get_log_file_path,
    log_dir,

    # semantic helpers
    log_data_setup,   # log_data_setup("seed_users", count=12)
    log_api_call,     # log_api_call("GET", "/path", status=200, total=100)
    log_ui_action,    # log_ui_action("click", target="登录按钮")
    log_assertion,    # log_assertion("count_equal", expected=1, actual=2, passed=False)

    # free-form fallbacks
    log_info, log_warn, log_error,
)

from packages.logging import hooks as log_hooks  # behave environments only
#   log_hooks.on_run_begin(context)
#   log_hooks.on_run_end(context)
#   log_hooks.on_feature_begin(context, feature)
#   log_hooks.on_feature_end(context, feature)
#   log_hooks.on_scenario_begin(context, scenario)
#   log_hooks.on_scenario_end(context, scenario)
#   log_hooks.on_step_begin(context, step)
#   log_hooks.on_step_end(context, step)
```
