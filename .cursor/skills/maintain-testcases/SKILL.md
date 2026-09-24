---
name: maintain-testcases
version: 1.1.0
description: Creates and updates the functional testcase set under assets/testcases/<module>/<feature>.md using the four-level heading template and stable feature-prefixed IDs such as User-Login0001. Use when the user asks to 编写/生成/维护测试用例, add a module or feature case file, or mentions assets/testcases or case ID. Do not use for testdesign click-paths or behave .feature files.
---

# Maintain testcases

## Scope

- **Write**: `assets/testcases/**` only.
- **Must follow**: `docs/spec/testcase-syntax.md`.
- **Out of scope**: `assets/testdesign/`（用 `derive-test-design`）、`tests/features/**`（用 `feature-authoring`）、pytest。

## Before writing

1. 读 `assets/testcases/README.md` 与目标模块的 `README.md`（没有就先按下面的模板建）。
2. 读 `INDEX.md`；存在 `INDEX.project.md` 时一并读。只采用已有 usecase / domain-notes / explore / design，或用户本次给出的事实。
3. 功能文件已有 `id_prefix` 就沿用，不要另起缩写。新建功能时用功能名的英文词，每词首字母大写、`-` 连接（`用户登录` → `User-Login`），写入 `id_prefix`。确认这个前缀没有被别的功能占用。
4. 序号只在该前缀内递增：`rg -N "^#### User-Login[0-9]{4} " assets/testcases`。下一条 = 最大序号 + 1，4 位补零。该前缀还没有用例时从 `0001` 起，得到 `User-Login0001`。

## Where a case goes

- 已有同名 `<模块>/<功能>.md`：只追加或修改四级标题，不新建第二份文件。
- 模块已存在、功能没有：新建 `assets/testcases/<模块>/<功能>.md`，并在该模块 README 的功能清单加一行。
- 模块也没有：新建目录和模块 README，再在总索引的模块表加一行，然后写功能文件。

## Templates

功能文件：

```markdown
---
kind: testcase
id: <ascii-slug>
id_prefix: <Feature-Name>
title: <功能>
module: <模块>
source: <依据路径或需求名>
version: 1.0.0
confidence: medium
---

# 测试用例
## <模块>
### <功能>
#### <Feature-Name>0001 正向-<测试点>
- 步骤：<操作>
- 预期：<可观察结果>
#### <Feature-Name>0002 反向-<测试点>
- 步骤：<操作>
- 预期：<可观察结果>
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

规范：`docs/spec/testcase-syntax.md`。一个功能一个文件，用例写在四级标题下，ID 全库唯一且不重排。

## 放置规则

- 新用例归入已有模块的功能文件；对不上时才新增模块目录。
- 目录名 = 二级标题；文件名 = 三级标题。
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

## 功能

| 功能 | 文件 |
| --- | --- |
| <功能> | [<功能>.md](<功能>.md) |

## 相关知识

无
```

## Update rules

- 改步骤或预期：保留原 ID 和 `id_prefix`，bump 该文件 `version`。
- 废弃：标题加 `（废弃）`，补 `- 状态：废弃` 与原因。不删除该四级标题，不把 ID 让给新用例。
- 拆文件或改功能名：用例带着原 ID 搬家，并改两边 README 的链接。

## Finish

```bash
python -m tuner_testkit.testcases assets/testcases
uv run tuner-workspace meta stamp <改过的.md> --kind <testcase|testcase-module|testcase-index>
```

校验失败就改文件再跑，通过后再停。有 `INDEX.project.md` 时在其知识表登记新功能文件的路径（只读 front-matter）；平台仓没有业务用例时不要往根 `INDEX.md` 填模块明细。
