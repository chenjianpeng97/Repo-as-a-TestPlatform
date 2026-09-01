# apps.page_recorder — 手点冻结 Page Object

拉起 headed Playwright 浏览器，人工点击 / 填写 / 浏览时**直播冻结**声明式 `PageModel` 到 `packages/page_objects/`（元素表多候选 + 当前操作流）。对标合录入口 `apps.recorder` 的「抓一条冻一条」（本工具只冻 UI）。不走 `playwright codegen`（后者吐裸 locator，没有 fallback、没有 `{{password}}`、也不过 `locator_policy`）。同一会话还要冻 API Object 请直接用 `python -m apps.recorder`。

## 需求背景

`packages.page_test` 已经把页面资产做成可序列化数据（`LocatorSpec` / `PageFlow` / `Step.to_dict()`），缺的是「浏览器会话 → Capture → merge 源码」这一层。工程师对着真实页面点一遍，就能得到可 `python -m packages.page_test run` 的资产，而不是事后手写定位器。

## 试用场景

**适用**

- 给一个尚未有 Page Object 的页面快速冻出元素表 + 线性 flow（登录、填表、点按钮）。
- 在已有 `PageModel` 上追加候选定位器或补录步骤（并集 merge，不覆盖手写的其它 flow）。
- 用 `--scan` 进页后先收一圈可见的 button / link / textbox，再按需点选补 flow。

**不适用**

- 不能替代 BDD 流水线的 **Playwright MCP Gate 1**（网络证据仍走 MCP capture → freeze-api-objects）。
- 不生成 `if` / `for` / `BasePage` 子类；复杂编排仍手写逃生舱。
- `--scan` 扫不到虚拟列表未滚入视口的节点、canvas、无障碍树为空的控件。
- 不把命中候选自动提升为首选（自愈级别三禁止）。

**前置条件**

- 已装 BDD extra 与 Chromium：`uv sync --extra bdd` 后 `uv run playwright install chromium`
- UI 入口：`--url` 绝对地址，或环境变量 `TEST_UI_BASE_URL` / `TEST_BASE_URL`
- 可选 `--storage-state` 指向已登录的 Playwright `storage_state` JSON（凭据仍不进资产）

## 运行方式

```bash
uv sync --extra bdd
uv run playwright install chromium

uv run python -m apps.page_recorder --app plane --flow login
# 指定入口，并在每个新 URL 扫描可见控件
uv run python -m apps.page_recorder --app plane --flow login --url /sign-in --scan
# 只冻某个 host
uv run python -m apps.page_recorder --app plane --include_host example.com --url https://app.example/sign-in
```

| 参数 | 默认 | 说明 |
| --- | --- | --- |
| `--app` | （必填） | 写入 `id` 与目录 `packages/page_objects/<app>/` |
| `--flow` | `recorded` | 追加到该 flow；已有其它 flow 保留 |
| `--url` | `get_ui_base_url()` | 起始地址；相对路径拼到 UI host |
| `--scan` | 关 | 进入新 URL 后扫描可见交互控件（只扩元素表） |
| `--outputs_dir` | `packages/page_objects` | 资产根目录 |
| `--storage-state` | 空 | 已登录会话 JSON |
| `--include_host` | 空 | host 子串过滤 |

终端 **Ctrl+C** 或关掉浏览器窗口结束。会话结束向 `packages/page_objects/CHANGELOG.md` 追加一行。

## 运行示例

```bash
set TEST_UI_BASE_URL=https://your-env.example
uv run python -m apps.page_recorder --app plane --flow login --url /sign-in --scan
```

预期：

1. 弹出 headed Chromium，打开 `/sign-in`。
2. 输入用户名/密码并点登录。密码当场写成 `{{password}}`，源码与日志都没有真值。
3. 磁盘出现 `packages/page_objects/plane/sign_in.py`（`PageModel` + `__main__` 回放块）。
4. 终端一行：`[page_recorder] merged plane.sign_in@v1 +username_input fill username_input`
5. 结束后 `packages/page_objects/CHANGELOG.md` 多一行 `page_recorder | record-pages`。

回放（凭据走环境变量，见 `packages.page_objects.session`）：

```bash
set TEST_USERNAME=userA
set TEST_PASSWORD=...
uv run python packages/page_objects/plane/sign_in.py
# 或
uv run python -m packages.page_test run plane.sign_in@v1 --flow login --example
```

## 冻成什么

- **元素表**：按 `locator_policy` 排序的多候选（role+name → label → test_id → 短 CSS → 相对 XPath/`fragile`+`note`）。**绝对 XPath 永不写入**。
- **flow**：`Fill` / `Click` / `Check` / `Select` / `Press`；导航补 `WaitForUrl`。连续相同 Click 压成一次；连续 Fill 只留最后一次。
- **按页切资产**：`page.url` 去掉 host 再 `normalize_url_path` → `packages/page_objects/<app>/<page_slug>.py`，`id=<app>.<page_slug>@v1`。
- **脱敏当场做**：`type=password` 与敏感键名 → `{{password}}` / `{{username}}`。
- 只生成声明式 `PageModel`，不生成 `BasePage` 子类。若目标文件已是手写 class，工具 **skip** 以免覆盖。

本工具是**本地维护 CLI**（产物进 git），不加 `@plane_app`。
