from pathlib import Path

from tuner_testkit.testcases.validate import validate_tree

_INDEX = """---
kind: testcase-index
title: 测试用例模块索引
version: 1.0.0
---

# 测试用例模块索引
"""

_MODULE = """---
kind: testcase-module
id: user-system
title: 用户系统
module: 用户系统
version: 1.0.0
---

# 用户系统

## 功能

| 功能 | 文件 |
| --- | --- |
| 用户登录 | [用户登录.md](用户登录.md) |
"""

_FEATURE = """---
kind: testcase
id: user-login
id_prefix: User-Login
title: 用户登录
module: 用户系统
source: 需求
version: 1.0.0
confidence: medium
---

# 测试用例
## 用户系统
### 用户登录
#### User-Login0001 正向-正确账号密码
- 步骤：输入已注册账号与正确密码点击登录
- 预期：登录成功进入首页或个人中心
#### User-Login0002 反向-正确账号错误密码
- 步骤：输入已注册账号与错误密码点击登录
- 预期：停留在登录页并提示账号或密码错误
"""


def _tree(root: Path, feature: str = _FEATURE) -> None:
    base = root / "assets" / "testcases"
    module = base / "用户系统"
    module.mkdir(parents=True)
    (base / "README.md").write_text(_INDEX, encoding="utf-8")
    (module / "README.md").write_text(_MODULE, encoding="utf-8")
    (module / "用户登录.md").write_text(feature, encoding="utf-8")


def test_valid_tree(tmp_path: Path) -> None:
    _tree(tmp_path)
    assert validate_tree(tmp_path / "assets" / "testcases") == []


def test_duplicate_id_and_bad_heading(tmp_path: Path) -> None:
    broken = _FEATURE.replace(
        "#### User-Login0002 反向-正确账号错误密码",
        "#### User-Login0001 反向-错误密码\n#### 没有编号",
    )
    _tree(tmp_path, broken)
    errors = validate_tree(tmp_path / "assets" / "testcases")
    assert any("duplicate User-Login0001" in item for item in errors)
    assert any("case heading must be" in item for item in errors)
