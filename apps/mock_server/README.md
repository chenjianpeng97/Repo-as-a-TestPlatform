# mock_server

用 `packages/api_objects` 的路由资产 + `data/mocks/**.json` 的响应定义起一个
**可在运行时改返回值**的 mock HTTP 服务，并对外暴露控制面供测试平台调用。

## 需求背景

`APIModel` 只描述**请求契约**（method / path / query / body / auth）与稳定断言；
它的 `response_hints` 由 `packages.api_objects.recording` 生成，只有顶层键名，**没有响应体、状态码、响应头**，
所以无法直接拿资产当 mock 用。另一方面，被测后端不可用（环境挂了、接口还没开发完、
要造 500 / 超时 / 空列表等异常分支）时，UI 与 API 用例就跑不动。

本工具把「响应契约」外置到 `data/mocks/`，与资产**一一对照**但互不侵入：

```
packages/api_objects/prod-api/inout/report/his/queryInoutHis/POST.v1.py   # 请求契约
data/mocks/          prod-api/inout/report/his/queryInoutHis/POST.v1.json # 响应场景
```

`packages/api_test` 一行未改。消费侧也零改动——资产的 `path` 不含 host，
`get_test_base_url()` 从 `TEST_BASE_URL` 读，所以把该环境变量指向 mock server
即可让全部既有 APIModel 打到 mock。

## 试用场景

**适用**

- 后端未就绪 / 环境不稳，但要先把 UI、API 用例跑通。
- 构造真实环境难复现的分支：500、业务码非 200、空列表、慢响应。
- 测试平台（Plane）拉起本仓后，由页面定义某接口这次返回什么。
- 给 `packages/api_test` 自身做回归时，需要一个确定性的对端。

**不适用**

- 验证后端真实行为（那要连真环境）。
- 性能压测（uvicorn 单进程，且响应是静态回放）。
- 当作契约测试工具：这里不校验请求是否符合 `body_schema`，只按 method+path 回放。

**前置条件**

- 需要 `mock` extra：`uv sync --extra mock`（fastapi + uvicorn + httpx）。
- `seed` 需要仓库里已有冻结资产；没有资产也能用，直接用控制面凭空定义路由即可。

## 运行方式

```bash
uv sync --extra mock

# 1) 拿到 mock 定义，二选一：
#    a. 边抓包边存【完整】响应（推荐，数据最全）
python -m apps.api_recorder --write-mocks
#    或合录：python -m apps.recorder --app <app> --write-mocks
#    b. 从已冻结资产的【截断】样例补骨架
python -m apps.mock_server seed --dry-run     # 先看会写什么
python -m apps.mock_server seed

# 2) 起服务
python -m apps.mock_server serve --port 8931

# 3) 让既有用例打到 mock（PowerShell）
$env:TEST_BASE_URL = "http://127.0.0.1:8931"
```

两条来源写的是同一份 `data/mocks/**.json`、同一个 `success` 场景，可以混用：
先 `seed` 铺骨架，之后哪条路由抓到了真流量，`--write-mocks` 就把它刷成完整数据。

查看当前状态：

```bash
python -m apps.mock_server routes            # 资产 + mock 定义对照表
python -m apps.mock_server routes --json
```

`serve` 参数：`--host` `--port` `--mocks-dir` `--admin-prefix`
`--no-assets`（只服务 `data/mocks`，跳过资产扫描）`--max-request-log` `--log-level`。

## 运行示例

```bash
python -m apps.mock_server serve --port 8931
```

预期输出：

```
api_mock serving on http://127.0.0.1:8931
  control plane : http://127.0.0.1:8931/__mock__/routes
  openapi docs  : http://127.0.0.1:8931/__mock__/docs
  definitions   : C:\dev\repo\innovamed-test-template\data\mocks
  point tests at it with TEST_BASE_URL=http://127.0.0.1:8931
```

运行时改一个接口的返回值（这就是平台页面背后的调用）：

```bash
curl -X PUT http://127.0.0.1:8931/__mock__/scenario \
  -H "Content-Type: application/json" \
  -d '{
        "method": "POST",
        "path": "/prod-api/inout/report/his/queryInoutHis",
        "scenario": "empty",
        "activate": true,
        "response": {"status": 200, "body": {"code": 200, "data": {"total": 0, "list": []}}}
      }'
```

切回原场景、把改动落盘：

```bash
curl -X PUT  http://127.0.0.1:8931/__mock__/active \
  -H "Content-Type: application/json" \
  -d '{"method":"POST","path":"/prod-api/inout/report/his/queryInoutHis","scenario":"success"}'

curl -X POST http://127.0.0.1:8931/__mock__/persist -H "Content-Type: application/json" -d '{}'
```

