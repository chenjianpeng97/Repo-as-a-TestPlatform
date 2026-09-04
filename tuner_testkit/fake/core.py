"""Seed, Faker instance, and generic (non-domain) generators."""
from __future__ import annotations

import random
import string
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from faker import Faker
from pydantic import BaseModel, ConfigDict, Field

from tuner_testkit.fake.catalog import register

_faker: Faker | None = None


def get_faker() -> Faker:
    global _faker
    if _faker is None:
        _faker = Faker("zh_CN")
    return _faker


class _RawProxy:
    """Pass-through to the seeded ``Faker('zh_CN')`` instance."""

    def __getattr__(self, name: str) -> object:
        return getattr(get_faker(), name)


raw = _RawProxy()


def seed(value: int) -> None:
    """Seed stdlib ``random`` and Faker together for reproducible runs."""
    random.seed(value)
    Faker.seed(value)
    get_faker().seed_instance(value)


def now() -> datetime:
    return datetime.now()


def now_str() -> str:
    return now().strftime("%Y-%m-%d %H:%M:%S")


def today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def date_str(d: date) -> str:
    return d.strftime("%Y-%m-%d")


def _parse_bound(value: str, *, end_of_day: bool) -> datetime:
    text = value.strip()
    if len(text) <= 10:
        d = date.fromisoformat(text[:10])
        if end_of_day:
            return datetime(d.year, d.month, d.day, 23, 59, 59)
        return datetime(d.year, d.month, d.day, 0, 0, 0)
    return datetime.strptime(text[:19], "%Y-%m-%d %H:%M:%S")


def resolve_timestamp(start: str | None = None, end: str | None = None) -> str:
    """Pick ``YYYY-MM-DD HH:MM:SS`` in ``[start, end]``, or ``now_str()``."""
    if start and end:
        low = _parse_bound(start, end_of_day=False)
        high = _parse_bound(end, end_of_day=True)
        if high < low:
            low, high = high, low
        span = (high - low).total_seconds()
        picked = low + timedelta(seconds=random.uniform(0, span))
        return picked.strftime("%Y-%m-%d %H:%M:%S")
    if start or end:
        raise ValueError("start 与 end 必须同时给出")
    return now_str()


def resolve_date(start: str | None = None, end: str | None = None) -> str:
    return resolve_timestamp(start, end)[:10]


class DigitsInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    n: int = Field(10, ge=1, le=64, description="位数")


@register("digits", name="数字串", category="generic", inputs=DigitsInputs, example={"n": 10})
def digits(n: int = 10) -> str:
    return "".join(random.choices(string.digits, k=n))


class PastDateInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    max_days_ago: int = Field(365, ge=0, description="最多多少天前")
    min_days_ago: int = Field(0, ge=0, description="至少多少天前")


@register(
    "random_past_date",
    name="过去日期",
    category="generic",
    inputs=PastDateInputs,
    returns="string",
)
def random_past_date(*, max_days_ago: int = 365, min_days_ago: int = 0) -> date:
    delta = random.randint(min_days_ago, max_days_ago)
    return date.today() - timedelta(days=delta)


past_date = random_past_date


class FutureDateInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    min_days: int = Field(30, ge=0, description="至少多少天后")
    max_days: int = Field(1095, ge=1, description="最多多少天后")


@register("random_future_date", name="未来日期", category="generic", inputs=FutureDateInputs)
def random_future_date(*, min_days: int = 30, max_days: int = 1095) -> date:
    return date.today() + timedelta(days=random.randint(min_days, max_days))


future_date = random_future_date


class DateBetweenInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    start: str | None = Field(None, description="起点 YYYY-MM-DD")
    end: str | None = Field(None, description="终点 YYYY-MM-DD")


@register("date_between", name="区间日期", category="generic", inputs=DateBetweenInputs)
def date_between(*, start: str | None = None, end: str | None = None) -> date:
    faker = get_faker()
    if start and end:
        return faker.date_between(
            start_date=date.fromisoformat(start[:10]),
            end_date=date.fromisoformat(end[:10]),
        )
    return faker.date_between()


@register("date_time_between", name="区间时间", category="generic", inputs=DateBetweenInputs)
def date_time_between(*, start: str | None = None, end: str | None = None) -> datetime:
    faker = get_faker()
    if start and end:
        return faker.date_time_between(
            start_date=_parse_bound(start, end_of_day=False),
            end_date=_parse_bound(end, end_of_day=True),
        )
    return faker.date_time_between()


class MoneyInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    low: float = Field(10.0, description="下限")
    high: float = Field(100000.0, description="上限")
    places: int = Field(2, ge=0, le=6, description="小数位")


@register("money", name="金额", category="generic", inputs=MoneyInputs, returns="number")
def money(low: float = 10.0, high: float = 100000.0, *, places: int = 2) -> Decimal:
    raw_n = Decimal(str(random.uniform(low, high)))
    quant = Decimal(10) ** -places
    return raw_n.quantize(quant, rounding=ROUND_HALF_UP)


class QtyInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    low: int = Field(1, description="下限")
    high: int = Field(100, description="上限")


