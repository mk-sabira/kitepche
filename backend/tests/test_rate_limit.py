from app.core.rate_limit import RateLimiter


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now


def test_allows_requests_up_to_the_limit():
    limiter = RateLimiter(max_requests=3, window_seconds=60, clock=FakeClock())
    assert [limiter.check("a") for _ in range(3)] == [None, None, None]


def test_refuses_the_request_over_the_limit_and_says_how_long_to_wait():
    clock = FakeClock()
    limiter = RateLimiter(max_requests=2, window_seconds=60, clock=clock)
    limiter.check("a")
    limiter.check("a")
    clock.now = 10
    assert limiter.check("a") == 50


def test_users_are_counted_separately():
    limiter = RateLimiter(max_requests=1, window_seconds=60, clock=FakeClock())
    assert limiter.check("a") is None
    assert limiter.check("a") is not None
    assert limiter.check("b") is None


def test_requests_are_allowed_again_after_the_window():
    clock = FakeClock()
    limiter = RateLimiter(max_requests=1, window_seconds=60, clock=clock)
    assert limiter.check("a") is None
    assert limiter.check("a") is not None
    clock.now = 60
    assert limiter.check("a") is None