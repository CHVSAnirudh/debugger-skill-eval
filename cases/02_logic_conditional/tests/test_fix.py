import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import is_leap


def test_2000():
    assert is_leap(2000) is True


def test_1900():
    assert is_leap(1900) is False


def test_2024():
    assert is_leap(2024) is True


def test_2023():
    assert is_leap(2023) is False


def test_2100():
    assert is_leap(2100) is False


def test_2400():
    assert is_leap(2400) is True
