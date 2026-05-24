"""Extract per-session metrics from opencode's local sqlite database.

opencode stores everything at ~/.local/share/opencode/opencode.db. Schemas:
  session(id, time_created, time_updated, ...)
  message(id, session_id, time_created, data TEXT)
  part(id, message_id, session_id, time_created, data TEXT)

`message.data` is JSON. Assistant messages contain:
  {"tokens": {"input": N, "output": N, "total": N, "cache": {"read": N, "write": N}},
   "cost": F, "modelID": "...", ...}

`part.data` is JSON. Tool-call parts look like:
  {"type": "tool", "tool": "bash", "state": {"input": {"command": "...", ...}, ...}, ...}
"""

from __future__ import annotations

import json
import re
import sqlite3
from dataclasses import dataclass, asdict
from pathlib import Path

DB_PATH = Path.home() / ".local" / "share" / "opencode" / "opencode.db"

PDB_PATTERN = re.compile(r"\bpython\d*(?:\.\d+)?\s+-m\s+pdb\b|pdb\.set_trace\(|breakpoint\(")


@dataclass
class SessionMetrics:
    session_id: str
    tokens_input: int
    tokens_output: int
    tokens_total: int
    tokens_cache_read: int
    tokens_cache_write: int
    cost: float
    wall_time_seconds: float
    tool_calls: int
    bash_calls: int
    pdb_invocations: int
    model_id: str


def latest_session_id(db_path: Path = DB_PATH) -> str | None:
    """Return the most recently created session id, or None if none exist."""
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        row = conn.execute(
            "SELECT id FROM session ORDER BY time_created DESC LIMIT 1"
        ).fetchone()
    return row[0] if row else None


def first_session_after(baseline_id: str | None, db_path: Path = DB_PATH) -> str | None:
    """Return the oldest session created strictly after the baseline session.

    If baseline_id is None, returns the oldest session overall.
    """
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        if baseline_id is None:
            row = conn.execute(
                "SELECT id FROM session ORDER BY time_created ASC LIMIT 1"
            ).fetchone()
        else:
            baseline_t = conn.execute(
                "SELECT time_created FROM session WHERE id = ?", (baseline_id,)
            ).fetchone()
            if baseline_t is None:
                return None
            row = conn.execute(
                "SELECT id FROM session WHERE time_created > ? "
                "ORDER BY time_created ASC LIMIT 1",
                (baseline_t[0],),
            ).fetchone()
    return row[0] if row else None


def extract(session_id: str, db_path: Path = DB_PATH) -> SessionMetrics:
    """Pull all metrics for a single opencode session."""
    with sqlite3.connect(f"file:{db_path}?mode=ro", uri=True) as conn:
        s_row = conn.execute(
            "SELECT time_created, time_updated FROM session WHERE id = ?",
            (session_id,),
        ).fetchone()
        if s_row is None:
            raise ValueError(f"session {session_id!r} not found")
        time_created_ms, time_updated_ms = s_row
        wall = max(0.0, (time_updated_ms - time_created_ms) / 1000.0)

        msg_rows = conn.execute(
            "SELECT data FROM message WHERE session_id = ?", (session_id,)
        ).fetchall()
        part_rows = conn.execute(
            "SELECT data FROM part WHERE session_id = ?", (session_id,)
        ).fetchall()

    t_in = t_out = t_total = c_read = c_write = 0
    cost = 0.0
    model_id = ""
    for (raw,) in msg_rows:
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        toks = obj.get("tokens") or {}
        t_in += int(toks.get("input") or 0)
        t_out += int(toks.get("output") or 0)
        t_total += int(toks.get("total") or 0)
        cache = toks.get("cache") or {}
        c_read += int(cache.get("read") or 0)
        c_write += int(cache.get("write") or 0)
        cost += float(obj.get("cost") or 0.0)
        if not model_id and obj.get("modelID"):
            model_id = obj["modelID"]

    tool_calls = 0
    bash_calls = 0
    pdb_invocations = 0
    for (raw,) in part_rows:
        try:
            obj = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if obj.get("type") != "tool":
            continue
        tool_calls += 1
        if obj.get("tool") == "bash":
            bash_calls += 1
            cmd = ((obj.get("state") or {}).get("input") or {}).get("command") or ""
            if PDB_PATTERN.search(cmd):
                pdb_invocations += 1

    return SessionMetrics(
        session_id=session_id,
        tokens_input=t_in,
        tokens_output=t_out,
        tokens_total=t_total,
        tokens_cache_read=c_read,
        tokens_cache_write=c_write,
        cost=round(cost, 6),
        wall_time_seconds=round(wall, 2),
        tool_calls=tool_calls,
        bash_calls=bash_calls,
        pdb_invocations=pdb_invocations,
        model_id=model_id,
    )


def main() -> None:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("session_id", nargs="?", help="opencode session id (default: latest)")
    args = p.parse_args()
    sid = args.session_id or latest_session_id()
    if not sid:
        raise SystemExit("no sessions found")
    print(json.dumps(asdict(extract(sid)), indent=2))


if __name__ == "__main__":
    main()
