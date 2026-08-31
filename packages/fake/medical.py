"""Medical-device generators: SN / DI / UDI / registration / names."""
from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from packages.fake.catalog import GS, register
from packages.fake.core import digits, random_future_date, random_past_date

_DEVICE_STEMS = (
    "一次性使用血液灌流器",
    "一次性使用血浆胆红素吸附器",
    "一次性使用体外循环血路",
    "血液透析浓缩液",
    "一次性使用无菌注射器",
    "医用外科口罩",
    "一次性使用输液器",
)
_DEVICE_LANG = ("中文", "无菌液路", "MDR三年效期", "出口")
_MODELS = ("HA100", "HA130", "HA150", "HA280", "HA330", "BS80", "BS330", "ET-2", "CAP")


def _yyMMdd(d: date) -> str:
    return d.strftime("%y%m%d")


def gtin14_check_digit(body13: str) -> str:
    """GS1 check digit for a 13-digit GTIN-14 body."""
    if len(body13) != 13 or not body13.isdigit():
        raise ValueError("GTIN-14 body 必须是 13 位数字")
    total = 0
    for i, ch in enumerate(reversed(body13)):
        total += int(ch) * (3 if i % 2 == 0 else 1)
    return str((10 - (total % 10)) % 10)


class SnCodeInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    length: int = Field(21, ge=1, le=30, description="独立序列号位数（默认 21）")
    alphabet: Literal["digits", "hex"] = Field("digits", description="字符集")


@register("sn_code", name="医疗产品独立序列号", category="medical", inputs=SnCodeInputs, example={"length": 21})
def sn_code(*, length: int = 21, alphabet: Literal["digits", "hex"] = "digits") -> str:
    if alphabet == "hex":
        return "".join(random.choices("0123456789ABCDEF", k=length))
    return digits(length)


class UniqueCodeInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    length: int = Field(10, ge=1, le=30, description="短唯一码位数（健帆库存多为 10）")
    snowflake_id: int | None = Field(None, description="有则按雪花派生防撞；CLI 可空")


@register("unique_code", name="短唯一码", category="medical", inputs=UniqueCodeInputs)
def unique_code(*, snowflake_id: int | None = None, length: int = 10) -> str:
    if snowflake_id is not None:
        return str(snowflake_id % 10**length).zfill(length)
    return digits(length)


class ProductDiInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    product_code: str | None = Field(None, description="可选；用 MD5 派生 14 位 DI")
    check_digit: bool = Field(True, description="是否按 GTIN-14 计算校验位")


@register("product_di", name="14 位产品 DI", category="medical", inputs=ProductDiInputs)
def product_di(*, product_code: str | None = None, check_digit: bool = True) -> str:
    if product_code:
        digest = hashlib.md5(product_code.encode("utf-8")).hexdigest()  # noqa: S324
        n = (int(digest[:12], 16) % 90_000_000_000_000) + 10_000_000_000_000
        body = str(n).zfill(14)[:13]
    else:
        body = digits(13)
    if check_digit:
        return body + gtin14_check_digit(body)
    return body + digits(1)


def _normalize_batch_number(batch: str, length: int = 10) -> str:
    if len(batch) >= length:
        return batch[-length:]
    return batch.zfill(length)


class BatchNumberInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    length: int = Field(10, ge=1, le=20, description="批号位数")
    snowflake_id: int | None = Field(None, description="可选雪花派生")


@register("batch_number", name="生产批号", category="medical", inputs=BatchNumberInputs)
def batch_number(*, snowflake_id: int | None = None, length: int = 10) -> str:
    if snowflake_id is not None:
        return str(snowflake_id % 10**length).zfill(length)
    return digits(length)


class UdiInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    with_gs: bool = Field(True, description="是否在 AI(10) 与 AI(21) 之间插入 GS (ASCII 29)")
    di: str | None = Field(None, description="14 位产品 DI；缺省随机")
    production_date: date | None = Field(None, description="生产日期")
    expiry_date: date | None = Field(None, description="失效日期")
    batch_number: str | None = Field(None, description="批号；缺省 10 位")
    serial: str | None = Field(None, description="AI(21) 序列号；缺省按 serial_length 生成")
    serial_length: int = Field(21, ge=1, le=30, description="独立序列号位数")


