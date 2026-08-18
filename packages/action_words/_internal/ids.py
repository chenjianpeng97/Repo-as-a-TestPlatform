"""Client-side monotonic bigint id generation for data factories.

Capacity-test injection needs to control parent/child ids *before* hitting the
database so that a whole batch (parent rows + child rows) can be inserted with
``executemany`` while keeping the foreign-key linkage correct. We therefore do
not rely on MySQL ``auto_increment`` / ``lastrowid`` for linkage; instead we
mint ids here with a small snowflake-style scheme::

    id = (elapsed_ms << 20) | sequence

- ``elapsed_ms`` is milliseconds since a fixed epoch (2025-01-01 UTC), so the
  high bits keep increasing over time and stay comfortably inside MySQL
  ``bigint`` range.
- ``sequence`` is a 20-bit per-millisecond counter (up to 1,048,576 ids/ms);
  when it overflows we spin to the next millisecond, so ids are strictly
  monotonically increasing and unique within a process.

The generated ids visually resemble the sample data (e.g.
``2070119332155711489``) while remaining unique across a run.
"""
from __future__ import annotations

import threading
import time

# Fixed epoch: 2025-01-01T00:00:00Z in milliseconds.
_EPOCH_MS = 1_735_689_600_000
_SEQ_BITS = 20
_SEQ_MASK = (1 << _SEQ_BITS) - 1


class IdGenerator:
    """Thread-safe, strictly increasing bigint id generator."""

    def __init__(self, *, epoch_ms: int = _EPOCH_MS) -> None:
        self._epoch_ms = epoch_ms
        self._lock = threading.Lock()
        self._last_ms = -1
        self._seq = 0

    def _now_ms(self) -> int:
        return int(time.time() * 1000) - self._epoch_ms

    def next(self) -> int:
        """Return the next unique, monotonically increasing bigint id."""
        with self._lock:
            now = self._now_ms()
            if now == self._last_ms:
                self._seq = (self._seq + 1) & _SEQ_MASK
                if self._seq == 0:
                    # Sequence exhausted within this ms: wait for the next ms.
                    while now <= self._last_ms:
                        now = self._now_ms()
            else:
                self._seq = 0
            self._last_ms = now
            return (now << _SEQ_BITS) | self._seq

    def next_batch(self, n: int) -> list[int]:
        """Return ``n`` unique ids in increasing order."""
        if n < 0:
            raise ValueError("n must be >= 0")
        return [self.next() for _ in range(n)]


# Process-wide default shared by all factories so a single run never collides
# parent and child ids across different factory instances.
default_id_generator = IdGenerator()


def next_id() -> int:
    """Convenience wrapper around the process-wide default generator."""
    return default_id_generator.next()


def next_ids(n: int) -> list[int]:
    """Convenience wrapper returning ``n`` ids from the default generator."""
    return default_id_generator.next_batch(n)
