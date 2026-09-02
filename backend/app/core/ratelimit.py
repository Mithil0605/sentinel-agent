from __future__ import annotations

import time
from collections import defaultdict, deque


class SlidingWindowRateLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = limit
        self.window = window_seconds
        self._hits: dict[str, deque] = defaultdict(deque)

    def __call__(self, key: str) -> tuple[bool, int]:
        now = time.monotonic()
        q = self._hits[key]
        while q and now - q[0] >= self.window:
            q.popleft()
        if len(q) >= self.limit:
            retry_after = int(self.window - (now - q[0])) + 1
            return False, retry_after
        q.append(now)
        return True, 0
