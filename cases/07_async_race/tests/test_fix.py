import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import run


def test_basic():
    assert asyncio.run(run(5, 10)) == 50


def test_single_task():
    assert asyncio.run(run(1, 3)) == 3


def test_many_small():
    assert asyncio.run(run(10, 1)) == 10


def test_zero_tasks():
    assert asyncio.run(run(0, 5)) == 0
