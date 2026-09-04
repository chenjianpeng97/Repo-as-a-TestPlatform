# index_ai

扫描 `.cursor/**` 的 AI 组件（rule / skill / agent / hook），确定性生成人类可读的
`.cursor/REGISTRY.md`——即"平台后端服务"的能力清单与版本表。

## 需求背景

`.cursor/**` 的规则/技能/编排/钩子是本平台的"后端 service"（业务规则与处理逻辑）。
工程师需要一眼看全当前有哪些组件、如何触发、各是什么版本，而不必逐个打开文件。

## 试用场景

- 新增/修改 rule/skill/agent/hook 后，刷新注册表。
- CI 用 `--check` 防止 REGISTRY 与实际组件漂移。
- 前置条件：无（纯本地文件扫描，无需数据库/网络）。

## 运行方式

```bash
python -m tuner_testkit.apps.index_ai            # 重新生成 .cursor/REGISTRY.md
python -m tuner_testkit.apps.index_ai --check    # 不写文件；REGISTRY 过期则退出码 1
```

无额外依赖（stdlib）。

## 运行示例

```bash
python -m tuner_testkit.apps.index_ai
# -> Wrote .cursor/REGISTRY.md
```

组件的 `version` 取自各文件 front-matter 的 `version` 字段（rules/skills/agents）；缺失显示 `-`。
