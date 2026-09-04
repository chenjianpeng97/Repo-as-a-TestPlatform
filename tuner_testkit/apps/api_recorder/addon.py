"""mitmproxy addon: filter static traffic and freeze API Objects live."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from tuner_testkit.api_objects.recording import ApiCapturePipeline, MockSampleWriter
from tuner_testkit.api_objects.recording.freeze import FreezeResult


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
        self.pipeline = ApiCapturePipeline(
            outputs_dir=outputs_dir,
            include_host=include_host,
            verbose=verbose,
            mock_writer=mock_writer,
            tool="api_recorder",
            log_prefix="api_recorder",
        )
        self.freezer = self.pipeline.freezer
        self.include_host = self.pipeline.include_host
        self.verbose = verbose
        self.mock_writer = mock_writer

    @property
    def stats(self) -> dict:
        return self.pipeline.stats

    @property
    def results(self) -> list[FreezeResult]:
        return self.pipeline.results

    def response(self, flow) -> None:  # mitmproxy http.HTTPFlow
        try:
            req = flow.request
            resp = flow.response
            if resp is None:
                return
            self.pipeline.ingest(
                method=req.method or "",
                url=req.pretty_url or req.url,
                request_headers=dict(req.headers),
                request_content=req.content,
                response_status=int(resp.status_code),
                response_headers=dict(resp.headers),
                response_content=resp.content,
            )
        except Exception as exc:  # noqa: BLE001 — keep proxy alive on freeze errors
            self.pipeline._log(f"[api_recorder] freeze error: {exc}")

    def done(self) -> None:
        self.pipeline.done()
