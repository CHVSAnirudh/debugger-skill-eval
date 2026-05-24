import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import RollingStats


def test_max_after_new_peak():
    rs = RollingStats(window_size=3)
    for v in [1.0, 2.0, 3.0]:
        rs.add(v)
    assert rs.max() == 3.0
    rs.add(5.0)  # window now [2,3,5]
    assert rs.max() == 5.0


def test_min_after_new_trough():
    rs = RollingStats(window_size=3)
    for v in [10.0, 20.0, 30.0]:
        rs.add(v)
    assert rs.min() == 10.0
    rs.add(5.0)  # window now [20,30,5]
    assert rs.min() == 5.0


def test_max_after_evicting_peak():
    rs = RollingStats(window_size=3)
    for v in [100.0, 1.0, 2.0]:
        rs.add(v)
    assert rs.max() == 100.0
    rs.add(3.0)  # evicts 100; window [1,2,3]
    assert rs.max() == 3.0


def test_min_after_evicting_trough():
    rs = RollingStats(window_size=3)
    for v in [-100.0, 1.0, 2.0]:
        rs.add(v)
    assert rs.min() == -100.0
    rs.add(3.0)  # evicts -100; window [1,2,3]
    assert rs.min() == 1.0


def test_mean_still_correct():
    rs = RollingStats(window_size=3)
    for v in [1.0, 2.0, 3.0, 4.0]:
        rs.add(v)
    assert abs(rs.mean() - 3.0) < 1e-9


def test_sequence_of_news():
    rs = RollingStats(window_size=2)
    rs.add(1.0)
    rs.add(2.0)
    assert rs.max() == 2.0
    rs.add(3.0)
    assert rs.max() == 3.0
    rs.add(4.0)
    assert rs.max() == 4.0
    rs.add(0.5)
    assert rs.min() == 0.5


def test_window_size_one():
    rs = RollingStats(window_size=1)
    rs.add(5.0)
    assert rs.max() == 5.0
    assert rs.min() == 5.0
    rs.add(10.0)
    assert rs.max() == 10.0
    assert rs.min() == 10.0
    rs.add(1.0)
    assert rs.max() == 1.0
    assert rs.min() == 1.0
