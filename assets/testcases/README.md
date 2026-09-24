---
kind: testcase-index
title: 测试用例模块索引
version: 1.0.0
confidence: high
---

# 测试用例模块索引

规范：`docs/spec/testcase-syntax.md`。维护流程：skill `maintain-testcases`。

一个功能一个 Markdown 文件。该功能的全部用例写在四级标题下。用例 ID 是功能英文缩写加 4 位序号，例如 `User-Login0001`，在全库是唯一键。模块怎么划、文件写到哪，以本页和各模块 `README.md` 为准。

## 放置规则

- 新用例优先归入已有模块的功能文件。现有模块的范围都覆盖不住时，才新建 `assets/testcases/<模块>/`。
- 目录名等于功能文件的二级标题；`<功能>.md` 的文件名等于三级标题。
- 模块目录下只放 `README.md` 和功能文件，不再套子目录。
- 不写密码、token、Cookie。账号只写 `account_id`。

## 模块

| 模块 | 目录 | 范围 | 状态 |
| --- | --- | --- | --- |
| _（尚无）_ | | 本仓是平台仓。业务系统的模块与用例写在下游 workspace 或 `dogfood/` 的 `assets/testcases/`，不要把被测业务用例堆进平台索引。 | 规划中 |

## 给编写的人

1. 先看上表，选定模块。
2. 打开该模块的 `README.md`，确认功能边界。
3. 在对应 `<功能>.md` 追加四级标题。沿用该文件的 `id_prefix`，序号在这个前缀内取最大号 + 1。
4. 改完跑 `python -m tuner_testkit.testcases assets/testcases`。
