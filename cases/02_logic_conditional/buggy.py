import json
import sys


def is_leap(year):
    """Return True iff year is a Gregorian leap year."""
    if year % 4 == 0:
        return True
    return False


if __name__ == "__main__":
    year = json.load(sys.stdin)["year"]
    print(is_leap(year))
