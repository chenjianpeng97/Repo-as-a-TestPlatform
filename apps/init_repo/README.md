# init_repo

模板仓的 "release 制品"：把本平台复制到新项目仓，并对公共资产做版本化/漂移检测。

## 需求背景

本模板仓 *就是* 平台。新建项目仓时需要一份可复制的六层骨架 + 共享的"平台 DNA"
（`.cursor` 组件、`docs/spec`、公共 `packages`/`apps`/`tools`）。同时，当公共资产更新时，
需要能感知"该发新版本了"，避免下游各仓的平台能力悄悄漂移。

## 试用场景

- **新建项目仓**：`scaffold` 生成骨架并下发平台 DNA。
- **发布/漂移检测**：`manifest --check` 判断公共资产是否偏离已发布版本；配合
  `release-template` skill 决策语义化版本 bump。
- 前置条件：从模板仓根目录运行（工具以本仓为 DNA 来源）。无需数据库/网络。

## 运行方式

```bash
# 生成新项目仓骨架 + 平台 DNA
python -m apps.init_repo scaffold ../my-new-project

# 只要骨架，不复制 .cursor/docs-spec/packages
python -m apps.init_repo scaffold ../my-new-project --no-ai

# 版本清单
python -m apps.init_repo manifest --write            # 以 pyproject 版本生成清单
python -m apps.init_repo manifest --write --version 2.1.0
python -m apps.init_repo manifest --check            # 漂移则退出码 1
```

无额外依赖（stdlib）。

## 运行示例

```bash
python -m apps.init_repo scaffold ../demo-repo
# dir  assets/ddl
# ...
# copy .cursor/rules
# copy docs/spec
# ...
# Scaffolded N entries into ../demo-repo
```

## 版本与漂移

- `release_manifest.json`：`template_version` + 被跟踪公共资产的 `sha256`。
- `tools/git-hooks/pre-push` 会在推送前跑 `manifest --check`，**仅警告不阻断**。
- 决策版本 bump / 刷新清单 / 写 release notes：用 `release-template` skill。
- 被跟踪的路径见 `manifest.PLATFORM_PATHS`。
