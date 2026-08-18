# 放置环境信息，如 db 配置、url 配置等。
# 本文件只提交占位结构（别名 / 类型 / 本地示例 host），不含真实密钥。
#
# 覆盖顺序（后者覆盖前者的同名键）：
#   1. 本文件 DATABASES / TEST_* 占位
#   2. config/env_overlay.py（可选，项目/试验田提交：额外别名与类型，仍无密钥）
#   3. config/env_local.py（gitignore，本机真实 host/密码/账号）
#   4. 环境变量 ARGON_DB_<ALIAS>_HOST/PORT/USER/PASSWORD/NAME
#      （旧的 ARGON_DB_HOST/... 继续覆盖默认别名 "main"）
#      TEST_BASE_URL / TEST_USERNAME / TEST_PASSWORD 同样优先于本模块。

from __future__ import annotations

from typing import Any

DATABASES: dict[str, dict[str, Any]] = {
    # 主业务库 — MySQL
    "main": {
        "type": "mysql",
        "host": "127.0.0.1",
        "port": 3306,
        "user": "root",
        "password": "CHANGE_ME",
        "database": "example",
    },
    # 第二数据源占位 — SQL Server（需要时填入真实连接）
    "sqlserver": {
        "type": "sqlserver",
        "host": "127.0.0.1",
        "port": 1433,
        "user": "sa",
        "password": "CHANGE_ME",
        "database": "example",
    },
    # 第三数据源占位 — PostgreSQL（Plane 等；需要时填入真实连接）
    "postgres": {
        "type": "postgres",
        "host": "127.0.0.1",
        "port": 5432,
        "user": "postgres",
        "password": "CHANGE_ME",
        "database": "example",
    },
}

# API 执行的网关地址（仅 host，不带路径！）。
# 环境变量 TEST_BASE_URL 优先于此处。
TEST_BASE_URL = ""

# behave api stage 登录账号。优先级：behave -D username/-D password
# > 环境变量 TEST_USERNAME/TEST_PASSWORD > 此处。
TEST_ACCOUNT: dict[str, str] | None = None


def _merge_databases(overlay: dict[str, Any]) -> None:
    for alias, cfg in overlay.items():
        if not isinstance(cfg, dict):
            continue
        if alias in DATABASES:
            DATABASES[alias] = {**DATABASES[alias], **cfg}
        else:
            DATABASES[alias] = dict(cfg)


def _apply_module(mod: Any) -> None:
    extra = getattr(mod, "DATABASES", None)
    if isinstance(extra, dict):
        _merge_databases(extra)
    global TEST_BASE_URL, TEST_ACCOUNT
    url = getattr(mod, "TEST_BASE_URL", None)
    if url:
        TEST_BASE_URL = str(url)
    account = getattr(mod, "TEST_ACCOUNT", None)
    if account:
        TEST_ACCOUNT = account


def _load_overlay(mod_name: str) -> None:
    try:
        mod = __import__(mod_name, fromlist=["*"])
    except ImportError:
        return
    _apply_module(mod)


_load_overlay("config.env_overlay")
_load_overlay("config.env_local")

# 向后兼容：历史代码读取的默认库即 main 别名
DB_CONFIG = DATABASES["main"]
