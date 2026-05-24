import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import add_item


def test_single():
    assert add_item(1) == [1]


def test_independent_calls():
    a = add_item("a")
    b = add_item("b")
    assert a == ["a"]
    assert b == ["b"]


def test_three_independent():
    r1 = add_item(10)
    r2 = add_item(20)
    r3 = add_item(30)
    assert r1 == [10]
    assert r2 == [20]
    assert r3 == [30]
