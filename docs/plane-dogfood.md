# plane-dogfood — Plane 试验田（dogfood）

本分支 = GitHub `main` 的平台 DNA + **Plane** 业务资产。

[Plane](https://github.com/makeplane/plane) 是开源项目管理软件。本试验田同时做两件事：

1. 用 Plane 作为本测试仓（Repo-as-a-TestPlatform）的可视化入口；
2. 用本仓的测试资产回归 Plane 自身（dogfood）。

其它被测系统不要堆进这个分支，去各自项目仓，用 `python -m apps.init_repo scaffold` 从 **`main`** 取 DNA。

## 分支纪律

- 只允许 **`main` → `plane-dogfood`** merge。禁止把本分支合回 `main`。
- 试用中发现 `packages.db` / `logging` / `api_test` / 公共 apps / `.cursor/**` 要改：切到 `main` 改并提交，再回到本分支 `git merge main`。
- 本分支不要改平台文件（`INDEX.md`、`config/env.py`、`pyproject.toml`、action_words 骨架、`docs/spec/**`、`AGENTS.md`）。

在「私有 GitLab + 公开 GitHub」同一工作副本里：公开仓的 `main` 本地叫 `public-main`（跟踪 `github/main`），框架改动请提交到 `public-main` 再 merge 进本分支。不要和 GitLab 的 `main` / `sandbox/jafron` 搞混。

## 本分支独有、main 上没有的路径

| 路径 | 内容 |
| --- | --- |
| `INDEX.project.md` | Plane 业务资产地图 |
| `config/env_overlay.py` | 额外数据源别名（无密钥；按需追加） |
| `packages/action_words/_internal/params_project.py` | 主数据样例（需要时再加） |
| `packages/action_words/models_project.py` | 业务模型（需要时再加） |
| `assets/`、业务 `api_objects` / action words、`tests/features/**` | 被测系统资产 |

## 密钥（必做，否则跑不了）

1. 复制 `config/env_local.py.example` → `config/env_local.py`（已被 gitignore）。
2. 填入真实 `DATABASES`、`TEST_BASE_URL`（Plane 网关）、`TEST_ACCOUNT`。
3. 也可只用环境变量：`ARGON_DB_<ALIAS>_*`、`TEST_BASE_URL`、`TEST_USERNAME` / `TEST_PASSWORD`。

**不要**把 `env_local.py` 或 `.env` 提交到任何分支。

## 合入 main 之后怎么继续试用

```powershell
git checkout plane-dogfood
git merge public-main
```

GitHub 上对应：

```powershell
git fetch github
git merge github/main
```

若偶然改到了平台文件，把它们还原成 `main` 的版本后再提交业务改动。
