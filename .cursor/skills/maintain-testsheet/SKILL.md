---
name: maintain-testsheet
version: 1.0.0
description: Builds and updates a test sheet under assets/testsheet/<round>/testsheet.md, copying the selected ready cases from assets/testcases into that round's testcase/ folder and linking only those copies. Use when the user asks to 生成测试单, 维护测试单, 测试单, or mentions assets/testsheet or testsheet.md. Do not use to edit the case library, write a testdesign, or curate assets/testreport.
---

# Maintain testsheet

## Scope

- **Write**: `assets/testsheet/<轮次>/testsheet.md`，以及同目录 `testcase/` 里的用例副本。
- **Read**: `assets/testcases/`。有 `INDEX.project.md` 时先读，只采用已有事实。
- **Out of scope**: 改 `assets/testcases/`（用 `maintain-testcases`）、写 `assets/testdesign/`、写 `assets/testreport/`（用 `generate-test-report`）。已有的 `assets/testreports/**/测试单.md` 不搬，除非用户明确要求迁移。

## Layout

```text
assets/testsheet/<轮次>/
  testsheet.md
  testcase/<模块>/README.md
  testcase/<模块>/<套件>/README.md
  testcase/<模块>/<套件>/<用例ID>.md
  evidence/
```

`<轮次>` 用用户给的目录名。没给就用 `yyMMdd` 加模块名，例如 `261015预入库管控`。一轮一个目录。

## Generate

1. 读模块 README 和相关套件 README。范围按用户点名的模块、套件或用例 ID。没点名到单条时，纳入该范围内 `status: 就绪` 的用例。`status: 废弃` 不复制、不进表，在测试单开头点名。
2. 用文件复制，不要重写正文。用例文件、该模块 README、被选中套件的 README 都复制到上面的 `testcase/` 路径。复制后不再从用例库刷新，除非用户要求重新提取。
3. 写 `testsheet.md`。不写 YAML 头。用例列只链副本：

```text
[Admin-View-columns-shown](testcase/预入库管控/管控情况查看/Admin-View-columns-shown.md)
```

不要链 `assets/testcases/` 或 `../../testcases/`。

从副本填列，不要另编业务规则：

| 列 | 来源 |
| --- | --- |
| 用例 | 副本文件名，链到副本 |
| 测试点 | `<type>-<title>`，如 `正向-清单展示约定列` |
| 数据 | `## 测试数据` 的第一句。没有则用 `## 前置条件` 的第一句 |
| 预期要点 | 第一步 `预期` 收成一句 |
| 结果 | `未执行` |
| 实测记录 | 空 |

分组：模块 README 的 `## 范围` 已有编号块时，用那些块做 `##`。块内按套件 README 的顺序各做一个 `###` 和一张表。没有范围编号时，一个套件一个 `##`。不要把一个套件拆进两张表，除非用户要求。

## Sheet

```markdown
# <主题>测试单

共 N 条。步骤在本目录 `testcase/`。`<废弃ID>` 已废弃，不在本单。

依据：<用户给出的需求或来源路径>。

## 怎么填

- 「结果」只写：通过、失败、部分通过、未执行、阻塞。
- 「实测记录」写看到的文案、单号、库存状态。不写密码、token、Cookie。账号只写 `account_id` 或登录名。
- 截图放本目录，文件名用用例 ID。

## 本轮信息

| 项 | 填写 |
| --- | --- |
| 测试人 | |
| 日期 | |
| 环境 | |
| 证据 | 本目录 `evidence/` |
| 通过 | 0 |
| 失败 | 0 |
| 部分通过 | 0 |
| 未执行 | N |
| 阻塞 | 0 |

## 测的时候先记住

- <会改变通过或失败判定的规则。来自套件 README 的「详情」，或用户本轮原话。没有就写「无」。>

## 1. <范围块>

### 1.1 <套件名>

| 用例 | 测试点 | 数据 | 预期要点 | 结果 | 实测记录 |
| --- | --- | --- | --- | --- | --- |
| [<用例ID>](testcase/<模块>/<套件>/<用例ID>.md) | 正向-<title> | <数据> | <预期要点> | 未执行 | |

## 缺陷

| 编号 | 用例 | 现象 | 是否阻塞后续 |
| --- | --- | --- | --- |
| 无 | | | |
```

五个计数之和等于表内行数。新建时未执行等于 N，其余为 0。

## Update

- 回写时只改 `testsheet.md` 的结果、实测记录、计数和缺陷。结果只用那五个词。
- 增删一行后立刻重算「共 N 条」和五个计数。
- 从本单移除一条：删表行，删 `testcase/` 里对应副本。开头写明 ID 和原因。菜单权限这类配置问题、以及改由别的页面跟踪的条目，是移除，不记失败，也不进缺陷表。
- 缺陷只记产品行为。
- 本轮步骤缺前置或判定规则：改 `testcase/` 里的副本。要沉淀回用例库时另走 `maintain-testcases`，改完不要把测试单的链接改回用例库。
- 截图放本目录，文件名用用例 ID。一组结果的图放在对应小节下，写成 `![](文件名.png)`。接口 JSON 放 `evidence/`。造数写 `packages/action_words/db_seed/`，不在 `assets/testsheet/` 里放可执行脚本。

## Hard rules

- 不写密码、token、Cookie。
- 不编用例库和套件详情里没有、用户本轮也没说的业务规则。
- 测试单生成后，步骤以副本为准。
