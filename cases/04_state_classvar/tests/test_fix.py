import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import Counter


def test_independent_instances():
    a = Counter()
    a.add(1)
    a.add(2)
    b = Counter()
    assert b.count() == 0
    assert a.count() == 2


def test_b_adds_dont_leak_to_a():
    a = Counter()
    b = Counter()
    b.add("x")
    b.add("y")
    assert a.count() == 0
    assert b.count() == 2


def test_fresh_counter_is_empty():
    Counter().add(99)
    fresh = Counter()
    assert fresh.count() == 0
