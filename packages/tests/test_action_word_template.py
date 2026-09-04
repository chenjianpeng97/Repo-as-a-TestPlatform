"""Action word 模板一致性兜底测试。

`@register` 装饰器在导入期只校验硬约束（word_id / name / category /
docstring 存在）；本测试对全量注册的 word 强制更完整的模板规范：

- 模块与类 docstring 必须描述业务（非占位一行）；
- ``Params`` / ``Result`` 每个字段必须带中文 ``description``（平台可视化依赖）；
- ``Params`` 必须 ``extra="forbid"``（拒绝未知参数拼写错误静默通过）；
- ``example_params`` 非空且能通过 ``Params`` 校验（保证文档样例永远可运行）；
- ``run`` 必须带返回类型标注。

模板仓库允许注册量为 0（仅骨架）；一旦项目新增 word，下列约束全部生效。
"""
from __future__ import annotations

import inspect

import pytest
from pydantic import BaseModel

from tuner_testkit.action_words.base import ActionResult, ActionWord
from tuner_testkit.action_words.registry import list_all

ALL_WORDS = list_all()
WORD_IDS = [cls.word_id for cls in ALL_WORDS]


def test_registry_is_list():
    """空模板合法：允许 0 个 word；有注册时其余用例覆盖模板契约。"""
    assert isinstance(ALL_WORDS, list)


@pytest.mark.parametrize("cls", ALL_WORDS, ids=WORD_IDS)
def test_docstrings_meaningful(cls: type[ActionWord]):
    class_doc = inspect.getdoc(cls) or ""
    assert len(class_doc.strip()) >= 20, f"{cls.word_id}: 类 docstring 过短，须描述业务/前置条件/副作用"
    module_doc = inspect.getdoc(inspect.getmodule(cls)) or ""
    assert len(module_doc.strip()) >= 20, f"{cls.word_id}: 模块 docstring 过短"


@pytest.mark.parametrize("cls", ALL_WORDS, ids=WORD_IDS)
def test_params_fields_described_and_strict(cls: type[ActionWord]):
    params_cls = cls.Params
    assert issubclass(params_cls, BaseModel), f"{cls.word_id}: Params 必须是 pydantic BaseModel"
    assert params_cls.model_config.get("extra") == "forbid", (
        f"{cls.word_id}: Params 必须 extra='forbid'"
    )
    for field_name, field in params_cls.model_fields.items():
        assert (field.description or "").strip(), (
            f"{cls.word_id}: Params.{field_name} 缺少 description"
        )


@pytest.mark.parametrize("cls", ALL_WORDS, ids=WORD_IDS)
def test_result_fields_described(cls: type[ActionWord]):
    result_cls = cls.Result
    assert issubclass(result_cls, ActionResult), f"{cls.word_id}: Result 必须继承 ActionResult"
    for field_name, field in result_cls.model_fields.items():
        assert (field.description or "").strip(), (
            f"{cls.word_id}: Result.{field_name} 缺少 description"
        )


@pytest.mark.parametrize("cls", ALL_WORDS, ids=WORD_IDS)
def test_example_params_validates(cls: type[ActionWord]):
    assert cls.example_params, f"{cls.word_id}: 必须提供 example_params"
    cls.Params.model_validate(cls.example_params)


@pytest.mark.parametrize("cls", ALL_WORDS, ids=WORD_IDS)
def test_run_signature_annotated(cls: type[ActionWord]):
    signature = inspect.signature(cls.run)
    assert signature.return_annotation is not inspect.Signature.empty, (
        f"{cls.word_id}: run 缺少返回类型标注"
    )
    params_param = list(signature.parameters.values())[1]
    assert params_param.annotation is not inspect.Parameter.empty, (
        f"{cls.word_id}: run(params) 缺少类型标注"
    )


@pytest.mark.parametrize("cls", ALL_WORDS, ids=WORD_IDS)
def test_describe_exports_schema(cls: type[ActionWord]):
    payload = cls.describe()
    for key in ("word_id", "name", "category", "doc", "params_schema", "example_params"):
        assert key in payload, f"{cls.word_id}: describe() 缺少 {key}"
    assert payload["params_schema"].get("properties") is not None
