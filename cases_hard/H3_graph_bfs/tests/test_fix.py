import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import Graph, build_graph, shortest_distances, furthest_node


def test_direct_edge_wins():
    g = build_graph([["A", "B"], ["A", "D"], ["B", "D"]])
    d = shortest_distances(g, "A")
    assert d == {"A": 0, "B": 1, "D": 1}


def test_diamond():
    g = build_graph([["A", "B"], ["A", "C"], ["B", "D"], ["C", "D"]])
    d = shortest_distances(g, "A")
    assert d == {"A": 0, "B": 1, "C": 1, "D": 2}


def test_longer_chain():
    g = build_graph([["A", "B"], ["B", "C"], ["C", "D"], ["A", "D"]])
    d = shortest_distances(g, "A")
    # D should be reached directly in 1, not via the chain in 3
    assert d["D"] == 1
    assert d["A"] == 0 and d["B"] == 1 and d["C"] == 2


def test_unreachable():
    g = build_graph([["A", "B"], ["C", "D"]])
    d = shortest_distances(g, "A")
    assert d == {"A": 0, "B": 1}
    assert "C" not in d and "D" not in d


def test_single_node():
    g = Graph()
    g.add_node("X")
    assert shortest_distances(g, "X") == {"X": 0}


def test_furthest_consistency():
    g = build_graph([["A", "B"], ["A", "C"], ["C", "D"], ["D", "E"]])
    name, dist = furthest_node(g, "A")
    assert name == "E"
    assert dist == 3


def test_multiple_short_paths():
    g = build_graph([["A", "B"], ["A", "C"], ["B", "X"], ["C", "X"], ["A", "X"]])
    d = shortest_distances(g, "A")
    assert d["X"] == 1
