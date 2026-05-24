import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import config_value


def test_missing_returns_none():
    assert config_value({"a": 1}, "missing") is None


def test_present_returns_value():
    assert config_value({"a": 1}, "a") == 1


def test_empty_dict():
    assert config_value({}, "anything") is None


def test_present_falsy_value():
    assert config_value({"a": 0}, "a") == 0


def test_does_not_raise():
    config_value({}, "x")
    config_value({"y": 1}, "z")
