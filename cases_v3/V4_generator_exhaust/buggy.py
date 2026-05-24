"""Sales report generator.

Pulls transactions, filters to a date range, and reports several aggregates
over the filtered set. Filtering is implemented as a lazy pipeline using
generator expressions so we don't materialize the full list in memory.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Iterator
from dataclasses import dataclass


@dataclass
class Transaction:
    customer_id: str
    amount: float
    day: int  # day-of-year


def filter_window(
    transactions: list[Transaction], start: int, end: int
) -> Iterator[Transaction]:
    """Yield transactions with start <= day <= end."""
    return (t for t in transactions if start <= t.day <= end)


def report(transactions: list[Transaction], start: int, end: int) -> dict:
    """Return aggregates over the filtered window."""
    window = filter_window(transactions, start, end)
    total = sum(t.amount for t in window)
    count = sum(1 for _ in window)
    max_amount = max((t.amount for t in window), default=0.0)
    customers = {t.customer_id for t in window}
    return {
        "total": round(total, 2),
        "count": count,
        "max": round(max_amount, 2),
        "unique_customers": len(customers),
    }


def main() -> None:
    data = json.load(sys.stdin)
    txs = [Transaction(**t) for t in data["transactions"]]
    r = report(txs, data["start"], data["end"])
    print(
        f"total={r['total']} count={r['count']} "
        f"max={r['max']} unique_customers={r['unique_customers']}"
    )


if __name__ == "__main__":
    main()
