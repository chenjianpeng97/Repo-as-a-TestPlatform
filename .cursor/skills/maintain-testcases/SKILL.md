---
name: maintain-testcases
version: 1.3.0
description: Creates and updates functional testcases so each case is its own Markdown file under assets/testcases/<module>/<suite>/<Case-ID>.md, with suite notes in that folder's README. Uses a TestLink-style template (summary, preconditions, numbered steps, expected results, status). Use when the user asks to 编写/生成/维护测试用例, add a module or suite, or mentions assets/testcases or a case ID. Do not use for testdesign click-paths or behave .feature files.
---

# Maintain testcases

## Scope

- **Write**: `assets/testcases/**` only.
- **Must follow**: `docs/spec/testcase-syntax.md`.
- **Out of scope**: `assets/testdesign/`（用 `derive-test-design`）、`tests/features/**`（用 `feature-authoring`）、pytest。

## Before writing

1. 读 `assets/testcases/README.md`、目标模块的 `README.md`、目标套件的 `README.md`（没有就先按下面的模板建）。
2. 读 `INDEX.md`；存在 `INDEX.project.md` 时一并读。只采用已有 usecase / domain-notes / explore / design，或用户本次给出的事实。
3. 套件 README 已有 `id_prefix` 就沿用，不要另起缩写。新建套件时用套件名的英文词，每词首字母大写、`-` 连接（`用户登录` → `User-Login`）。确认这个前缀没有被别的套件占用。
4. 新用例 ID 为 `<id_prefix>-<slug>`，文件名就是 `<用例ID>.md`。`slug` 是测试点的英文短名：小写 kebab-case，2–5 个词，只含 `[a-z0-9]` 与 `-`。从测试点提炼条件，不翻译整段步骤，不加序号，不把正向/反向写进 slug。
5. 查重：`rg -N "^id: User-Login-valid-credentials$" assets/testcases`。完整 ID 全库唯一。已出现过的 slug 不复用（含已从树里删除、仍被报告或 evidence 引用的 ID）。

## Where a case goes

- 已有同名 `<模块>/<套件>/`：只新增或修改其中的 `<用例ID>.md`，并改套件 README 的用例表。不把多条用例写回一个文件。
- 模块已存在、套件没有：新建 `assets/testcases/<模块>/<套件>/README.md` 和用例文件，并在该模块 README 的套件清单加一行。
- 模块也没有：新建模块目录和模块 README，再在总索引的模块表加一行，然后写套件。

套件级说明（数据流、共同前置、本套件特有的边界）不属于任何一条用例时，只写在套件 `README.md` 的 `## 详情`。没有这种说明就不写 `## 详情`。

## Templates

用例文件。空的可选节不要写出。步骤从 1 编号；原来只有一段操作和一段预期时保持一步。

```markdown
---
kind: testcase
id: User-Login-valid-credentials
title: 正确账号密码
suite: 用户登录
module: 用户系统
id_prefix: User-Login
type: 正向
status: 就绪
execution: 手工
source: <依据路径或需求名>
version: 1.0.0
confidence: medium
---

# User-Login-valid-credentials 正确账号密码

## 前置条件

账号已注册。

## 步骤

### 1

- 操作：输入已注册账号与正确密码，点击登录
- 预期：进入首页或个人中心
```

反向用例是另一个文件，例如 `User-Login-wrong-password.md`，`type: 反向`。可选节：`## 摘要`、`## 测试数据`、`## 备注`。不知道重要性就不写 `importance`。

套件 README：

```markdown
---
kind: testcase-suite
id: user-login
id_prefix: User-Login
title: 用户登录
module: 用户系统
source: <依据路径或需求名>
version: 1.0.0
confidence: medium
---

# 用户登录

## 详情

不属于任何一条用例的说明。没有就不写这一节。

## 用例

| ID | 名称 | 类型 | 状态 |
| --- | --- | --- | --- |
| [User-Login-valid-credentials](User-Login-valid-credentials.md) | 正确账号密码 | 正向 | 就绪 |
```

总索引 `assets/testcases/README.md`：

```markdown
---
kind: testcase-index
title: 测试用例模块索引
version: 1.0.0
confidence: high
---

# 测试用例模块索引

规范：`docs/spec/testcase-syntax.md`。一个套件一个目录，一条用例一个文件。ID 全库唯一。删除一条用例不改其余 ID，不复用 slug。

## 放置规则

- 新用例归入已有模块的套件目录；对不上时才新增模块目录。
- 套件目录名 = 套件标题。用例文件名 = 用例 ID。
- 不写密码、token、Cookie。账号只写 `account_id`。

## 模块

| 模块 | 目录 | 范围 | 状态 |
| --- | --- | --- | --- |
| <模块> | `assets/testcases/<模块>/` | <一句话> | 在用 |
```

模块 README：

```markdown
---
kind: testcase-module
id: <ascii-slug>
title: <模块>
module: <模块>
version: 1.0.0
confidence: high
---

# <模块>

## 范围

## 不测

## 套件

| 套件 | 目录 |
| --- | --- |
| <套件> | [<套件>](<套件>/README.md) |

## 相关知识

无
```

字段和 TestLink 的对应关系见 `docs/spec/testcase-syntax.md`。

## Update rules

- 改操作或预期：保留原 ID，只 bump 该用例文件的 `version`。套件详情或用例表变了，再 bump 套件 README。
- 测试点含义变了才换 slug，新建文件。旧 ID 不复用。在 `## 备注` 写 `曾用：<旧 ID>`。
- 删除：删掉该 `<用例ID>.md`，并从套件用例表去掉这一行。不改其他用例的 ID。
- 废弃：`status` 改为 `废弃`，在备注写原因。不删除文件，不把 ID 让给新用例，标题不加 `（废弃）`。
- 拆套件或改套件名：用例带着原 ID 搬家，并改两边 README 的链接。每条用例的 `suite` 改成新目录名。

## Finish

```bash
python -m tuner_testkit.testcases assets/testcases
uv run tuner-workspace meta stamp <改过的.md> --kind <testcase|testcase-suite|testcase-module|testcase-index>
```

校验失败就改文件再跑，通过后再停。有 `INDEX.project.md` 时在其知识表登记新套件 README 的路径（只读 front-matter）；平台仓没有业务用例时不要往根 `INDEX.md` 填模块明细。
