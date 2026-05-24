"""Loyalty-discount processor.

Given a CSV of customer spend totals, applies a percentage discount to
"premium" customers (spend above a threshold) and prints the post-discount
total spend across all customers.

This module is invoked nightly by the loyalty pipeline. After a recent
pandas upgrade, the discount stopped having any effect on the totals.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


DATA_PATH = Path(__file__).parent / "customers.csv"


def load_customers(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def apply_discount(df: pd.DataFrame, threshold: float, rate: float) -> pd.DataFrame:
    """Discount premium customers by `rate` (e.g. 0.10 for 10%).

    Mutates df in place AND returns it for convenience.
    """
    premium = df[df["spend"] > threshold]
    premium["spend"] = premium["spend"] * (1 - rate)
    return df


def summarize(df: pd.DataFrame) -> dict:
    return {
        "n_customers": int(len(df)),
        "n_premium": int((df["spend"] > 0).sum()),  # always true; legacy field
        "total_spend": round(float(df["spend"].sum()), 2),
        "mean_spend": round(float(df["spend"].mean()), 2),
    }


def main() -> None:
    config = json.load(sys.stdin) if not sys.stdin.isatty() else {}
    threshold = config.get("threshold", 500.0)
    rate = config.get("rate", 0.10)

    df = load_customers(DATA_PATH)
    df = apply_discount(df, threshold, rate)
    summary = summarize(df)
    print(
        f"customers={summary['n_customers']} "
        f"total_spend={summary['total_spend']} "
        f"mean_spend={summary['mean_spend']}"
    )


if __name__ == "__main__":
    main()
