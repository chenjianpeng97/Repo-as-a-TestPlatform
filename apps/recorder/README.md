# apps.recorder — API Object traffic recorder

Terminal HTTP(S) proxy that captures browser/client traffic and **auto-maintains** route-aligned API Objects under `packages/api_objects/` (or a custom `--outputs_dir`), following `docs/spec/api-objects-syntax.md`.

## Install

```bash
pip install -e ".[recorder]"
# or
pip install "mitmproxy>=10"
```

## Run

From the repo root:

```bash
python -m apps.recorder
# custom output root (still expects an api_objects-style tree underneath)
python -m apps.recorder --outputs_dir D:\tmp\api_objects
# only freeze a target host
python -m apps.recorder --include_host example.com --port 8888
# also save FULL response samples for apps.mock_server
python -m apps.recorder --write-mocks
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

Configure the browser (or OS) HTTP/HTTPS proxy to `127.0.0.1:8080`. For HTTPS, install/trust the mitmproxy CA.

## What gets frozen

- Non-static API requests (JSON / form-urlencoded / **multipart upload** / binary download routes)
- Path normalized: numeric segments → `{id}`, UUIDs → `{uuid}`
- Files written as route tree + `<METHOD>.v<MAJOR>.py`, e.g.  
  `packages/api_objects/argon/mainData/getCategoryTree/GET.v1.py`
- Compatible re-hits **merge** into existing v1 (additive schema / stable asserts)
- Secrets never written (`Authorization` / `Cookie` / `*token*` / …)
- Each asset ends with ``if __name__ == "__main__"``：回放录制时的 request，并对 recorded response 做稳定断言
- **Multipart**：只冻结文本字段 + 文件**字段名**（`files_schema`）；**从不**写入文件字节。回放需设置 `TEST_UPLOAD_FILE` 或 `TEST_UPLOAD_FILE_<FIELD>` 指向本地样例文件，否则 `__main__` 会 SKIP

## Replay a single asset（端到端样本回放）

录制后直接运行资产文件即可复现当时那次请求：

```bash
# 鉴权（类似 Postman Environment）——统一维护在 packages/api_objects/auth.py
set TEST_BASE_URL=https://your-env.example
set TEST_BEARER_TOKEN=...          # 或 TEST_USERNAME + TEST_PASSWORD 自动登录

uv run python packages/api_objects/prod-api/bsx/mainReport/auditDistributorList/GET.v1.py
```

- Request / Response 样本写在文件底部的 `_RECORDED_*` 常量中（随 recorder 更新）
- Token / Cookie **不**写入资产；一律从 `packages.api_objects.auth` 注入
- 断言策略：`http_status` + `$.code` + 顶层 key 形状；列表类字段（`rows`/`data`）不做全量相等（易变）

## `--write-mocks`：另存**完整**响应样例

资产里的 `_RECORDED_RESPONSE` 是**故意截断**的（`codegen.truncate_sample`：列表留 5 条 +
`...(+N more)`、嵌套超 6 层塌成 `...`、字符串超 240 字符裁掉），因为 Python 源码要保持可读、可 diff。
但这样的样例喂给 `apps.mock_server` 就只剩 5 行数据和一堆 `null` 空洞。

加上 `--write-mocks` 后，同一次抓包会**额外**把**完整**响应体写成 mock 定义，
与资产同路由树、同 `v<N>` 后缀：

```text
packages/api_objects/prod-api/inout/report/his/queryInoutHis/POST.v1.py    # 截断，给人读
data/mocks/          prod-api/inout/report/his/queryInoutHis/POST.v1.json  # 完整，给 mock server 跑
```

```bash
python -m apps.recorder --write-mocks
# 抓完直接起 mock server 回放真实数据
python -m apps.mock_server serve --port 8931
```

行为要点：

- **只刷新自己那个场景**（默认 `success`）。文件里手工加的 `empty` / `boom` 等场景、
  以及用户切到哪个 `active`，重录都不会被覆盖。
- 想保住手工调过的 `success`，就让 recorder 写别的名字：`--mock-scenario recorded`。
- 响应头**只保留 `Content-Type`**。回放录制来的 `Content-Length` / `Transfer-Encoding`
  会与实际响应体不符，反而把客户端搞坏。
- 超过 `--mock-max-bytes` 的响应跳过并计入 `mocks_skipped`，避免把巨型响应写进仓库。
- 脱敏与资产**同一套**（`sanitize.py` 在 `build_capture` 阶段就已掩码），不会因为存全量而泄漏凭证。
  但它确实比资产多留**很多行真实业务数据**，请按对待抓包产物的标准对待 `data/mocks/`。
- mock 写失败不会影响冻结资产（异常被吞掉并计数，代理继续跑）。

没开这个开关时，recorder 的行为与以前完全一致。
若已经录过但当时没开，可以用 `python -m apps.mock_server seed` 从截断样例补一份骨架（数据不全）。

## What is skipped

- **`.js` / `.css`** (and `.mjs` / `.cjs`) — hard requirement
- Other static blobs (images, fonts, source maps, media)
- `OPTIONS` / `HEAD` / `CONNECT`
- HTML document GETs (SPA shells)

## Layout

```text
apps/recorder/
  cli.py          # argparse + mitmdump runner
  addon.py        # mitmproxy response hook
  capture.py      # sanitize + structure one exchange
  normalize.py    # path / fingerprint / static filter
  sanitize.py     # header/body secret scrubbing
  codegen.py      # APIModel source render (truncates samples)
  freeze.py       # create/update route-tree files
  mocks.py        # --write-mocks: full samples -> data/mocks (apps.mock_server)
  tests/          # app-local unit tests
```

```bash
uv run --with pytest pytest apps/recorder/tests -q
```
