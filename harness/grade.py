"""Grade a candidate fix in a temp directory.

A temp dir has the agent-edited `buggy.py`. The grader copies in the hidden
`tests/` and `golden.json` for that case, then:
  1. Runs `pytest tests/` -> pytest_passed.
  2. Runs `python buggy.py < inputs.json`, strips trailing newline, compares
     against `golden.json` -> golden_match.

accuracy = pytest_passed AND golden_match.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PYTHON = ROOT / ".venv" / "bin" / "python"


@dataclass
class GradeResult:
    pytest_passed: bool
    golden_match: bool
    accuracy: bool
    actual_output: str
    expected_output: str
    pytest_summary: str


def _run_pytest(work_dir: Path) -> tuple[bool, str]:
    proc = subprocess.run(
        [str(PYTHON), "-m", "pytest", "tests/", "-q", "--tb=no"],
        cwd=work_dir,
        capture_output=True,
        text=True,
        timeout=120,
    )
    summary_line = ""
    for line in (proc.stdout + proc.stderr).splitlines()[::-1]:
        if "passed" in line or "failed" in line or "error" in line:
            summary_line = line.strip()
            break
    return proc.returncode == 0, summary_line


def _run_golden(work_dir: Path) -> tuple[str, str]:
    inputs = (work_dir / "inputs.json").read_text()
    golden = json.loads((work_dir / "golden.json").read_text())
    expected = str(golden)
    try:
        proc = subprocess.run(
            [str(PYTHON), "buggy.py"],
            cwd=work_dir,
            input=inputs,
            capture_output=True,
            text=True,
            timeout=60,
        )
        actual = proc.stdout.rstrip("\n")
        if proc.returncode != 0:
            actual = f"<exit={proc.returncode}> {actual} | stderr={proc.stderr.strip()[:200]}"
    except subprocess.TimeoutExpired:
        actual = "<timeout>"
    return actual, expected


def grade(case_dir: Path, work_dir: Path) -> GradeResult:
    """Grade work_dir against the hidden assets in case_dir."""
    # Copy hidden tests + golden into work_dir (if missing)
    src_tests = case_dir / "tests"
    dst_tests = work_dir / "tests"
    if dst_tests.exists():
        shutil.rmtree(dst_tests)
    shutil.copytree(src_tests, dst_tests)
    shutil.copy2(case_dir / "golden.json", work_dir / "golden.json")
    # inputs.json should already be in work_dir, but ensure it's there
    if not (work_dir / "inputs.json").exists():
        shutil.copy2(case_dir / "inputs.json", work_dir / "inputs.json")

    pytest_ok, summary = _run_pytest(work_dir)
    actual, expected = _run_golden(work_dir)
    golden_ok = actual == expected
    return GradeResult(
        pytest_passed=pytest_ok,
        golden_match=golden_ok,
        accuracy=pytest_ok and golden_ok,
        actual_output=actual,
        expected_output=expected,
        pytest_summary=summary,
    )


def main() -> None:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("case_dir", help="path to cases/<NN_name>/")
    p.add_argument("work_dir", help="path to the temp dir with the candidate buggy.py")
    args = p.parse_args()
    result = grade(Path(args.case_dir).resolve(), Path(args.work_dir).resolve())
    print(json.dumps(asdict(result), indent=2))
    sys.exit(0 if result.accuracy else 1)


if __name__ == "__main__":
    main()
