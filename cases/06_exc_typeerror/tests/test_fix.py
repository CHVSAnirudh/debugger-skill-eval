import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import total_str_nums


def test_basic():
    assert total_str_nums(["1", "2", "3"]) == 6


def test_single():
    assert total_str_nums(["42"]) == 42


def test_empty():
    assert total_str_nums([]) == 0


def test_with_negatives():
    assert total_str_nums(["-5", "10", "-2"]) == 3


def test_returns_int():
    result = total_str_nums(["1", "2"])
    assert isinstance(result, int)
    assert result == 3
