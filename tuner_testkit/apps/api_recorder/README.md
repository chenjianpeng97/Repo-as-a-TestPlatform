# apps.api_recorder — API Object HTTP(S) 代理抓包

终端 HTTP(S) 代理，捕获浏览器/客户端流量并**自动维护**路由对齐的 API Objects
（`packages/api_objects/`，或自定义 `--outputs_dir`），规范见
`docs/spec/api-objects-syntax.md`。

**只抓 HTTP(S) 代理流量，不含 UI 元素表。** 同一 headed 会话里同时冻 PageObject
与 APIObject 请用 `python -m tuner_testkit.apps.recorder`。

冻结内核在 `tuner_testkit.api_objects.recording`（离线可测，不含 mitmproxy / Playwright）。

## 需求背景

非浏览器客户端（脚本、移动端、其它进程）的流量走系统/进程代理才能看见；合录入口
`apps.recorder` 只听 Playwright `response` 事件。本工具保留 mitmproxy 适配层。

## 试用场景

**适用**：需要抓非 Playwright 浏览器流量，或尚未开 headed 合录时单独冻 API。

**不适用**：人工点填同时要冻页面元素（用 `apps.recorder`）；BDD Gate 1 的网络证据
仍须 Playwright MCP，本工具不能替代。

## Install

```bash
pip install -e ".[recorder]"
# extra 名仍叫 recorder（mitmproxy），避免 lock 大改
# or
pip install "mitmproxy>=10"
```

## Run

从仓库根：

```bash
python -m tuner_testkit.apps.api_recorder
python -m tuner_testkit.apps.api_recorder --outputs_dir D:\tmp\api_objects
python -m tuner_testkit.apps.api_recorder --include_host example.com --port 8888
python -m tuner_testkit.apps.api_recorder --write-mocks
```

Defaults:

| Flag | Default |
|------|---------|
| `--outputs_dir` | `<repo>/packages/api_objects` |
| `--listen_host` | `127.0.0.1` |
| `--port` | `8080` |
| `--write-mocks` | off |
| `--mocks-dir` | `<repo>/data/mocks` |
| `--mock-scenario` | `success` |
| `--mock-max-bytes` | `1048576` (1 MiB; `0` disables) |

把浏览器（或系统）HTTP/HTTPS 代理指到 `127.0.0.1:8080`。HTTPS 需信任 mitmproxy CA。

结束时若冻过路由，向 `packages/api_objects/CHANGELOG.md` 追加一行。

## What gets frozen

- Non-static API requests (JSON / form-urlencoded / **multipart upload** / binary download routes)
- Path normalized: numeric segments → `{id}`, UUIDs → `{uuid}`
- Files written as route tree + `<METHOD>.v<MAJOR>.py`
- Compatible re-hits **merge** into existing v1 (additive schema / stable asserts)
- Secrets never written (`Authorization` / `Cookie` / `*token*` / …)
- Each asset ends with ``if __name__ == "__main__"``：回放录制时的 request
- **Multipart**：只冻结文本字段 + 文件**字段名**（`files_schema`）；**从不**写入文件字节

## `--write-mocks`

资产里的 `_RECORDED_RESPONSE` 故意截断。加上 `--write-mocks` 会把**完整**响应体
写成 mock 定义，供 `apps.mock_server` 回放。

```bash
python -m tuner_testkit.apps.api_recorder --write-mocks
python -m tuner_testkit.apps.mock_server serve --port 8931
```

合录入口同样支持 `--write-mocks`：`python -m tuner_testkit.apps.recorder --app <app> --write-mocks`。

## What is skipped

- **`.js` / `.css`**（以及 `.mjs` / `.cjs`）
- Other static blobs (images, fonts, source maps, media)
- `OPTIONS` / `HEAD` / `CONNECT`
- HTML document GETs (SPA shells)

## Layout

```text
tuner_testkit/apps/api_recorder/
  cli.py            # argparse + mitmdump runner
  addon.py          # mitmproxy response hook
  playwright_tap.py # Playwright page.on("response")（给合录复用）
  tests/            # fake flow / 过滤（不启真实代理）

packages/api_objects/recording/
  capture.py / normalize.py / sanitize.py / codegen.py / freeze.py / mocks.py / pipeline.py
```

```bash
uv run --extra test pytest packages/tests/test_api_objects_recording_*.py tuner_testkit/apps/api_recorder/tests -q
```
