import math
import time
from collections import defaultdict, deque
from threading import Lock


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int, clock=time.monotonic):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._clock = clock
        self._hits = defaultdict(deque)
        self._lock = Lock()

    def check(self, key) -> int | None:
        """Record a request. Returns None if allowed, or the seconds to wait if over the limit."""
        now = self._clock()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] >= self.window_seconds:
                hits.popleft()
            if len(hits) >= self.max_requests:
                return math.ceil(self.window_seconds - (now - hits[0]))
            hits.append(now)
            return None
