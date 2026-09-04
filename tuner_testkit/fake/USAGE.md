# packages.fake

测试假数据：生成器只产 **1 条**；条数是 runner 的 `count`。CLI 与未来平台页共用 `list` / `describe` / `run` / `catalog`，业务代码直接调函数。

```python
from tuner_testkit.fake import udi, uscc, seed, run

seed(1)
code = udi(with_gs=True)  # str
codes = run("udi", count=10, inputs={"with_gs": True}).values
```

## CLI（手工临时数据）

```bash
uv run python -m tuner_testkit.fake list
uv run python -m tuner_testkit.fake describe udi
uv run python -m tuner_testkit.fake run udi --count 10 --set with_gs=true
uv run python -m tuner_testkit.fake run uscc --count 5 --seed 1
uv run python -m tuner_testkit.fake run udi --count 3 --params "{\"with_gs\": false}" --format json
uv run python -m tuner_testkit.fake catalog --out -
```

默认一行一条，方便粘贴。含 GS 的 UDI 把 ASCII 29 显示成 `\x1d`（`--gs-repr raw` 才输出真字节）。`count` 上限 1000；不用 `amount`（本仓里表示金额）。

| CLI | `run()` |
| --- | --- |
| 位置参数 `fake_id` | `fake_id` |
| `--count N` | `count` |
| `--params JSON` / `--params-file` | `inputs` |
| `--set k=v`（可重复，覆盖 params） | 写入 `inputs` |
| `--seed N` | `seed` |
| `--unique` / `--no-unique` | `unique`（默认开） |

## 业务代码

`db_seed` / pytest 调单值函数，不要把 `count` 传进 `udi()`。随机值统一 `tuner_testkit.fake.seed(n)`（同时种 Faker 与 `random`）。

解析 / 校验是工具函数，不进「造 N 条」catalog：`parse_udi`、`strip_gs`、`is_valid_uscc`。

Faker 未提升为一等公民的方法走 `tuner_testkit.fake.raw`（已 seed 的 `Faker("zh_CN")`），例如 `raw.user_agent()`。

`ean13` / `ean8` 是零售条码，**不是**医疗 DI/UDI。

## 医疗 / 中国（自研）

| fake_id | 要点 |
| --- | --- |
| `sn_code` | 独立序列号，默认 21 位；`alphabet=hex` 可 4 位对齐 SQL |
| `unique_code` | 短码，默认 10 位；可 `snowflake_id` |
| `product_di` | 14 位 DI，默认 GTIN-14 校验位 |
| `udi` | `01+DI+11+17+10+lot[+GS]+21+sn`；`with_gs` |
| `uscc` | GB 32100-2015 18 位含校验 |
| `company_name` | `kind=generic\|medical_device\|hospital` |
| `registration_no` | `国械注{准\|许}{年}{8位}` |

完整目录：`python -m tuner_testkit.fake catalog`。