@register("qty", name="数量", category="generic", inputs=QtyInputs, returns="number")
def qty(low: int = 1, high: int = 100) -> int:
    return random.randint(low, high)


class HexIdInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    length: int = Field(32, ge=1, le=64, description="hex 字符数")


@register("hex_id", name="无连字符 hex id", category="generic", inputs=HexIdInputs, example={"length": 32})
def hex_id(*, length: int = 32) -> str:
    return "".join(random.choices("0123456789abcdef", k=length))


@register("task_id", name="任务 ID（32 hex）", category="generic")
def task_id() -> str:
    return hex_id(length=32)


class DocNoInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prefix: str = Field("DOC", description="前缀")
    snowflake_id: int | None = Field(None, description="有则拼接为 prefix-snowflake")


@register("doc_no", name="单据号", category="generic", inputs=DocNoInputs, example={"prefix": "DOC"})
def doc_no(prefix: str = "DOC", *, snowflake_id: int | None = None) -> str:
    if snowflake_id is not None:
        return f"{prefix}-{snowflake_id}"
    return f"{prefix}-{digits(19)}"


@register("sales_no", name="销售单号", category="generic")
def sales_no() -> str:
    return doc_no()


class ApplyCodeInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prefix: str = Field("ASQ", description="申请编号前缀")


@register("apply_code", name="审批申请编号", category="generic", inputs=ApplyCodeInputs)
def apply_code(*, prefix: str = "ASQ") -> str:
    return f"{prefix}{digits(10)}-{digits(4)}"


class AuthorizationNoInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    prefix: str = Field("JF", description="授权号前缀")


@register("authorization_no", name="授权结果编号", category="generic", inputs=AuthorizationNoInputs)
def authorization_no(*, prefix: str = "JF") -> str:
    return f"{prefix}-{digits(12)}SQ"


@register("tender_apply_code", name="投标授权申请编号", category="generic")
def tender_apply_code() -> str:
    return f"ATB{date.today().strftime('%Y%m')}{digits(4)}"


@register("dd_no", name="建档/开户流水号", category="generic")
def dd_no() -> str:
    return f"{now().strftime('%y%m%d%H%M')}-{digits(4)}"


@register("distributor_code_temp", name="临时经销商编码", category="generic")
def distributor_code_temp() -> str:
    return now().strftime("%y%m%d%H%M")


@register("shipment_no", name="厂家发货号", category="generic")
def shipment_no() -> str:
    return digits(10)


@register("factory_order_no", name="厂家订单号", category="generic")
def factory_order_no() -> str:
    return digits(10)


class FactoryDocdtlNoInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    shipment_no: str | None = Field(None, description="发货号；缺省随机 10 位")
    unique_code: str | None = Field(None, description="唯一码；缺省随机 10 位")


@register(
    "factory_docdtl_no",
    name="厂家发货行键",
    category="generic",
    inputs=FactoryDocdtlNoInputs,
)
def factory_docdtl_no(*, shipment_no: str | None = None, unique_code: str | None = None) -> str:
    ship = shipment_no or digits(10)
    code = unique_code or digits(10)
    return f"{ship}_{digits(6)}_{code}"


class InvoiceNoInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    digits: int = Field(8, ge=1, le=20, description="无雪花时的位数")
    snowflake_id: int | None = Field(None, description="有则生成 12 位防撞发票号")


@register("invoice_no", name="发票号码", category="generic", inputs=InvoiceNoInputs)
def invoice_no(*, snowflake_id: int | None = None, digits: int = 8) -> str:
    if snowflake_id is not None:
        return str(snowflake_id % 10**12).zfill(12)
    return "".join(random.choices(string.digits, k=digits))


class SnowflakeOptInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    snowflake_id: int | None = Field(None, description="可选雪花 id，用于防撞")


@register("invoice_code", name="发票代码", category="generic", inputs=SnowflakeOptInputs)
def invoice_code(*, snowflake_id: int | None = None) -> str:
    if snowflake_id is not None:
        return str((snowflake_id // 10) % 10**12).zfill(12)
    return digits(12)


@register("verify_code", name="发票校验码后 6 位", category="generic")
def verify_code() -> str:
    return digits(6)


def sales_year(d: date | None = None) -> str:
    return (d or date.today()).strftime("%Y")


def sales_month(d: date | None = None) -> str:
    return (d or date.today()).strftime("%Y-%m")


class TextLenInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nb_sentences: int = Field(3, ge=1, le=20, description="句数（paragraph）")


# lorem wrappers that need a tiny input live here so wrappers.py stays EmptyInputs-heavy
class SentenceInputs(BaseModel):
    model_config = ConfigDict(extra="forbid")
    nb_words: int = Field(6, ge=1, le=40, description="词数")


@register("sentence", name="占位句子", category="text", inputs=SentenceInputs)
def sentence(*, nb_words: int = 6) -> str:
    return get_faker().sentence(nb_words=nb_words)


@register("paragraph", name="占位段落", category="text", inputs=TextLenInputs)
def paragraph(*, nb_sentences: int = 3) -> str:
    return get_faker().paragraph(nb_sentences=nb_sentences)


@register("text", name="占位文本", category="text")
def text() -> str:
    return get_faker().text()
