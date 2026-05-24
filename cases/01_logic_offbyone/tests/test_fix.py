import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import sum_to


def test_basic():
    assert sum_to(5) == 15


def test_one():
    assert sum_to(1) == 1


def test_zero():
    assert sum_to(0) == 0


def test_ten():
    assert sum_to(10) == 55


def test_hundred():
    assert sum_to(100) == 5050
