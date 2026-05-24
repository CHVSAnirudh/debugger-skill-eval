import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import apply_discount


def _df():
    return pd.DataFrame({"customer_id": ["A", "B", "C", "D"], "spend": [100.0, 600.0, 800.0, 200.0]})


def test_premium_rows_discounted():
    df = _df()
    result = apply_discount(df, threshold=500.0, rate=0.10)
    # B (600) and C (800) are premium; should drop to 540 and 720
    spend = dict(zip(result["customer_id"], result["spend"]))
    assert abs(spend["B"] - 540.0) < 1e-6
    assert abs(spend["C"] - 720.0) < 1e-6


def test_non_premium_rows_unchanged():
    df = _df()
    result = apply_discount(df, threshold=500.0, rate=0.10)
    spend = dict(zip(result["customer_id"], result["spend"]))
    assert spend["A"] == 100.0
    assert spend["D"] == 200.0


def test_total_spend_decreases():
    df = _df()
    before = df["spend"].sum()
    after = apply_discount(df, threshold=500.0, rate=0.10)["spend"].sum()
    assert after < before
    assert abs(after - (100 + 540 + 720 + 200)) < 1e-6


def test_returns_modified_dataframe():
    df = _df()
    out = apply_discount(df, threshold=500.0, rate=0.10)
    # Whether or not df is mutated in place, the returned frame must reflect the discount.
    assert isinstance(out, pd.DataFrame)
    assert abs(out["spend"].sum() - 1560.0) < 1e-6


def test_zero_rate_is_noop():
    df = _df()
    before = df["spend"].sum()
    out = apply_discount(df, threshold=500.0, rate=0.0)
    assert abs(out["spend"].sum() - before) < 1e-6


def test_high_threshold_no_premium():
    df = _df()
    out = apply_discount(df, threshold=10_000.0, rate=0.50)
    assert abs(out["spend"].sum() - 1700.0) < 1e-6  # unchanged
