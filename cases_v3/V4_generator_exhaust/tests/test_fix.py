import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import Transaction, report, filter_window


def _txs():
    return [
        Transaction("A", 100.0, day=10),
        Transaction("A", 200.0, day=50),
        Transaction("B", 50.0, day=50),
        Transaction("B", 75.0, day=80),
        Transaction("C", 300.0, day=200),
    ]


def test_report_basic():
    r = report(_txs(), start=40, end=100)
    assert r["total"] == 325.0
    assert r["count"] == 3
    assert r["max"] == 200.0
    assert r["unique_customers"] == 2


def test_report_empty_window():
    r = report(_txs(), start=500, end=600)
    assert r["total"] == 0.0
    assert r["count"] == 0
    assert r["max"] == 0.0
    assert r["unique_customers"] == 0


def test_report_full_window():
    r = report(_txs(), start=1, end=365)
    assert r["count"] == 5
    assert r["max"] == 300.0
    assert r["unique_customers"] == 3


def test_filter_window_is_lazy():
    """filter_window should still return an iterator/iterable, not eagerly materialize."""
    txs = _txs()
    fw = filter_window(txs, 1, 365)
    # We allow either a generator OR a fresh-iterable-each-call (e.g. a list factory),
    # but it must NOT be a single iterator whose elements vanish after one pass —
    # otherwise the agent has solved the count-bug by accident without addressing
    # exhaustion. report() above checks that.
    # Here we only check it yields all elements at least once.
    assert sum(1 for _ in fw) == 5


def test_report_with_zero_amounts():
    txs = [Transaction("X", 0.0, day=50), Transaction("Y", 0.0, day=60)]
    r = report(txs, start=40, end=70)
    assert r["count"] == 2
    assert r["max"] == 0.0
    assert r["unique_customers"] == 2
