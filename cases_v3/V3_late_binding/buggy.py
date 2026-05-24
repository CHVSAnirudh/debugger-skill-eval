"""Feature-flag rollout decision engine.

Each feature has an integer rollout threshold in [0, 100]. A user is in the
rollout for feature F if hash(user_id) % 100 < threshold(F).

The engine pre-builds one predicate per feature and runs each predicate
against incoming user hashes. The predicates are reused across many users,
so building them once is the right shape.
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import dataclass


@dataclass
class Feature:
    name: str
    threshold: int  # 0..100 — % of users rolled in


def user_bucket(user_id: str) -> int:
    """Stable hash bucket in [0, 100) derived from user_id."""
    h = hashlib.sha256(user_id.encode()).hexdigest()
    return int(h, 16) % 100


def build_predicates(features: list[Feature]) -> list:
    """Return one predicate per feature. predicate(bucket) -> bool."""
    return [lambda bucket: bucket < f.threshold for f in features]


def evaluate(user_id: str, features: list[Feature]) -> dict[str, bool]:
    bucket = user_bucket(user_id)
    predicates = build_predicates(features)
    result = {}
    for feat, pred in zip(features, predicates):
        result[feat.name] = pred(bucket)
    return result


def evaluate_many(user_ids: list[str], features: list[Feature]) -> list[dict]:
    return [{"user_id": uid, "flags": evaluate(uid, features)} for uid in user_ids]


def main() -> None:
    data = json.load(sys.stdin)
    features = [Feature(name=f["name"], threshold=int(f["threshold"])) for f in data["features"]]
    results = evaluate_many(data["user_ids"], features)
    lines = []
    for r in results:
        flag_str = " ".join(f"{k}={int(v)}" for k, v in r["flags"].items())
        lines.append(f"{r['user_id']}: {flag_str}")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
