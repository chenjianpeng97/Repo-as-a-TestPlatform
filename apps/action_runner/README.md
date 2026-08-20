# action_runner

Plane Job 门面：把 ``packages.action_words`` 接到 TestCopilot 的 ``@plane_app`` 协议上。
**不是** action word 实现，也不是 BDD/pytest 该 import 的入口。

## 需求背景

Plane 只能跑 ``python -m apps.*`` 形态的作业，且不能回写 git。造数 / API
动作的领域逻辑已经在 ``packages.action_words``（供 behave / pytest / 其它
apps 组合）。需要一层浅封装：带 Plane 元数据（类别 ``app_id``、destructive、
argv_plan），执行时仍调用 ``get(word_id).run_from_dict``。

## 试用场景

- **适用**：TestCopilot Formulation 点运行某个 word；或 Tools 页用 word_id + JSON
  走同一条 Job。
- **不适用**：写新 word、BDD 步骤、pytest。那些继续
  ``from packages.action_words import ...``。
- 前置：绑定测试仓并 Sync（``apps.index_platform``）；破坏性类别需要确认。
- 密钥走环境变量 / ``env_local.py``，本 CLI **不接受** ``--username`` / ``--password``。

## 运行方式

在仓库根目录：

```bash
python -m apps.action_runner run --expect-category db_assert <word_id> --params "{}"
python -m apps.action_runner run --expect-category db_seed <word_id> --example
```

依赖与 ``packages.action_words`` 相同（项目 ``uv sync`` / 最小安装即可）。

## 运行示例

```bash
python -m apps.action_runner run --expect-category db_seed db_seed.create_example --example
```

stdout 打印 word ``Result`` JSON（含 cleanup 登记）；退出码 0/1。
平台侧作业日志里查看这份 JSON。本地调试 word 请用
``python -m packages.action_words run ...``，不要从 tests 里 import 本包。
