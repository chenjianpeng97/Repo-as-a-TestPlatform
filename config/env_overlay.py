# plane-dogfood 提交的数据源别名与类型（无密钥）。
# 真实 host / 密码 / 账号写入本机 gitignore 的 config/env_local.py，
# 或用环境变量 ARGON_DB_<ALIAS>_* / TEST_* 覆盖。
#
# 平台目前内置 mysql / sqlserver。Plane 若需要额外别名，在此按类型声明，
# 不要把真实连接写进本文件。

DATABASES = {}
