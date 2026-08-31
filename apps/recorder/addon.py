"""mitmproxy addon: filter static traffic and freeze API Objects live."""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from urllib.parse import urlsplit

from .capture import build_capture
from .freeze import ApiObjectFreezer, FreezeResult
from .mocks import MockSampleWriter
from .normalize import SKIP_METHODS, is_static_request


class ApiObjectRecorderAddon:
    """Capture eligible HTTP flows into route-aligned API Objects.

    When ``mock_writer`` is set, the same capture is also saved untruncated as a
    mock definition so ``apps.mock_server`` can replay the real payload.
    """

    def __init__(
        self,
        *,
        outputs_dir: Path,
        include_host: Optional[str] = None,
        verbose: bool = True,
        mock_writer: Optional[MockSampleWriter] = None,
    ) -> None:
        self.freezer = ApiObjectFreezer(outputs_dir)
        self.include_host = (include_host or "").strip().lower() or None
        self.verbose = verbose
        self.mock_writer = mock_writer
        self.stats = {
            "seen": 0,
            "skipped_static": 0,
            "skipped_host": 0,
            "skipped_method": 0,
            "frozen": 0,
            "mocks_written": 0,
            "mocks_skipped": 0,
        }
        self.results: list[FreezeResult] = []

    def _log(self, msg: str) -> None:
        if not self.verbose:
            return
        try:
            from packages.logging import log_info

            log_info(msg)
        except Exception:
            print(msg)

    def response(self, flow) -> None:  # mitmproxy http.HTTPFlow
        self.stats["seen"] += 1
        try:
            req = flow.request
            resp = flow.response
            if resp is None:
                return

            method = (req.method or "").upper()
            if method in SKIP_METHODS:
                self.stats["skipped_method"] += 1
                return

            url = req.pretty_url or req.url
            parts = urlsplit(url)
            host = parts.netloc.lower()
            path = parts.path or "/"

            if self.include_host and self.include_host not in host:
                self.stats["skipped_host"] += 1
                return

            req_ct = req.headers.get("Content-Type", "") or req.headers.get("content-type", "")
            resp_ct = resp.headers.get("Content-Type", "") or resp.headers.get("content-type", "")
            if is_static_request(path=path, content_type=req_ct, response_content_type=resp_ct):
                self.stats["skipped_static"] += 1
                return

            # Skip HTML document navigations (SPA shells); keep XHR/fetch APIs.
            if "text/html" in (resp_ct or "").lower() and method == "GET":
                self.stats["skipped_static"] += 1
                return

            capture = build_capture(
                method=method,
                url=url,
                request_headers=dict(req.headers),
                request_content=req.content,
                response_status=int(resp.status_code),
                response_headers=dict(resp.headers),
                response_content=resp.content,
            )
            result = self.freezer.freeze(capture)
            self.results.append(result)
            self.stats["frozen"] += 1
            self._log(
                f"[recorder] {result.action} {result.method} {result.normalized_path} -> {result.path}"
            )
            self._write_mock(capture, result)
        except Exception as exc:  # noqa: BLE001 — keep proxy alive on freeze errors
            self._log(f"[recorder] freeze error: {exc}")

    def _write_mock(self, capture, result: FreezeResult) -> None:
        """Side-car full-sample write. Never let it break the freeze path."""
        if self.mock_writer is None or result.action == "skipped":
            return
        try:
            written = self.mock_writer.write(capture, version=result.major)
        except Exception as exc:  # noqa: BLE001 — a mock write must not kill the proxy
            self.stats["mocks_skipped"] += 1
            self._log(f"[recorder] mock write error: {exc}")
            return
        if written.action == "skipped":
            self.stats["mocks_skipped"] += 1
        else:
            self.stats["mocks_written"] += 1
        self._log(f"[recorder] mock {written.action} {written.path} ({written.detail})")

    def done(self) -> None:
        summary = (
            "[recorder] done "
            f"seen={self.stats['seen']} frozen={self.stats['frozen']} "
            f"skipped_static={self.stats['skipped_static']} "
            f"skipped_host={self.stats['skipped_host']} "
            f"skipped_method={self.stats['skipped_method']}"
        )
        if self.mock_writer is not None:
            summary += (
                f" mocks_written={self.stats['mocks_written']} "
                f"mocks_skipped={self.stats['mocks_skipped']}"
            )
        self._log(summary)
