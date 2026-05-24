"""Daily transactions summarizer.

Reads transactions.csv (columns: customer_id, date, amount, currency),
computes the total spend per customer, and prints the top 5 customers
by total spend.

The script used to work fine. After today's nightly job, it started crashing.
The CSV format from the upstream system supposedly hasn't changed.
"""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from pathlib import Path


CSV_PATH = Path(__file__).parent / "transactions.csv"


def parse_amount(raw: str) -> float:
    """Convert the amount column to a float."""
    return float(raw)


def load_transactions(path: Path) -> list[dict]:
    transactions = []
    with path.open(newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["amount"] = parse_amount(row["amount"])
            transactions.append(row)
    return transactions


def totals_by_customer(transactions: list[dict]) -> dict[str, float]:
    totals: dict[str, float] = defaultdict(float)
    for t in transactions:
        totals[t["customer_id"]] += t["amount"]
    return dict(totals)


def top_customers(totals: dict[str, float], n: int = 5) -> list[tuple[str, float]]:
    return sorted(totals.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def format_report(top: list[tuple[str, float]]) -> str:
    lines = ["Top 5 customers by total spend:"]
    for cust, total in top:
        lines.append(f"  {cust}: ${total:.2f}")
    return "\n".join(lines)


def main() -> None:
    transactions = load_transactions(CSV_PATH)
    totals = totals_by_customer(transactions)
    top = top_customers(totals)
    print(format_report(top))


if __name__ == "__main__":
    main()
