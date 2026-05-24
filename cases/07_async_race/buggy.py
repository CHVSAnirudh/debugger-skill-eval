import asyncio
import json
import sys


async def increment(counter, key, n):
    for _ in range(n):
        counter[key] = counter[key] + 1


async def run(n_tasks, per_task):
    counter = {"value": 0}
    tasks = [increment(counter, "value", per_task) for _ in range(n_tasks)]
    asyncio.gather(*tasks)
    return counter["value"]


if __name__ == "__main__":
    data = json.load(sys.stdin)
    result = asyncio.run(run(data["n_tasks"], data["per_task"]))
    print(result)
