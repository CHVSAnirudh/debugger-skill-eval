# debugger-skill-eval

Does teaching an LLM coding agent to use **`pdb`** (Python's debugger) actually help it fix bugs? This repo runs that experiment carefully, in **four sweeps across two models**, and reports the numbers honestly — including where the result is the opposite of what I expected.

**TL;DR:**
- On a strong model (Kimi K2.6): the "use pdb" skill never improves accuracy, costs +42–280% more tokens, and on real-world bugs actually *hurts* accuracy by 8 percentage points.
- On a weaker model (gpt-oss-20b): the skill *helps* — **accuracy on real-world bugs jumps from 33% → 58% (+25pp)**.
- **But the weaker model never invoked pdb a single time** across 96 runs. The lift is from the *workflow framing* in `AGENTS.md` ("reproduce → form a hypothesis → fix → verify"), not from the debugger itself.

Full writeups in [`findings/`](findings/).

## What's in this repo

```
AGENTS.md                # the "skill" — a non-interactive pdb workflow
cases/                   # 8 short Python bugs (v1: easy)
cases_hard/              # 4 longer Python bugs (v2: hard)
cases_v3/                # 4 real-world bug regimes (blind data, pandas, etc.)
harness/                 # run_experiment.py, extract_metrics.py, grade.py
results/                 # v1 Kimi K2.6 runs.csv + summary.md
results_cases_hard/      # v2 Kimi K2.6
results_cases_v3/        # v3 Kimi K2.6
results_gptoss_v1/       # v1 gpt-oss-20b
results_gptoss_v2/       # v2 gpt-oss-20b
results_gptoss_v3/       # v3 gpt-oss-20b
findings/
├── README.md            # index of writeups
├── v1-easy-bugs.md
├── v2-hard-bugs.md
├── v3-real-world-bugs.md
└── v4-weaker-model.md
```

## Experiment design

Each case has:
- `buggy.py` — given to the agent
- `prompt.txt` — task statement
- `inputs.json` — stdin for the script
- Optional extra files (CSV, etc.)
- `tests/test_fix.py` — **hidden** pytest suite used only by the grader
- `golden.json` — **hidden** expected stdout from `python buggy.py < inputs.json`

Each run:
1. Copy non-hidden case files to a fresh temp dir
2. (with-skill condition only) Copy `AGENTS.md` into the temp dir
3. Snapshot opencode's session db, run `opencode run "<prompt>"` in the temp dir
4. Find the new session, extract tokens / wall time / tool calls from opencode's sqlite at `~/.local/share/opencode/opencode.db`
5. Grade against the hidden pytest suite + golden stdout; record one row to `runs.csv`

3 runs per (case × condition). Headline metric: `accuracy = pytest_passed AND golden_match`.

## Reproduce

```bash
# requires Python 3.10+, opencode 1.3+ (with a provider configured), pytest, pandas
python3 -m venv .venv
.venv/bin/pip install pytest pandas

# one case smoke test
.venv/bin/python harness/run_experiment.py --case 01_logic_offbyone --runs 1

# full v1 sweep (Kimi via default config)
.venv/bin/python harness/run_experiment.py --runs 3

# v2 / v3
.venv/bin/python harness/run_experiment.py --cases-dir cases_hard --runs 3
.venv/bin/python harness/run_experiment.py --cases-dir cases_v3 --runs 3

# weaker model (Fireworks gpt-oss-20b)
.venv/bin/python harness/run_experiment.py \
  --cases-dir cases_v3 \
  --model "fireworks-ai/accounts/fireworks/models/gpt-oss-20b" \
  --results-dir results_gptoss_v3 \
  --runs 3
```

## Headline numbers (192 invocations total)

| sweep | model | n | acc wo-skill | acc w-skill | Δacc | total cost |
|---|---|---:|---:|---:|---:|---:|
| v1 (easy) | Kimi K2.6 | 48 | 100% | 100% | +0pp | $1.54 |
| v2 (hard) | Kimi K2.6 | 24 | 100% | 100% | +0pp | $1.50 |
| v3 (real) | Kimi K2.6 | 24 | 100% | 92% | **−8pp** | $1.30 |
| v1 (easy) | gpt-oss-20b | 48 | 62% | 71% | **+8pp** | $0.05 |
| v2 (hard) | gpt-oss-20b | 24 | 75% | 75% | +0pp | $0.03 |
| v3 (real) | gpt-oss-20b | 24 | 33% | 58% | **+25pp** | $0.03 |

(See [`findings/v4-weaker-model.md`](findings/v4-weaker-model.md) for the side-by-side analysis.)

## Caveats

- Sample size is 3 runs per cell. A 33pp per-case shift can be one run flipping. The aggregate v3 +25pp on gpt-oss is 8/12 vs 4/12 passes — real but not airtight.
- Only Python, only `pdb`. No claim about debuggers in other languages or for non-Python agents.
- One skill design. A leaner workflow-only AGENTS.md would likely replicate the gpt-oss lift at lower token cost — that ablation isn't done yet.
- Only two models. Where the sign flips between "skill is a tax" and "skill helps" probably lies somewhere in the middle of the capability range (Llama-3-70B class).

## Open questions

1. If the lift on weaker models comes entirely from the workflow framing, should this kind of "reproduce/verify" discipline be **baked into post-training** instead of bolted on as a skill file?
2. Conversely — should we go back to actually *teaching* agents to use the debugger (post-mortem inspection, conditional breakpoints, watch expressions)? These were invaluable to human engineers; we've quietly stopped asking the agent to do them.
3. What's the smallest AGENTS.md that captures the workflow lift without the token tax?

PRs and other models / case sets welcome.
