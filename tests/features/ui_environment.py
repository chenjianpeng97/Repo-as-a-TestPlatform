from __future__ import annotations

# behave stage-mode: `behave --stage ui` loads hooks from `tests/features/ui_environment.py`.

from datetime import datetime
from pathlib import Path


def _get_playwright_page(context):
    # 约定：UI 自动化执行层将 Playwright Page 放入 context.page（或 context.pw_page）。
    for attr in ("page", "pw_page", "playwright_page"):
        page = getattr(context, attr, None)
        if page is not None:
            return page
    return None


def after_step(context, step):
    if step.status != "failed":
        return

    page = _get_playwright_page(context)
    if page is None:
        return

    ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    safe_step = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in step.name)[:80]
    out_dir = Path("artifacts/playwright/screenshots")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"ui_failed_step_{ts}_{safe_step}.png"

    try:
        page.screenshot(path=str(out_path), full_page=True)
    except Exception:
        # 截图不应让用例二次失败；真正失败原因在 step 的断言/异常里
        return

