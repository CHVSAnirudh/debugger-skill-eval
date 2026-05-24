# Findings

Each file documents one experiment run with date, setup, raw numbers, and interpretation. Newer runs may refute older conclusions — files are kept as-is.

| File | Date | Model | Cases | Conditions × runs | One-line result |
|---|---|---|---|---|---|
| [v1-easy-bugs.md](v1-easy-bugs.md) | 2026-05-19 | Kimi K2.6 (Fireworks) | 8 short (~15 LOC) Python bugs | 2 × 3 = 48 runs | Accuracy 100% in both conditions; with-skill +42% fresh tokens (+83% total incl. cache); 92% pdb activation. |
| [v2-hard-bugs.md](v2-hard-bugs.md) | 2026-05-19 | Kimi K2.6 (Fireworks) | 4 longer (~100-200 LOC) Python bugs needing runtime inspection | 2 × 3 = 24 runs | Accuracy 100% in both conditions; 67% pdb activation (heavy: 8/run on H4); with-skill +112% fresh tokens, +279% total, +121% wall time — skill is a pure tax. |
| [v3-real-world-bugs.md](v3-real-world-bugs.md) | 2026-05-19 | Kimi K2.6 (Fireworks) | 4 cases targeting blind data, pandas internals, closure gotcha, generator exhaustion | 2 × 3 = 24 runs | **First accuracy regression:** without-skill 100%, with-skill 92% (1 V3 run failed). 75% pdb activation, mean 3.17 invocations/run. Skill costs +58% total tokens and now costs accuracy too. |
| [v4-weaker-model.md](v4-weaker-model.md) | 2026-05-19 | **gpt-oss-20b** (Fireworks) | All 16 cases from v1+v2+v3 re-run on weaker model | 2 × 3 × 16 = 96 runs | **Hypothesis confirmed (with twist):** skill helps weaker model — v1 +8pp, v3 **+25pp** accuracy. BUT gpt-oss never invokes pdb (0 calls across 96 runs); the lift comes from the reproduce/verify workflow framing, not from the debugger. Cost: $0.12 total (38× cheaper than Kimi). |

**Metrics caveat:** the original `extract_metrics.py` regex matched only `python -m pdb`, missing `python3 -m pdb` (the actual invocation on macOS). All numbers across all three docs have been re-extracted with the corrected regex. Activation rates above are the corrected figures.
