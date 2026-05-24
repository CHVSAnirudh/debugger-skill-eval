import json
import sys


def total_str_nums(items):
    """Given a list of strings representing integers, return their integer sum."""
    return sum(items)


if __name__ == "__main__":
    data = json.load(sys.stdin)
    print(total_str_nums(data["items"]))
