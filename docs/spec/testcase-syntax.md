---
name: testcase-syntax
version: 1.1.0
description: assets/testcases 的目录、四级标题、功能缩写用例 ID 与模块 README。功能用例集的唯一事实源。
---

# 测试用例（testcase-syntax）

> 一份功能文件收齐该功能的全部用例。给人读，也给 LLM 按同一棵树增删改。
> 维护流程见 skill `maintain-testcases`。编辑约束见 `.cursor/rules/testcases.mdc`。

## 1. 和相邻知识的分工

| 路径 | 记什么 |
| --- | --- |
| `assets/usecases/` | 导入或讲解过的业务场景，不是带稳定 ID 的用例集 |
| `assets/testdesign/` | 一次任务的范围、策略和点击路径 |
| `assets/testcases/` | 按模块 / 功能维护的用例集，每条用例一个稳定 `CASE` ID |
| `tests/features/` | 已自动化的 Gherkin。本规范不写 `.feature` |

## 2. 目录

```text
assets/testcases/README.md                 # 模块总索引：规划、模块一览、给人和 LLM 的放置规则
assets/testcases/<模块>/README.md          # 该模块的范围、边界、功能清单
assets/testcases/<模块>/<功能>.md          # 该功能的全部用例
```

例子：`assets/testcases/用户系统/用户登录.md`。

- 目录名 = 模块显示名 = 功能文件里的二级标题。
- 文件名（不含 `.md`）= 功能显示名 = 三级标题。
- 只允许这一层：模块目录里不再套子目录。
- 名称不要用 `\ / : * ? " < > |`。

## 3. 标题层级

功能文件正文只用这四级。一个功能的全部用例都放在四级标题下。

```markdown
# 测试用例
## 用户系统
### 用户登录
#### User-Login0001 正向-正确账号密码
- 步骤：输入已注册账号与正确密码点击登录
- 预期：登录成功进入首页或个人中心
#### User-Login0002 反向-正确账号错误密码
- 步骤：输入已注册账号与错误密码点击登录
- 预期：停留在登录页并提示账号或密码错误
```

| 级别 | 含义 | 规则 |
| --- | --- | --- |
| `#` | 中心主题 | 固定为 `测试用例` |
| `##` | 模块 | 全文件只有一个，且等于父目录名 |
| `###` | 功能 | 全文件只有一个，且等于文件名 |
| `####` | 一条用例 | 功能缩写 ID + 空格 + `正向-` 或 `反向-` + 测试点名称 |

## 4. 用例 ID

ID 是全库唯一键，由功能缩写和该功能内的序号组成：`<缩写><四位序号>`。

- 缩写：功能名的英文词，每词首字母大写，用 `-` 连接。`用户登录` → `User-Login`。只含字母和连字符，不含数字。
- 序号：4 位数字，从 `0001` 起。`User-Login0001`、`User-Login0002`。
- 缩写写在功能文件 front-matter 的 `id_prefix`，之后不得改。同一 `id_prefix` 只能属于一个功能文件。
- 新增时只扫描这个前缀：`rg -N "^#### User-Login[0-9]{4} " assets/testcases`，取最大序号 + 1。
- 不同功能的前缀不同，所以 `User-Login0001` 与 `Reset-Password0001` 不会撞键。
- 已发出的 ID 不改、不复用、不因为删用例而重排。
- 废弃：标题末尾加 `（废弃）`，并在该条下写 `- 状态：废弃` 与原因。保留标题，不要删掉这一节。

## 5. 每条用例的子弹

必填，且用中文冒号：

- `- 步骤：` 测试人员或 LLM 能照做的操作
- `- 预期：` 可观察结果

可选，仍放在同一条四级标题下：

- `- 前置：`
- `- 数据：` 用账号 `account_id` 或数据文件路径，不写密码、token、Cookie
- `- 备注：`

没有依据的业务规则不要写进步骤或预期。依据来自用户说明，或 `INDEX.md` / `INDEX.project.md` 能指向的 usecase、domain-notes、explore、design。

## 6. Front-matter

功能文件：

```yaml
---
kind: testcase
id: user-login
id_prefix: User-Login
title: 用户登录
module: 用户系统
sut: <sut 短名，未知可省略>
source: <assets/… 或需求名>
version: 1.0.0
confidence: medium
---
```

模块 README 用 `kind: testcase-module`。总索引用 `kind: testcase-index`。
人工修改后 bump `version`。署名用 `tuner-workspace meta stamp <path> --kind testcase`（模块 README 用 `testcase-module`，总索引用 `testcase-index`）。

## 7. 两份 README

`assets/testcases/README.md` 告诉人和 LLM：模块怎么划分、新功能该进哪个目录、当前有哪些模块。至少包含：

- 放置规则（指向本 spec）
- 模块表：模块名、目录、一句话范围、状态（`在用` / `规划中`）

`assets/testcases/<模块>/README.md` 至少包含：

- 这个模块测什么、不测什么
- 功能清单：每个 `<功能>.md` 一行链接
- 相关知识路径（没有就写「无」）

新增或重命名功能文件时，两份 README 一起改。总索引的模块表与模块目录一致；模块 README 的功能清单与该目录下的功能文件一致。
