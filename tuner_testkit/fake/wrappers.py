"""First-class Faker(zh_CN) wrappers. Extra Faker methods stay on ``raw``."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from tuner_testkit.fake.catalog import EmptyInputs, register
from tuner_testkit.fake.core import get_faker

_FAKER_BINDINGS: tuple[tuple[str, str, str, str, str], ...] = (
    # fake_id, name, category, faker method, returns
    ("person_name", "中文姓名", "identity", "name", "string"),
    ("person_name_male", "中文男性姓名", "identity", "name_male", "string"),
    ("person_name_female", "中文女性姓名", "identity", "name_female", "string"),
    ("first_name", "名", "identity", "first_name", "string"),
    ("last_name", "姓", "identity", "last_name", "string"),
    ("phone", "手机号", "identity", "phone_number", "string"),
    ("job", "职位", "identity", "job", "string"),
    ("address", "地址", "address", "address", "string"),
    ("province", "省份", "address", "province", "string"),
    ("city", "城市", "address", "city", "string"),
    ("district", "区县", "address", "district", "string"),
    ("street_address", "街道地址", "address", "street_address", "string"),
    ("postcode", "邮编", "address", "postcode", "string"),
    ("building_number", "楼栋号", "address", "building_number", "string"),
    ("company_prefix", "公司字号", "china", "company_prefix", "string"),
    ("company_suffix", "公司后缀", "china", "company_suffix", "string"),
    ("email", "邮箱", "network", "email", "string"),
    ("user_name", "用户名", "network", "user_name", "string"),
    ("url", "URL", "network", "url", "string"),
    ("ipv4", "IPv4", "network", "ipv4", "string"),
    ("uuid4", "UUID", "generic", "uuid4", "string"),
    ("ean13", "EAN-13 条码", "generic", "ean13", "string"),
    ("ean8", "EAN-8 条码", "generic", "ean8", "string"),
    ("md5", "MD5 hex", "generic", "md5", "string"),
    ("sha256", "SHA256 hex", "generic", "sha256", "string"),
    ("bank_name", "银行名称", "finance", "bank", "string"),
    ("iban", "IBAN", "finance", "iban", "string"),
    ("bban", "BBAN", "finance", "bban", "string"),
    ("credit_card_number", "信用卡号", "finance", "credit_card_number", "string"),
    ("credit_card_expire", "信用卡有效期", "finance", "credit_card_expire", "string"),
    ("license_plate", "车牌号", "finance", "license_plate", "string"),
    ("vin", "车架号", "finance", "vin", "string"),
)


def _bind(method: str):
    def fn() -> object:
        return getattr(get_faker(), method)()

    fn.__name__ = method
    fn.__doc__ = f"Faker zh_CN ``{method}()``."
    return fn


for _fake_id, _name, _category, _method, _returns in _FAKER_BINDINGS:
    _fn = _bind(_method)
    _fn.__name__ = _fake_id
    register(_fake_id, name=_name, category=_category, inputs=EmptyInputs, returns=_returns)(_fn)
    globals()[_fake_id] = _fn


@register("phone_prefix", name="手机号段", category="identity", returns="number")
def phone_prefix() -> int:
    return int(get_faker().phonenumber_prefix())


class IdCardInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    min_age: int = Field(18, ge=0, le=120, description="最小年龄")
    max_age: int = Field(90, ge=0, le=120, description="最大年龄")
    gender: Literal["M", "F"] | None = Field(None, description="M/F；缺省随机")


@register("id_card", name="身份证号", category="identity", inputs=IdCardInputs)
def id_card(
    *,
    min_age: int = 18,
    max_age: int = 90,
    gender: Literal["M", "F"] | None = None,
) -> str:
    return str(get_faker().ssn(min_age=min_age, max_age=max_age, gender=gender))


@register("boolean", name="布尔值", category="generic", returns="boolean")
def boolean() -> bool:
    return bool(get_faker().boolean())


def __getattr__(name: str):
    """Keep ``from tuner_testkit.fake.wrappers import person_name`` working for loop-bound names."""
    if name in globals():
        return globals()[name]
    raise AttributeError(name)
