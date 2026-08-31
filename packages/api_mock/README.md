# packages.api_mock

把 `packages/api_objects` 的 `APIModel` 资产变成一个可运行、可在运行时改返回值的
mock HTTP 服务。工具入口与完整使用说明见 [`apps/mock_server/README.md`](../../apps/mock_server/README.md)；
本文件只讲**这个组件包的分层与 API**。

## 为什么响应定义在包外

`APIModel` 描述的是**请求契约 + 稳定断言**：

- `response_hints` 由 `apps.recorder.codegen.build_response_hints` 生成，只有
  `{"top_level_keys": [...]}`，没有值、类型、状态码、响应头。
- 状态码只能从 `asserts` 里的 `$.http_status` 反解，但那是**断言**不是响应契约，
  反向依赖会让「改 mock」变成「改断言」。
- 真实样例 `_RECORDED_RESPONSE` 在资产文件的 `if __name__ == "__main__":` 块里，
  是函数局部变量，import 拿不到。

所以响应契约外置到 `data/mocks/**.json`，与资产按路由树一一对照。
**`packages/api_test` 一行未改**，recorder 也不用改。

## 三层

| 层 | 位置 | 职责 |
| --- | --- | --- |
| 定义 | `spec.py` — `RouteMock` / `ResponseSpec` | 一个 `method + path` 的全部场景，pydantic 校验 + JSON 序列化 |
| 状态 | `store.py` — `MockStore` | 磁盘基线 + 内存覆盖层；`persist()` 才落盘 |
| 服务 | `app.py` — `create_app()` | FastAPI：控制面先注册，catch-all 后注册 |

辅助：`router.py`（`{id}` / `{uuid}` 路径匹配）、`errors.py`（异常层次，风格对齐
`packages/api_test/errors.py`）。

资产枚举不在本包，在 [`packages/api_objects/registry.py`](../api_objects/registry.py) 的
`iter_api_models()` —— 它是 api_objects 层的通用能力。

## 用法

```python
from packages.api_mock import MockStore, ResponseSpec, create_app

store = MockStore("data/mocks")
app = create_app(store=store)           # 需要 mock extra
```

不装 `mock` extra 时，`import packages.api_mock` 依然可用（`create_app` 是
PEP 562 惰性导出），所以 `spec` / `store` / `router` 可以被普通单测直接引用。

纯内存构造，不碰磁盘：

```python
from packages.api_mock import MockStore, ResponseSpec

store = MockStore(tmp_path)
store.upsert_scenario(
    "POST", "/api/items", "empty",
    ResponseSpec(status=200, body={"code": 200, "data": []}),
    activate=True,
)
store.persist()                          # 显式落盘
```

## 边界

- 不校验请求是否符合资产的 `body_schema` / `headers_policy`（那是 `packages.api_test` 的事）。
- 不发真实请求、不连数据库；`create_app` 之外没有 IO。
- 日志走 `packages.logging`，落盘前会对疑似凭证字段告警（见 `spec.scan_sensitive`）。
