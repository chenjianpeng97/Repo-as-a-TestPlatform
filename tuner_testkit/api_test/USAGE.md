## packages.api_test usage (recommended)

### 1) Define an APIModel asset (in `packages/api_objects/**`)

```python
from tuner_testkit.api_test.model import APIModel, AssertOperation, ExtractVariableOperation

login_v1 = APIModel(
    id="svc.POST./auth/login@v1",
    name="登录",
    description="...",
    method="POST",
    path="/auth/login",
    query_schema={},
    body_schema={
        "username": {"type": "string", "required": True},
        "password": {"type": "string", "required": True},
    },
    headers_policy={
        "allowlist": ["Accept", "Content-Type", "Accept-Language", "Content-Language"],
        "forbidden": ["Authorization", "Cookie", "Set-Cookie"],
    },
    auth_policy={"required": False, "strategy": "none", "source": "client.default"},
    asserts=[
        AssertOperation(name="http status", jsonpath="$.http_status", operator="eq", expected=200),
        AssertOperation(name="业务码", jsonpath="$.code", operator="eq", expected=200),
    ],
    extracts=[
        ExtractVariableOperation(name="token", jsonpath="$.data.token", variable_name="token"),
    ],
)
```

### 2) Invoke with set*\* / override*\* then execute()

```python
resp = (
    login_v1
    .set_json({"username": "userA", "password": "******"})
    .execute()
)

token = resp.extracted["token"]
```

### 3) `body_format`: JSON vs form-urlencoded vs multipart

Post/Put 默认 **`body_format="json"`**。当捕获显示 **`Content-Type: application/x-www-form-urlencoded`** 时，在 `APIModel` 上设置 **`body_format="form"`**；仍通过 **`set_json({...})`** 传字段，客户端会改为 `data=` 发送。

```python
export_v1 = APIModel(
    ...,
    method="POST",
    path="/api/export",
    body_schema={...},
    body_format="form",
    ...
)
```

```python
resp = export_v1.set_json({"pageNum": 1, "pageSize": 10}).execute(auth={"bearer_token": token})
```

Excel 导入等 **`multipart/form-data`** 使用 **`body_format="multipart"`** + **`files_schema`**：文本字段仍 `set_json`，文件字段用 `set_files`（路径或 bytes；**不要**写进资产源码）。

```python
import_v1 = APIModel(
    ...,
    method="POST",
    path="/prod-api/inout/import",
    body_schema={"bizType": {"type": "string", "required": False}},
    files_schema={"file": {"type": "file", "required": True}},
    body_format="multipart",
    ...
)

resp = (
    import_v1
    .set_json({"bizType": "1"})
    .set_files({"file": "testdata/sample.xlsx"})
    .execute(auth={"bearer_token": token})
)
```

### 4) Non-JSON and binary responses (`content`)

Every `ApiResponse` includes **`content: bytes`** — the raw HTTP body. For JSON APIs, `json` is populated; for file downloads (xlsx, pdf, …), `json` is often `None` and the bytes are in **`content`**.

- Assert in the `APIModel` only on **`$.http_status`** (and `$.code` if the server returns JSON).
- In steps, parse Excel with **`tuner_testkit.excel`** (e.g. `ExcelWorkbook.from_bytes(resp.content)` or `first_sheet_rows(resp.content)`), not in `packages/api_objects/`.

```python
from tuner_testkit.excel import ExcelWorkbook, first_sheet_rows

resp = some_export_v1.set_json({...}).execute(auth={"bearer_token": token})
rows = first_sheet_rows(resp.content)
```

### 5) Small changes vs rebuild

- **Small changes** (merge-set, can autofill schema for optional keys):

```python
resp = some_model.set_query({"pageNum": 1, "pageSize": 10}).execute(auth={"bearer_token": token})
```

- **Big changes** (override-rebuild, replaces the whole JSON body):

```python
resp = some_model.override_json({"filters": [{"field": "name", "op": "eq", "value": "小红"}]}).execute(auth={"bearer_token": token})
```
