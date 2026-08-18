# git-hooks

提交规范校验钩子。规范见 `docs/spec/commit-convention.md`。

## 启用（本地一次性，不改全局配置）

```bash
git config core.hooksPath tools/git-hooks
```

启用后每次 `git commit` 都会运行 `commit-msg`：

1. 校验首行是否符合 Conventional Commits（`type(scope): subject`，type/scope 在允许集合内）；
2. 校验声明的 scope 是否覆盖 `git diff --cached --name-only` 的实际改动层
   （`packages` 覆盖 api_objects/page_objects/action_words）。

- 合并/回滚提交（`Merge`/`Revert`/`fixup!`/`squash!` 开头）跳过校验。
- 找不到 python 或读不到暂存文件时，一致性检查跳过、格式检查仍执行（fail-open）。

## 文件

- `commit-msg`：git 调用的 shell 入口（sh，跨平台）。
- `validate_commit_msg.py`：确定性校验逻辑（stdlib，无第三方依赖）。

## CI 复用

CI 可直接调用 `python tools/git-hooks/validate_commit_msg.py <msg-file>`，或改造为读取
`git log -1 --format=%B` 的变体，与本地钩子共享同一份规则。
