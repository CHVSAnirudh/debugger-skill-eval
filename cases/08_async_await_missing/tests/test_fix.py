import asyncio
import inspect
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import buggy
from buggy import consumer, get_value


def test_get_value_still_async():
    assert inspect.iscoroutinefunction(get_value), "get_value must remain async"


def _run(value):
    """consumer may be sync or async after the fix; handle both."""
    result = consumer(value)
    if inspect.iscoroutine(result):
        return asyncio.run(result)
    return result


def test_basic():
    assert _run(2) == 84


def test_one():
    assert _run(1) == 42


def test_zero():
    assert _run(0) == 0


def test_negative():
    assert _run(-3) == -126
