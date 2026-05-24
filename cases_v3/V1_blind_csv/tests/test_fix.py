import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import parse_amount, totals_by_customer, top_customers


def test_plain_amount():
    assert parse_amount("123.45") == 123.45


def test_amount_with_thousands_separator():
    assert parse_amount("1,234.56") == 1234.56


def test_amount_with_thousands_and_no_decimals():
    assert parse_amount("2,500") == 2500.0


def test_amount_with_multiple_separators():
    assert parse_amount("1,234,567.89") == 1234567.89


def test_amount_whitespace_tolerant():
    assert parse_amount(" 99.50 ") == 99.50


def test_totals_with_mixed_formats():
    txs = [
        {"customer_id": "A", "amount": parse_amount("100.00")},
        {"customer_id": "A", "amount": parse_amount("1,234.56")},
        {"customer_id": "B", "amount": parse_amount("50.00")},
    ]
    t = totals_by_customer(txs)
    assert abs(t["A"] - 1334.56) < 1e-6
    assert abs(t["B"] - 50.00) < 1e-6


def test_top_customers_ordering():
    totals = {"X": 50, "Y": 200, "Z": 100, "W": 200}
    top = top_customers(totals, n=3)
    # 200 ties broken by customer_id alphabetical
    assert top == [("W", 200), ("Y", 200), ("Z", 100)]
