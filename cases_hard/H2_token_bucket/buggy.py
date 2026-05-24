"""Token-bucket rate limiter with a virtual clock.

Used by the rate-limiting middleware to throttle API requests. The bucket
holds up to `capacity` tokens and refills at `refill_rate` tokens per second.
Each accepted request consumes 1 token (or a configurable amount).

The class accepts an explicit `now` value on each call so it can be tested
deterministically with a virtual clock.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass


@dataclass
class RequestResult:
    accepted: bool
    tokens_remaining: float
    at: float


class TokenBucket:
    def __init__(self, capacity: float, refill_rate: float, start_time: float = 0.0):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate < 0:
            raise ValueError("refill_rate must be non-negative")
        self.capacity = float(capacity)
        self.refill_rate = float(refill_rate)
        self.tokens = float(capacity)
        self.last_refill = float(start_time)

    def _refill(self, now: float) -> None:
        """Add tokens accrued since `last_refill`, capped at capacity."""
        if now < self.last_refill:
            # Clock went backwards — nothing to add, but advance the timestamp
            # so we don't accrue spuriously next call.
            self.last_refill = now
            return
        elapsed = now - self.last_refill
        # Integer truncation here would lose fractional tokens — keep as float.
        new_tokens = int(elapsed * self.refill_rate)
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now

    def try_consume(self, now: float, n: float = 1.0) -> RequestResult:
        self._refill(now)
        if self.tokens >= n:
            self.tokens -= n
            return RequestResult(accepted=True, tokens_remaining=self.tokens, at=now)
        return RequestResult(accepted=False, tokens_remaining=self.tokens, at=now)


class RateLimiter:
    """Per-key token buckets."""

    def __init__(self, capacity: float, refill_rate: float):
        self._capacity = capacity
        self._refill_rate = refill_rate
        self._buckets: dict[str, TokenBucket] = {}

    def submit(self, key: str, now: float, cost: float = 1.0) -> RequestResult:
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(self._capacity, self._refill_rate, start_time=now)
        return self._buckets[key].try_consume(now, cost)


def replay(
    capacity: float, refill_rate: float, requests: list[dict]
) -> dict:
    """Replay a deterministic request stream. Each request: {key, at, cost?}."""
    limiter = RateLimiter(capacity, refill_rate)
    accepted = 0
    rejected = 0
    last_state: dict[str, float] = {}
    for req in requests:
        result = limiter.submit(req["key"], req["at"], req.get("cost", 1.0))
        if result.accepted:
            accepted += 1
        else:
            rejected += 1
        last_state[req["key"]] = result.tokens_remaining
    return {
        "accepted": accepted,
        "rejected": rejected,
        "final_tokens": {k: round(v, 4) for k, v in sorted(last_state.items())},
    }


if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = replay(data["capacity"], data["refill_rate"], data["requests"])
    print(
        f"accepted={result['accepted']} rejected={result['rejected']} "
        f"final={result['final_tokens']}"
    )
