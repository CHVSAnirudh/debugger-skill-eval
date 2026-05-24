import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import TokenBucket, RateLimiter


def test_fractional_refill():
    b = TokenBucket(capacity=10, refill_rate=1.0, start_time=0.0)
    r1 = b.try_consume(now=0.0, n=10)
    assert r1.accepted is True
    assert r1.tokens_remaining == 0
    r2 = b.try_consume(now=0.5, n=1)
    assert r2.accepted is False
    assert abs(r2.tokens_remaining - 0.5) < 1e-9


def test_accumulated_small_refills():
    b = TokenBucket(capacity=10, refill_rate=2.0, start_time=0.0)
    # Drain
    b.try_consume(now=0.0, n=10)
    # 10 calls each spaced 0.1s -> 10 * 0.1 * 2.0 = 2 tokens accrued total
    last = None
    for i in range(1, 11):
        last = b.try_consume(now=i * 0.1, n=0)  # zero-cost ping just to refill
    assert abs(last.tokens_remaining - 2.0) < 1e-9


def test_refill_capped_at_capacity():
    b = TokenBucket(capacity=5, refill_rate=10.0, start_time=0.0)
    b.try_consume(now=0.0, n=5)  # drain
    r = b.try_consume(now=100.0, n=0)
    assert r.tokens_remaining == 5  # capped


def test_clock_backward_does_not_accrue():
    b = TokenBucket(capacity=10, refill_rate=1.0, start_time=10.0)
    b.try_consume(now=10.0, n=10)
    r = b.try_consume(now=5.0, n=0)
    assert r.tokens_remaining == 0  # no spurious refill


def test_rate_limiter_two_keys_independent():
    rl = RateLimiter(capacity=2, refill_rate=1.0)
    a1 = rl.submit("a", now=0.0)
    a2 = rl.submit("a", now=0.0)
    a3 = rl.submit("a", now=0.0)
    b1 = rl.submit("b", now=0.0)
    assert a1.accepted and a2.accepted and not a3.accepted
    assert b1.accepted  # b's bucket is untouched by a


def test_exact_refill_after_full_drain():
    b = TokenBucket(capacity=10, refill_rate=1.0, start_time=0.0)
    b.try_consume(now=0.0, n=10)
    # 5 seconds later -> 5 tokens
    r = b.try_consume(now=5.0, n=3)
    assert r.accepted
    assert abs(r.tokens_remaining - 2.0) < 1e-9
