import json
import sys


class Counter:
    items = []

    def add(self, x):
        self.items.append(x)

    def count(self):
        return len(self.items)


if __name__ == "__main__":
    data = json.load(sys.stdin)
    a = Counter()
    for x in data["a_items"]:
        a.add(x)
    b = Counter()
    for x in data["b_items"]:
        b.add(x)
    print(json.dumps({"a": a.count(), "b": b.count()}))
