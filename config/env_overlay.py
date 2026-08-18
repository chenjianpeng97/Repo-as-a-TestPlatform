# plane-dogfood 提交的数据源别名与类型（无密钥）。
# 真实密码写入本机 gitignore 的 config/env_local.py，
# 或用环境变量 ARGON_DB_<ALIAS>_* / TEST_* 覆盖。
#
# 本试验田主库是 Plane 本地 PostgreSQL（docker-compose-local.yml 的 plane-db，
# 宿主机 127.0.0.1:5432）。平台 DNA 仍在 config/env.py 保留 mysql/sqlserver/postgres
# 占位；此处覆盖 main 的 type / 库名，便于 dump_ddl 默认打到 assets/ddl/main/。

DATABASES = {
    "main": {
        "type": "postgres",
        "host": "127.0.0.1",
        "port": 5432,
        "user": "plane",
        "password": "CHANGE_ME",
        "database": "plane",
    },
}
