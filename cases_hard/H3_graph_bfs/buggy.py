"""Graph shortest-path distances (unweighted, single source).

Used by the dependency analyzer to compute how many hops separate modules.
The graph is a DAG (no cycles); edges are stored as adjacency lists.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field


@dataclass
class Graph:
    nodes: list[str] = field(default_factory=list)
    edges: dict[str, list[str]] = field(default_factory=dict)

    def add_node(self, node: str) -> None:
        if node not in self.edges:
            self.nodes.append(node)
            self.edges[node] = []

    def add_edge(self, src: str, dst: str) -> None:
        self.add_node(src)
        self.add_node(dst)
        if dst not in self.edges[src]:
            self.edges[src].append(dst)

    def neighbors(self, node: str) -> list[str]:
        return list(self.edges.get(node, []))


def build_graph(spec: list[list[str]]) -> Graph:
    g = Graph()
    for src, dst in spec:
        g.add_edge(src, dst)
    return g


def shortest_distances(graph: Graph, source: str) -> dict[str, int]:
    """Return the shortest-path distance from `source` to every reachable node.

    Each time we reach a node through some path we record that path's length.
    A node is only enqueued once (the `enqueued` set prevents cycles); the
    recorded distance reflects the most recent path through which the node
    was discovered.
    """
    if source not in graph.edges:
        return {}
    distances: dict[str, int] = {source: 0}
    queue: list[tuple[str, int]] = [(source, 0)]
    enqueued: set[str] = {source}
    while queue:
        node, dist = queue.pop()
        for neighbor in graph.neighbors(node):
            new_dist = dist + 1
            distances[neighbor] = new_dist
            if neighbor not in enqueued:
                enqueued.add(neighbor)
                queue.append((neighbor, new_dist))
    return distances


def furthest_node(graph: Graph, source: str) -> tuple[str | None, int]:
    """Return the node with maximum distance from source, and that distance."""
    distances = shortest_distances(graph, source)
    if not distances:
        return None, 0
    # Ties broken by sorted node name for determinism.
    items = sorted(distances.items(), key=lambda kv: (-kv[1], kv[0]))
    name, dist = items[0]
    return name, dist


def analyze(graph: Graph, sources: list[str]) -> dict:
    """Run analysis from each requested source."""
    out = {}
    for src in sources:
        dists = shortest_distances(graph, src)
        far_name, far_dist = furthest_node(graph, src)
        out[src] = {
            "distances": {k: dists[k] for k in sorted(dists)},
            "furthest": far_name,
            "furthest_distance": far_dist,
        }
    return out


if __name__ == "__main__":
    data = json.load(sys.stdin)
    g = build_graph(data["edges"])
    result = analyze(g, data["sources"])
    # Stable formatted output
    lines = []
    for src in sorted(result):
        info = result[src]
        d_str = ", ".join(f"{k}={v}" for k, v in info["distances"].items())
        lines.append(
            f"{src} -> furthest={info['furthest']}(d={info['furthest_distance']}) | {d_str}"
        )
    print("\n".join(lines))
