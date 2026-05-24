# v3 — Real-world bug regimes (2026-05-19)

## Question

v1 (easy bugs) and v2 (longer code) both hit 100% accuracy in both conditions. The skill couldn't demonstrate help because the model didn't need it. v3 targets the regimes I argued pdb would actually shine in:

1. **Blind data** — bug is in input data the model can't see in the prompt
2. **Library internals** — bug is in pandas semantics the model might mis-model
3. **Python closure gotcha** — bug looks fine on read, surprises at runtime
4. **Iterator semantics** — generator exhaustion across re-iteration

## Setup

- Same harness, same model (Kimi K2.6 / Fireworks), same `AGENTS.md`.
- 4 cases under `cases_v3/`, ~50–60 LOC each, including data files.
- 4 × 2 × 3 = **24 invocations.** Total cost: $1.30.

### The cases

| case | bug regime | ships data? | bug |
|---|---|---|---|
| V1_blind_csv | data-dependent | 500-row CSV | `float("1,234.56")` raises; 3 of 500 rows have thousands separators |
| V2_pandas_chained | library internals | 60-row CSV | `df[mask]['col'] = …` silently doesn't propagate under copy-on-write |
| V3_late_binding | Python gotcha | inputs only | `[lambda x: x < f.threshold for f in features]` — all closures bind same `f` |
| V4_generator_exhaust | iterator semantics | inputs only | `filter_window` returns a generator; `report()` iterates it 4 times → only first sees data |

Each verified end-to-end: buggy code → `accuracy=False`, known fix → `accuracy=True`.

## Results

### Headline

| | accuracy | fresh tokens | total tokens | wall (s) | tool calls | pdb invocations |
|---|---|---:|---:|---:|---:|---:|
| without-skill (12) | **100%** | 30,957 | 100,127 | 76.1 | 6.9 | 0.00 |
| with-skill (12) | **92%** | 36,735 | 158,199 | 79.4 | 11.1 | 3.17 |
| **delta** | **−8 pp** | +19% | +58% | +4% | +60% | +3.17 |

**For the first time across all three sweeps, the skill hurt accuracy.** 1 of 12 with-skill runs (V3 late-binding run 1) failed; 0 of 12 without-skill runs failed.

Cost: **$0.55 vs $0.75** with-skill (+36%).

### Per case

| case | wo acc | w acc | wo fresh | w fresh | wo wall | w wall | w pdb |
|---|---|---|---:|---:|---:|---:|---:|
| V1_blind_csv | 100% | 100% | 47,293 | 44,646 (-6%) | 90.3s | 82.7s | **1.0** |
| V2_pandas_chained | 100% | 100% | 26,291 | 31,603 (+20%) | 83.8s | 78.7s | **4.0** |
| V3_late_binding | 100% | **67%** | 23,985 | 37,548 (+57%) | 62.7s | 94.5s | **5.3** |
| V4_generator_exhaust | 100% | 100% | 26,255 | 33,144 (+26%) | 67.6s | 61.8s | **2.3** |

### Activation rate

**9 of 12** with-skill runs invoked pdb (75%), with a mean of **3.17 invocations per run**. The skill is being followed.

