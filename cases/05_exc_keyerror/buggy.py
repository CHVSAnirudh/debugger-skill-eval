import json
import sys


def config_value(config, key):
    """Return config[key] if present, else None. Must not raise."""
    return config[key]


if __name__ == "__main__":
    data = json.load(sys.stdin)
    config = data["config"]
    key = data["key"]
    print(config_value(config, key))
