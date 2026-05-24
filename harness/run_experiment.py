"""Run the debugger-skill eval.

For each (case, condition, run_idx):
  1. Copy `cases/<case>/{buggy.py, prompt.txt, inputs.json}` to a fresh temp dir.
  2. If condition == 'with-skill', also copy AGENTS.md into the temp dir.
  3. Snapshot latest opencode session id (baseline).
  4. cd <temp>; opencode run "<prompt>"
  5. Find the new session id, extract metrics from opencode's sqlite.
  6. Grade with hidden pytest + golden-output diff.
  7. Append one row to results/runs.csv.

After all runs, write results/summary.md.
"""

from __future__ import annotations

import argparse
import csv
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# CASES_DIR and RESULTS_DIR/RUNS_CSV are resolved at runtime from CLI args
# so we can sweep different case sets into separate result files.
DEFAULT_CASES_DIR = ROOT / "cases"
DEFAULT_RESULTS_DIR = ROOT / "results"
AGENTS_MD = ROOT / "AGENTS.md"

# These are populated by main() and read by run_one / _ensure_csv / _append_row.
CASES_DIR: Path = DEFAULT_CASES_DIR
RESULTS_DIR: Path = DEFAULT_RESULTS_DIR
RUNS_CSV: Path = DEFAULT_RESULTS_DIR / "runs.csv"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_metrics import (  # noqa: E402
    extract,
    first_session_after,
    latest_session_id,
)
from grade import grade  # noqa: E402

CONDITIONS = ("without-skill", "with-skill")


def _discover_cases(cases_dir: Path) -> list[str]:
    return sorted(p.name for p in cases_dir.iterdir() if p.is_dir())

CSV_FIELDS = [
    "case",
    "condition",
    "run_idx",
    "session_id",
    "model_id",
    "tokens_input",
    "tokens_output",
    "tokens_total",
    "tokens_cache_read",
    "tokens_cache_write",
    "cost",
    "wall_time_seconds",
    "harness_wall_seconds",
    "tool_calls",
    "bash_calls",
    "pdb_invocations",
    "pytest_passed",
    "golden_match",
    "accuracy",
    "pytest_summary",
    "actual_output",
    "expected_output",
    "opencode_exit_code",
    "opencode_stderr_tail",
]


def _prepare_workdir(case_name: str, condition: str) -> Path:
    """Copy every file in the case dir to a fresh temp dir, except the hidden
    grading assets (`tests/` and `golden.json`). This lets cases ship arbitrary
    data files (CSVs, JSONs, extra .py modules) alongside buggy.py.
    """
    case_dir = CASES_DIR / case_name
    work_dir = Path(tempfile.mkdtemp(prefix=f"dse_{case_name}_{condition}_"))
    for entry in case_dir.iterdir():
        if entry.name in ("tests", "golden.json"):
            continue
        if entry.is_dir():
            shutil.copytree(entry, work_dir / entry.name)
        else:
            shutil.copy2(entry, work_dir / entry.name)
    if condition == "with-skill":
        shutil.copy2(AGENTS_MD, work_dir / "AGENTS.md")
    return work_dir


def _run_opencode(work_dir: Path, prompt: str, timeout_s: int, model: str | None) -> tuple[int, str]:
    env = os.environ.copy()
    cmd = ["opencode", "run"]
    if model:
        cmd.extend(["--model", model])
    cmd.append(prompt)
    proc = subprocess.run(
        cmd,
        cwd=work_dir,
        capture_output=True,
        text=True,
        env=env,
        timeout=timeout_s,
    )
    return proc.returncode, proc.stderr[-500:] if proc.stderr else ""


def _ensure_csv():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    if not RUNS_CSV.exists():
        with RUNS_CSV.open("w", newline="") as f:
            csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()


def _append_row(row: dict) -> None:
    with RUNS_CSV.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        w.writerow({k: row.get(k, "") for k in CSV_FIELDS})


