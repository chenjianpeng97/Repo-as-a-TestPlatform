"""China business identifiers: USCC, company / hospital names, org codes."""
from __future__ import annotations

import random
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from tuner_testkit.fake.catalog import register
from tuner_testkit.fake.core import digits, get_faker

# GB 32100-2015：不含 I O Z S V
_USCC_CHARS = "0123456789ABCDEFGHJKLMNPQRTUWXY"
_USCC_WEIGHTS = (1, 3, 9, 27, 19, 26, 16, 17, 20, 29, 25, 13, 8, 24, 10, 30, 28)
_REGIONS = (
    "110000",
    "310000",
    "320000",
    "330000",
    "340000",
    "350000",
    "420000",
    "440000",
    "440300",
    "510000",
)
_CITIES = (
    "珠海",
    "无锡",
    "北京",
    "上海",
    "广州",
    "深圳",
    "宿州",
    "成都",
    "杭州",
    "南京",
    "苏州",
    "武汉",
)
_MED_DOMAINS = ("医疗器械", "生物科技", "医用材料", "医疗科技", "生物医药")
_CO_SUFFIXES = ("有限公司", "股份有限公司")
_HOSPITAL_KINDS = ("人民医院", "中心医院", "中医院", "妇幼保健院")


def uscc_check_char(body17: str) -> str:
    if len(body17) != 17:
        raise ValueError("USCC 主体必须是 17 位")
    total = 0
    for i, ch in enumerate(body17):
        try:
            idx = _USCC_CHARS.index(ch)
        except ValueError as exc:
            raise ValueError(f"非法 USCC 字符: {ch!r}") from exc
        total += idx * _USCC_WEIGHTS[i]
    checksum = 31 - (total % 31)
    if checksum == 31:
        return "0"
    return _USCC_CHARS[checksum]


def is_valid_uscc(value: str) -> bool:
    text = value.strip().upper()
    if len(text) != 18:
        return False
    try:
        return uscc_check_char(text[:17]) == text[17]
    except ValueError:
        return False


class UsccInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    region: str | None = Field(None, description="6 位行政区划；缺省随机")


@register("uscc", name="统一社会信用代码", category="china", inputs=UsccInputs)
def uscc(*, region: str | None = None) -> str:
    area = region or random.choice(_REGIONS)
    if len(area) != 6 or not area.isdigit():
        raise ValueError("region 必须是 6 位数字行政区划")
    org = "".join(random.choices(_USCC_CHARS, k=9))
    body = f"91{area}{org}"
    return body + uscc_check_char(body)


class CompanyNameInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["generic", "medical_device", "hospital"] = Field(
        "generic",
        description="generic=Faker 通用公司名；medical_device=器械企业；hospital=医院",
    )


@register(
    "company_name",
    name="公司/医院名称",
    category="china",
    inputs=CompanyNameInputs,
    example={"kind": "medical_device"},
)
def company_name(*, kind: Literal["generic", "medical_device", "hospital"] = "generic") -> str:
    if kind == "generic":
        return str(get_faker().company())
    city = random.choice(_CITIES)
    if kind == "hospital":
        suffix = random.choice(("", "有限公司"))
        return f"{city}{random.choice(_HOSPITAL_KINDS)}{suffix}"
    return f"{city}{random.choice(_MED_DOMAINS)}{random.choice(_CO_SUFFIXES)}"


class OrgCodeInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    length: int = Field(10, ge=4, le=20, description="编码位数")


@register("org_code", name="机构编码", category="china", inputs=OrgCodeInputs)
def org_code(*, length: int = 10) -> str:
    return digits(length)


def distributor_code(*, length: int = 10) -> str:
    return org_code(length=length)


def hospital_code(*, length: int = 10) -> str:
    return org_code(length=length)


class ErpProductCodeInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start: int | None = Field(None, description="起点；缺省 18 位 9e17")
    seq: int = Field(0, ge=0, description="序号偏移")


@register("erp_product_code", name="ERP 产品编码", category="china", inputs=ErpProductCodeInputs)
def erp_product_code(*, start: int | None = None, seq: int = 0) -> str:
    base = 900_000_000_000_000_000 if start is None else start
    return str(base + seq)[:30]
