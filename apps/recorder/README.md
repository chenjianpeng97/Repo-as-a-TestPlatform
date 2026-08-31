# apps.recorder — headed 合录（PageObject + APIObject）

拉起 headed Playwright 浏览器，人工点击 / 填写 / 浏览时**默认同时冻结**：

- `PageModel` → `packages/page_objects/`（元素表多候选 + 当前操作流）
- `APIModel` → `packages/api_objects/`（路由树；Playwright `page.on("response")`）

不走 `playwright codegen`，不合入 mitmproxy。非浏览器客户端请用
`python -m apps.api_recorder`。

**不是** BDD Gate 1：MCP 网络证据规则不变。本地 Playwright 不能替代 MCP capture。

## 需求背景

`apps.page_recorder` 只冻 UI，`apps.api_recorder` 只冻代理流量。人工对着真实页面点一遍时，
XHR 与 DOM 本来就在同一会话里，合录避免开两个工具、两套会话。

## 试用场景

**适用**

- 给尚未有 Page / API Object 的流程快速冻出元素表 + 接口资产（登录、填表）。
- 只要 UI：`--page-only`（等价于只跑 page_recorder 的冻结侧）。
- 只要 API：`--api-only`（仍开 headed 浏览器，不写 PageModel）。

**不适用**

- 不能替代 BDD 流水线的 **Playwright MCP Gate 1**。
- 不抓非浏览器 HTTP 客户端（用 `apps.api_recorder`）。
- 不把命中 locator 自动提升为首选；不自动把 XHR 写成 `WaitForResponse` step。

**前置条件**

- `uv sync --extra bdd` 后 `uv run playwright install chromium`
- UI 入口：`--url` 绝对地址，或 `TEST_UI_BASE_URL` / `TEST_BASE_URL`
- 可选 `--storage-state`（凭据仍不进资产）

## 运行方式

```bash
uv sync --extra bdd
uv run playwright install chromium

uv run python -m apps.recorder --app plane --flow login --url /sign-in --scan
# 只要 UI / 只要 API
uv run python -m apps.recorder --app plane --url /sign-in --page-only
uv run python -m apps.recorder --app plane --url /sign-in --api-only
# API 侧同时写完整 mock
uv run python -m apps.recorder --app plane --url /sign-in --write-mocks
```

旧命令 `python -m apps.recorder --port 8080` **不会**静默转去代理，会报错并提示改用
`python -m apps.api_recorder`。

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--app` | （必填） | PageModel 目录 `packages/page_objects/<app>/` |
| `--flow` | `recorded` | 写入的 page flow 名 |
| `--url` | `get_ui_base_url()` | 起始地址 |
| `--scan` | 关 | 进页扫描可见控件（仅冻 page 时生效） |
| `--outputs_dir` | `packages/page_objects` | Page Objects 根目录 |
| `--api-outputs-dir` | `packages/api_objects` | API Objects 根目录 |
| `--page-only` / `--api-only` | 关（双冻） | 互斥；只关一边 |
| `--write-mocks` | 关 | 仅 API 开启时把完整响应写入 `data/mocks` |
| `--storage-state` | 空 | 已登录会话 JSON |
| `--include_host` | 空 | 页面与 API 共用的 host 子串过滤 |

终端 **Ctrl+C** 或关掉浏览器窗口结束。

- page 有改动 → `packages/page_objects/CHANGELOG.md`
- api 有改动 → `packages/api_objects/CHANGELOG.md`

## 实现

薄封装，不复制 harvest/freeze：

- UI：`apps.page_recorder.PageRecorderSession`（`on_page_ready` 挂 tap）
- API：`apps.api_recorder.PlaywrightApiTap` → `packages.api_objects.recording`
- tap 回调内禁止 `page.evaluate`（避免与 `expose_binding` 死锁）；可读 `response.body()`

```bash
uv run --extra test pytest apps/recorder/tests -q
uv run python -m apps.recorder --help
```