产出位置：`data/mocks/<路由树>/<METHOD>.v<N>.json`。

## 控制面 API

统一挂在 `--admin-prefix`（默认 `/__mock__`）下；交互式文档在 `{prefix}/docs`。
路由用 **`method` + `path`** 定位，不做 slug 编码，避免 path 里的 `/` 和 `{id}` 被转义。

| 端点 | 用途 |
| --- | --- |
| `GET {prefix}/health` | 存活 + 路由数 / 待落盘改动数 |
| `GET {prefix}/routes` | 全部路由：资产契约 + 是否有 mock + 当前场景（平台列表数据源） |
| `GET {prefix}/routes/detail?method=&path=` | 单路由全部场景的完整定义 |
| `PUT {prefix}/active` | 切换激活场景 |
| `PUT {prefix}/scenario` | **定义/覆盖某场景的返回值**（status / headers / body / delay_ms） |
| `DELETE {prefix}/scenario?method=&path=&scenario=` | 删除场景（不允许删到一个不剩） |
| `POST {prefix}/persist` | 把内存改动写进 `data/mocks`（不传参=全部；传 method+path=单条） |
| `POST {prefix}/reset?reload=true` | 丢弃内存改动，可选重读磁盘 |
| `GET {prefix}/requests?limit=` | 最近收到的请求留痕（已脱敏），可断言调用次数与入参 |
| `DELETE {prefix}/requests` | 清空留痕 |

**改动默认只在内存**，必须显式 `persist` 才写盘。这样 Plane Runner 在容器里改返回值
不会污染 checkout（与 `apps/index_platform` 的「不写 git」一致）。

## mock 定义格式

```json
{
  "method": "POST",
  "path": "/prod-api/inout/report/his/queryInoutHis",
  "id": "prod-api.POST./prod-api/inout/report/his/queryInoutHis@v1",
  "version": 1,
  "active": "success",
  "scenarios": {
    "success": {
      "status": 200,
      "headers": { "Content-Type": "application/json" },
      "body": { "code": 200, "message": "SUCCESS", "data": { "total": 91, "list": [] } },
      "delay_ms": 0
    },
    "empty":  { "status": 200, "body": { "code": 200, "data": { "total": 0, "list": [] } } },
    "boom":   { "status": 500, "body": { "code": 500, "message": "mocked failure" } }
  }
}
```

- `body` 为 dict / list → JSON 响应；为字符串 → 原样文本；为 `null` → 空响应体。
- `path` 支持 `{id}` / `{uuid}` 动态段，语义与 `packages.api_objects.recording.normalize_path` 一致。
  字面路由优先于占位路由，`/users/me` 不会被 `/users/{id}` 抢走。
- 未定义的路由返回 **501** 并说明如何定义，不会静默返回 200。

## 两种数据来源

| 来源 | 命令 | 数据完整度 |
| --- | --- | --- |
| **recorder 直存**（推荐） | `python -m apps.api_recorder --write-mocks` 或合录 `--write-mocks` | **完整**：全部行、全部层级、长字符串不裁 |
| **从资产 seed**（兜底） | `python -m apps.mock_server seed` | 截断：5 行 / 6 层 / 240 字符 |

`seed` 用 `ast` 读资产 `__main__` 块里的 `_RECORDED_RESPONSE`（函数局部变量，import 拿不到），
剥掉截断标记后落盘；没有录制样例的资产则用 `response_hints.top_level_keys` 生成 `{key: null}`
占位，保证每条路由在控制面里可见。两者写同一份文件、同一个 `success` 场景，可以先 seed 铺骨架，
之后对能重抓的路由用 `--write-mocks` 刷成完整数据。

## 已知限制

- **seed 路径拿到的 body 是残缺的**（recorder 写资产时 `truncate_sample` 丢掉的数据无法还原）。
  要完整数据就重新抓一次并加 `--write-mocks`。
- 不做请求校验：不检查请求是否符合资产的 `body_schema` / `headers_policy`。
- 不做真实后端透传（record-and-replay 代理）。
- `data/mocks/` 不在 `apps/init_repo` 的 `PLATFORM_PATHS` 里 —— mock 数据是项目资产，
  不随平台 DNA 分发；`packages/api_mock` 与本工具会分发。

## 安全

- 落盘时会扫描疑似凭证（`authorization` / `cookie` / `token` / `secret` / `password` /
  `session` 形状的 header 名与 body 键），命中且值不是 `***` 这类占位符时写 WARN 日志。
  **不要把真实 token 写进 mock 定义**——`data/mocks/` 会进 git。
- 请求留痕对敏感 header 做掩码，body 只记键名不记内容。
