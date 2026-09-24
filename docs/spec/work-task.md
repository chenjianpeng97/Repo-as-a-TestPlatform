---
name: work-task
version: 1.0.0
description: 入库任务 work/tasks、阻塞式人类提问，以及和测试设计、证据、测试报告的闭环。
---

# 工作任务（work-task）

> 人在 workspace 里发布的任务是 Agent 的事务上下文，写入 Git。
> 会话流水仍在 `artifacts/inbox/<utc>-<agent>-<slice>.md`（gitignore）。
> 必须由人回答的问题写到 `artifacts/inbox/questions/`，不猜 SSH、日志接口或 Rancher。

## 1. 路径

```text
work/tasks/TASK-<YYYYMMDD>-<nnn>.md          # 入库
artifacts/inbox/questions/Q-<YYYYMMDD>-<nnn>.md   # gitignore，本机异步信箱
```

`work/**` 的提交 scope 是 `work`。问题文件不入库；人答完后的结论写回任务的 `## Decisions`，需要留下的通道说明再策展到 `assets/domain-notes/`。

## 2. 任务类型

| type | 输入 | 产出 | 证据 |
| --- | --- | --- | --- |
| `explore` | URL / account_id | `assets/explore/` | `artifacts/evidence/<run_id>/` |
| `test-design` | 用例、domain-notes、explore、design | `assets/testdesign/<sut>/<slug>.md` | 需求或探索来源，见 test-design-syntax |
| `test-execution` | 已存在的 testdesign（front-matter `design`） | `assets/testreport/<sut>/<yyyy-mm>/<slug>.md` | 同一次 run 的截图、网络、接口响应、日志 |

`test-execution` 按测试设计里的「点击路径」跑 `page_test run` 或 behave UI，不代替测试设计，也不承担纯 API 回归。

状态：`open` → `in_progress` → `done`。存在未回答的阻塞问题时为 `blocked`。全部答完后回到 `in_progress`。

## 3. Front-matter

```yaml
kind: task
id: TASK-20260924-001
title: 订单创建端到端
type: test-execution
status: open
objective: 按测试设计点完订单创建并写出报告
scope: [order-create]
inputs: []
outputs: []
design: assets/testdesign/order/create.md
evidence: []
questions: []
```

作者与日期用 `tuner-workspace meta stamp`（`tuner-task create` 会调用）。禁止写入密码、token、Cookie。

## 4. 人类提问循环

仓库里还没有该通道的说明时才问。`assets/domain-notes`、`INDEX`、已有 `apps/<log-fetcher>` 能回答的，直接用。

日志通道没有 provider 时，主题固定为 `sut-log-source`，选项固定为：

| id | 含义 |
| --- | --- |
| `ssh-dir` | SSH 到指定目录读日志文件 |
| `log-api` | 调用已有日志接口 |
| `rancher-api` | 用 Rancher API 拉 Pod 日志 |
| `skip` | 本轮不做日志通道 |

```bash
tuner-task ask --task TASK-20260924-001 --topic sut-log-source \
  --prompt "仓库没有写明后端日志从哪取"

tuner-task answer Q-20260924-001 --option rancher-api \
  --note "命名空间见 env_local 的 LOG_SOURCE" \
  --curate assets/domain-notes/order/log-source.md
```

- 提问立刻落盘，并把任务标为 `blocked`。只挡住依赖该答案的回写；不依赖日志的点击可以先做完，但在回答前不要编写取日志实现，也不要选定通道。
- `--note` 只留可入库的指向。CLI 拒绝 `password=` / `token:` / `Bearer …` 这类赋值。
- `skip` 表示报告里日志证据写「无」，设计上的日志断言保持未验证。
- `tuner-task finish` 在仍有 `status: open` 且 `blocking: true` 的问题时失败。
- `test-execution` 收口时，`design` 与 `outputs` 里的路径必须已在磁盘上。

## 5. 和测试设计的闭环

```text
test-design（点击路径 + 期望）
  → task type=test-execution
  → 端到端点击
  → artifacts/evidence/<run_id>/（截图、network、api、logs）
  → assets/testreport（每条路径的结果 + 证据路径）
  → 回写 testdesign「执行反馈」
  → 通道类决定写入 Decisions，并在需要时策展 domain-notes
```

点击失败只记入「执行反馈」。接口与落库不一致时写 Decision，并引用 evidence 相对路径。点出设计没覆盖的副作用时策展 `assets/design/`，风险行指向同一 `run_id`。
