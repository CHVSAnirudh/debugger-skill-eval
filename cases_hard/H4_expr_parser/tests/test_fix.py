import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import evaluate


def test_division_left_assoc():
    assert evaluate("20 / 2 / 5") == 2.0


def test_division_chain():
    assert evaluate("100 / 10 / 2") == 5.0


def test_subtraction_left_assoc():
    assert evaluate("10 - 2 - 3") == 5.0


def test_mixed_mul_div():
    # 8 / 4 * 2 = (8/4)*2 = 4
    assert evaluate("8 / 4 * 2") == 4.0


def test_multiplication_chain():
    assert evaluate("2 * 3 * 4") == 24.0


def test_parens_still_work():
    assert evaluate("(20 / 2) / 5") == 2.0
    assert evaluate("20 / (2 / 5)") == 50.0


def test_precedence_preserved():
    # */ still bind tighter than +-
    assert evaluate("100 - 50 / 5") == 90.0
    assert evaluate("2 + 3 * 4") == 14.0


def test_unary_minus():
    assert evaluate("-5 + 3") == -2.0
    assert evaluate("10 / -2") == -5.0
