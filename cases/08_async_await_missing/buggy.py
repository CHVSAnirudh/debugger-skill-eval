import asyncio
import json
import sys


async def get_value():
    return 42


def consumer(multiplier):
    result = get_value()
    return result * multiplier


if __name__ == "__main__":
    data = json.load(sys.stdin)
    print(consumer(data["multiplier"]))
