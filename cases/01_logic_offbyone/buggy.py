import json
import sys


def sum_to(n):
    """Return the sum 1 + 2 + ... + n inclusive."""
    total = 0
    for i in range(n):
        total += i
    return total


if __name__ == "__main__":
    n = json.load(sys.stdin)["n"]
    print(sum_to(n))
