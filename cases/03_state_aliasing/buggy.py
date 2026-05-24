import json
import sys


def add_item(item, lst=[]):
    """Append item to a new list and return it."""
    lst.append(item)
    return lst


if __name__ == "__main__":
    data = json.load(sys.stdin)
    results = []
    for item in data["items"]:
        results.append(add_item(item))
    print(json.dumps(results))