def run_one(case_name: str, condition: str, run_idx: int, timeout_s: int, model: str | None = None) -> dict:
    case_dir = CASES_DIR / case_name
    prompt = (case_dir / "prompt.txt").read_text()
    work_dir = _prepare_workdir(case_name, condition)
    baseline = latest_session_id()

    t0 = time.monotonic()
    try:
        exit_code, stderr_tail = _run_opencode(work_dir, prompt, timeout_s, model)
    except subprocess.TimeoutExpired:
        exit_code, stderr_tail = -1, "<timeout>"
    harness_wall = round(time.monotonic() - t0, 2)

    new_sid = first_session_after(baseline)
    if new_sid is None:
        # opencode didn't write a session (auth, network, etc.). Record what we can.
        result = grade(case_dir, work_dir)
        return {
            "case": case_name,
            "condition": condition,
            "run_idx": run_idx,
            "session_id": "",
            "model_id": "",
            "tokens_input": 0,
            "tokens_output": 0,
            "tokens_total": 0,
            "tokens_cache_read": 0,
            "tokens_cache_write": 0,
            "cost": 0,
            "wall_time_seconds": 0,
            "harness_wall_seconds": harness_wall,
            "tool_calls": 0,
            "bash_calls": 0,
            "pdb_invocations": 0,
            "pytest_passed": result.pytest_passed,
            "golden_match": result.golden_match,
            "accuracy": result.accuracy,
            "pytest_summary": result.pytest_summary,
            "actual_output": result.actual_output[:300],
            "expected_output": result.expected_output,
            "opencode_exit_code": exit_code,
            "opencode_stderr_tail": stderr_tail.replace("\n", " | ")[:300],
            "_work_dir": str(work_dir),
        }

    metrics = extract(new_sid)
    grade_result = grade(case_dir, work_dir)
    return {
        "case": case_name,
        "condition": condition,
        "run_idx": run_idx,
        "session_id": metrics.session_id,
        "model_id": metrics.model_id,
        "tokens_input": metrics.tokens_input,
        "tokens_output": metrics.tokens_output,
        "tokens_total": metrics.tokens_total,
        "tokens_cache_read": metrics.tokens_cache_read,
        "tokens_cache_write": metrics.tokens_cache_write,
        "cost": metrics.cost,
        "wall_time_seconds": metrics.wall_time_seconds,
        "harness_wall_seconds": harness_wall,
        "tool_calls": metrics.tool_calls,
        "bash_calls": metrics.bash_calls,
        "pdb_invocations": metrics.pdb_invocations,
        "pytest_passed": grade_result.pytest_passed,
        "golden_match": grade_result.golden_match,
        "accuracy": grade_result.accuracy,
        "pytest_summary": grade_result.pytest_summary,
        "actual_output": grade_result.actual_output[:300],
        "expected_output": grade_result.expected_output,
        "opencode_exit_code": exit_code,
        "opencode_stderr_tail": stderr_tail.replace("\n", " | ")[:300],
        "_work_dir": str(work_dir),
    }


def write_summary() -> None:
    """Aggregate runs.csv into results/summary.md."""
    if not RUNS_CSV.exists():
        return
    with RUNS_CSV.open() as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return

    def _f(s):
        try:
            return float(s)
        except (TypeError, ValueError):
            return 0.0

    def _b(s):
        return str(s).lower() == "true"

    def agg(filtered):
        if not filtered:
            return None
        n = len(filtered)
        return {
            "n": n,
            "tokens_total": sum(_f(r["tokens_total"]) for r in filtered) / n,
            "tokens_input": sum(_f(r["tokens_input"]) for r in filtered) / n,
            "tokens_output": sum(_f(r["tokens_output"]) for r in filtered) / n,
            "cost": sum(_f(r["cost"]) for r in filtered) / n,
            "wall": sum(_f(r["wall_time_seconds"]) for r in filtered) / n,
            "tool_calls": sum(_f(r["tool_calls"]) for r in filtered) / n,
            "pdb": sum(_f(r["pdb_invocations"]) for r in filtered) / n,
            "accuracy": sum(1.0 for r in filtered if _b(r["accuracy"])) / n,
        }

    lines = ["# debugger-skill-eval results\n"]
    overall = {c: agg([r for r in rows if r["condition"] == c]) for c in CONDITIONS}
    lines.append("## Overall (mean per invocation)\n")
    lines.append("| condition | n | accuracy | tokens_total | tokens_in | tokens_out | cost ($) | wall (s) | tool_calls | pdb_calls |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")
    for c in CONDITIONS:
        a = overall[c]
        if a is None:
            lines.append(f"| {c} | 0 | - | - | - | - | - | - | - | - |")
            continue
        lines.append(
            f"| {c} | {a['n']} | {a['accuracy']:.0%} | {a['tokens_total']:.0f} | "
            f"{a['tokens_input']:.0f} | {a['tokens_output']:.0f} | {a['cost']:.4f} | "
            f"{a['wall']:.1f} | {a['tool_calls']:.1f} | {a['pdb']:.2f} |"
        )

    # Delta row
    if overall["with-skill"] and overall["without-skill"]:
        w, wo = overall["with-skill"], overall["without-skill"]
        lines.append(
            f"| **delta (with-without)** | - | "
            f"{(w['accuracy'] - wo['accuracy']):+.0%} | "
            f"{(w['tokens_total'] - wo['tokens_total']):+.0f} | "
            f"{(w['tokens_input'] - wo['tokens_input']):+.0f} | "
            f"{(w['tokens_output'] - wo['tokens_output']):+.0f} | "
            f"{(w['cost'] - wo['cost']):+.4f} | "
            f"{(w['wall'] - wo['wall']):+.1f} | "
            f"{(w['tool_calls'] - wo['tool_calls']):+.1f} | "
            f"{(w['pdb'] - wo['pdb']):+.2f} |"
        )

    lines.append("\n## Per-case (mean per invocation)\n")
    lines.append("| case | condition | n | accuracy | tokens_total | wall (s) | pdb_calls |")
    lines.append("|---|---|---|---|---|---|---|")
    cases = sorted({r["case"] for r in rows})
    for case in cases:
        for c in CONDITIONS:
            a = agg([r for r in rows if r["case"] == case and r["condition"] == c])
            if a is None:
                continue
            lines.append(
                f"| {case} | {c} | {a['n']} | {a['accuracy']:.0%} | "
                f"{a['tokens_total']:.0f} | {a['wall']:.1f} | {a['pdb']:.2f} |"
            )

    (RESULTS_DIR / "summary.md").write_text("\n".join(lines) + "\n")


