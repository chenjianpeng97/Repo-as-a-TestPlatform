"""Offline API capture / freeze kernel (no Playwright, no mitmproxy).

Protocol adapters live in apps: ``apps.api_recorder`` (HTTP proxy) and
``apps.recorder`` (headed Playwright tap). Both call into this package.
"""

from __future__ import annotations

from .capture import Capture, build_capture
from .codegen import render_api_model_source, truncate_sample
from .freeze import ApiObjectFreezer, FreezeResult
from .mocks import MockSampleWriter, MockWriteResult
from .normalize import (
    SKIP_METHODS,
    is_static_request,
    normalize_path,
    skip_api_flow,
)
from .pipeline import ApiCapturePipeline

__all__ = [
    "ApiCapturePipeline",
    "ApiObjectFreezer",
    "Capture",
    "FreezeResult",
    "MockSampleWriter",
    "MockWriteResult",
    "SKIP_METHODS",
    "build_capture",
    "is_static_request",
    "normalize_path",
    "render_api_model_source",
    "skip_api_flow",
    "truncate_sample",
]