(Note on data quality: the original `extract_metrics.py` regex matched only `python -m pdb`, missing `python3 -m pdb`. The fix at `harness/extract_metrics.py` now matches `python3`, `python3.12`, etc. All three sweeps' CSVs were re-extracted with the corrected regex; the numbers above are the corrected ones. v1 and v2 findings docs have been updated.)

## What the per-case results actually say

### V1_blind_csv — the case I designed *specifically* for pdb, and the agent ignored pdb
Mean pdb usage: 1.0 per run (1 run used pdb once, 2 runs used it 0 times). The model preferred just running the script, reading the traceback for the offending row index, and inspecting the CSV directly with `head -75 transactions.csv | tail -5` or similar shell tooling. That's a reasonable engineering choice — the file is human-readable text, so the model treats it like one.

Both conditions hit 100% in 90s and ~47k fresh tokens. Skill made no difference; agent solved it by reading the CSV either way.

### V2_pandas_chained — pdb used heavily, accuracy already at 100%
Mean **4 pdb invocations** per with-skill run. The agent clearly tried to understand what `df[mask]['col'] = X` actually does. But the without-skill agent also got 100% — likely by just knowing the pandas idiom (`.loc[mask, col] = X`) and reading the error/warning if any. Net result: pdb cost +63% total tokens and bought nothing.

### V3_late_binding — pdb used aggressively, accuracy DROPPED
Most pdb-heavy case (mean 5.3 invocations) and the only case where the skill made accuracy worse. The failing run (run 1) finished in 35 seconds with 0 pdb invocations and made a fast bad call. The other two runs used pdb 6 and 1 times and got it right. So the regression isn't "pdb made it worse" — it's "the workflow framing changed something about the agent's first-pass behavior on this case."

Possible explanation: the AGENTS.md preamble nudges the agent into a "reproduce + investigate" mindset, and on a Python gotcha where the *correct* fix is a one-line idiom (`lambda x, t=f.threshold: x < t`), that framing led one run to a different (wrong) hypothesis. Without the framing, the model went straight to the well-known idiom.

This is a real risk signal. Sample size is tiny (1 fail in 3), but it's the first time we've seen the skill hurt anything.

### V4_generator_exhaust — modest pdb use, no accuracy delta
Mean 2.3 pdb invocations. With-skill +32% total tokens, similar wall time, same 100% accuracy. The bug is visible from reading — agent solved it either way.

## What v3 finally shows

After three sweeps and 72 invocations:

1. **Accuracy ceiling held in v1 and v2 (100% both conditions).** In v3, the ceiling held only for the *without*-skill condition. With-skill DROPPED to 92%.
2. **Skill activation was always high** (67–92% across sweeps). The model follows the AGENTS.md nudge most of the time, even on bugs it could solve without.
3. **Tokens always worsen with skill** (+19% to +279% total tokens depending on sweep). This is now a robust finding.
4. **On bugs the model *can* solve from source-reading, the skill is dead weight.** All four v3 cases were solved 100% without-skill; the with-skill condition added cost and one regression.

The original hypothesis ("pdb workflow improves agent performance on Python bugs") has not been confirmed by any of the three sweeps. The most charitable read is: the bugs in this eval are still solvable by source-reading, so the skill has nothing to add. The harsher read is: even when the skill *is* used (3+ pdb invocations per run), it doesn't translate to fewer tokens, faster runs, or better accuracy.

## What I'd try next, in priority order

1. **Force the agent to use less context.** If the model can read all the source, it just does. Make some source unavailable (e.g., the bug is in a compiled-only module, or a function whose body is replaced with `# proprietary`) — only pdb can see the runtime behavior. This is the cleanest test of pdb-vs-source-reading.
2. **Weaker model.** Llama-3-8B / Mistral-7B. Their source-reading reliability is lower, so the structured workflow should pay off more.
3. **Real codebases.** Take a recent commit from a Django or FastAPI repo that fixed a bug, run the agent on the pre-fix state, see if pdb helps. This is much closer to "real" debugging.
4. **Reduce the skill's token tax.** A 5-line AGENTS.md that just says "use `python3 -m pdb -cc 'b N' -cc c -cc 'pp locals()'` for inspection" instead of the 32-line current version. If the skill helps at all, the leaner form should win.

## Side discovery: my own metric was undercounting

The original `extract_metrics.py` regex was `python\s+-m\s+pdb`, which doesn't match `python3 -m pdb` (the actual invocation used by macOS-default agents). That made v1 and v2 look like the agent had low pdb activation. Corrected numbers: v1 ~92% activation, v2 ~67%. The previous v1 and v2 findings docs have been updated. The conclusion that "the skill is a tax" survives the correction; only the "activation collapsed" sub-claim from v2 was wrong.