def main() -> None:
    global CASES_DIR, RESULTS_DIR, RUNS_CSV
    p = argparse.ArgumentParser()
    p.add_argument("--cases-dir", default=str(DEFAULT_CASES_DIR),
                   help="directory containing case subdirs (default: cases/)")
    p.add_argument("--results-dir", default=None,
                   help="directory for runs.csv/summary.md (default: results/ for cases/, results_<name>/ otherwise)")
    p.add_argument("--case", action="append", help="restrict to a single case (repeatable)")
    p.add_argument("--condition", choices=CONDITIONS, help="restrict to one condition")
    p.add_argument("--runs", type=int, default=3, help="runs per (case x condition)")
    p.add_argument("--timeout", type=int, default=600, help="opencode timeout in seconds")
    p.add_argument("--keep-workdirs", action="store_true", help="don't delete temp dirs")
    p.add_argument("--model", default=None, help='override opencode model (e.g. "fireworks-ai/accounts/fireworks/models/gpt-oss-20b")')
    args = p.parse_args()

    CASES_DIR = Path(args.cases_dir).resolve()
    if args.results_dir:
        RESULTS_DIR = Path(args.results_dir).resolve()
    elif CASES_DIR.name == "cases":
        RESULTS_DIR = DEFAULT_RESULTS_DIR
    else:
        RESULTS_DIR = ROOT / f"results_{CASES_DIR.name}"
    RUNS_CSV = RESULTS_DIR / "runs.csv"

    all_cases = _discover_cases(CASES_DIR)
    cases = args.case or all_cases
    conditions = (args.condition,) if args.condition else CONDITIONS

    _ensure_csv()
    total = len(cases) * len(conditions) * args.runs
    done = 0
    for case in cases:
        for cond in conditions:
            for ri in range(1, args.runs + 1):
                done += 1
                print(f"[{done}/{total}] {case} | {cond} | run {ri}", flush=True)
                try:
                    row = run_one(case, cond, ri, args.timeout, model=args.model)
                except Exception as e:  # noqa: BLE001
                    print(f"   ERROR: {e}", flush=True)
                    continue
                wd = row.pop("_work_dir", None)
                _append_row(row)
                print(
                    f"   acc={row['accuracy']} tokens={row['tokens_total']} "
                    f"wall={row['wall_time_seconds']}s pdb={row['pdb_invocations']}",
                    flush=True,
                )
                if wd and not args.keep_workdirs:
                    shutil.rmtree(wd, ignore_errors=True)

    write_summary()
    print(f"\nDone. Results: {RUNS_CSV}\nSummary: {RESULTS_DIR / 'summary.md'}")


if __name__ == "__main__":
    main()
