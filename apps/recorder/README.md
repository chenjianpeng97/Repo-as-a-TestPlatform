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
```

Defaults:

| Flag | Default |
|------|---------|
| `--outputs_dir` | `<repo>/packages/api_objects` |
| `--listen_host` | `127.0.0.1` |
| `--port` | `8080` |

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
  codegen.py      # APIModel source render
  freeze.py       # create/update route-tree files
  tests/          # app-local unit tests
```

```bash
uv run --with pytest pytest apps/recorder/tests -q
```