@register("udi", name="完整 UDI 码", category="medical", inputs=UdiInputs, example={"with_gs": True})
def udi(
    *,
    with_gs: bool = True,
    di: str | None = None,
    production_date: date | None = None,
    expiry_date: date | None = None,
    batch_number: str | None = None,
    serial: str | None = None,
    serial_length: int = 21,
) -> str:
    device_id = di if di is not None else product_di()
    if len(device_id) != 14 or not device_id.isdigit():
        raise ValueError("di 必须是 14 位数字")
    prod = production_date or random_past_date(max_days_ago=365)
    exp = expiry_date or random_future_date(min_days=365, max_days=1095)
    lot = _normalize_batch_number(
        batch_number if batch_number is not None else digits(10)
    )
    serial_value = serial if serial is not None else digits(serial_length)
    fixed = f"01{device_id}11{_yyMMdd(prod)}17{_yyMMdd(exp)}10{lot}"
    if with_gs:
        return f"{fixed}{GS}21{serial_value}"
    return f"{fixed}21{serial_value}"


def serial_number(
    *,
    di: str | None = None,
    production_date: date | None = None,
    expiry_date: date | None = None,
    batch_number: str | None = None,
    unique_serial: str | None = None,
    unique_serial_digits: int = 10,
) -> str:
    """Jafron ``generators.serial_number`` alias → ``udi(with_gs=True)``."""
    return udi(
        with_gs=True,
        di=di,
        production_date=production_date,
        expiry_date=expiry_date,
        batch_number=batch_number,
        serial=unique_serial,
        serial_length=unique_serial_digits,
    )


def strip_gs(value: str) -> str:
    return value.replace(GS, "")


@dataclass(frozen=True, slots=True)
class UdiParts:
    di: str
    production_yymmdd: str
    expiry_yymmdd: str
    batch_number: str
    serial: str
    with_gs: bool
    raw: str


def parse_udi(value: str) -> UdiParts:
    """Parse ``01…11…17…10…[GS]21…`` produced by :func:`udi`."""
    text = value.replace("\n", "")
    with_gs = GS in text
    body = text.replace(GS, "")
    if not body.startswith("01") or len(body) < 34:
        raise ValueError("不是可识别的 UDI 字符串")
    di = body[2:16]
    if body[16:18] != "11" or body[24:26] != "17" or body[32:34] != "10":
        raise ValueError("UDI 固定 AI 布局不是 01/11/17/10")
    prod = body[18:24]
    exp = body[26:32]
    rest = body[34:]
    marker = rest.rfind("21")
    if marker < 0:
        raise ValueError("UDI 缺少 AI(21)")
    lot = rest[:marker]
    serial = rest[marker + 2 :]
    return UdiParts(
        di=di,
        production_yymmdd=prod,
        expiry_yymmdd=exp,
        batch_number=lot,
        serial=serial,
        with_gs=with_gs,
        raw=value,
    )


class RegistrationNoInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: Literal["准", "许"] = Field("许", description="国械注准 / 国械注许")


@register("registration_no", name="医疗器械注册证号", category="medical", inputs=RegistrationNoInputs)
def registration_no(*, kind: Literal["准", "许"] = "许") -> str:
    return f"国械注{kind}{date.today().year}{digits(8)}"


class MedicalNameInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    seq: int | None = Field(None, description="容量造数序号；有则加 CAP 后缀")


@register("medical_device_name", name="医疗器械产品名称", category="medical", inputs=MedicalNameInputs)
def medical_device_name(*, seq: int | None = None) -> str:
    stem = random.choice(_DEVICE_STEMS)
    model = random.choice(_MODELS)
    lang = random.choice(_DEVICE_LANG)
    if seq is not None:
        return f"容量测试产品,CAP{seq:06d}"
    return f"{stem},{model},{lang}"


@register("product_model", name="医疗器械型号", category="medical", inputs=MedicalNameInputs)
def product_model(*, seq: int | None = None) -> str:
    if seq is not None:
        return f"CAP{seq:06d}"
    return random.choice(_MODELS)
