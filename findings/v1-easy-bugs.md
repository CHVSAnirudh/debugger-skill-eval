# v1 — Easy bugs (2026-05-19)

## Question

Does an `AGENTS.md` skill that teaches `pdb` reduce tokens, reduce wall time, or improve fix accuracy when an LLM coding agent is asked to fix small Python bugs?

## Setup

- **Agent:** opencode 1.3.13, non-interactive (`opencode run "<prompt>"`)
- **Model:** Kimi K2.6 via Fireworks (`accounts/fireworks/models/kimi-k2p6`) — not a thinking model (`reasoning` tokens = 0 across all 48 sessions)
- **Skill mechanism:** `AGENTS.md` copied into the case working directory in the `with-skill` condition (32 lines instructing the agent to use `python -m pdb -cc <cmd>` for pre-mortem inspection and `-c continue` for post-mortem on crashes). Absent in `without-skill`.
- **Cases:** 8 hand-crafted bugs (~15 LOC each), 2 per category — logic / state / exception / async. See `cases/01..08/`.
- **Grading:** hidden pytest suite per case + `python buggy.py < inputs.json` golden-output diff. `accuracy = pytest_passed AND golden_match`.
- **Runs:** 3 per (case × condition) → **48 total invocations**.
- **Metrics:** parsed from opencode's local sqlite at `~/.local/share/opencode/opencode.db` (tables `session`, `message`, `part`).
- **Total cost:** $1.54.

## Results

### Headline

| | accuracy | fresh tokens (in+out) | cache_read | total tokens | wall (s) | tool calls | pdb invocations |
|---|---|---:|---:|---:|---:|---:|---:|
| without-skill (24) | 100% | 17,517 | 35,740 | 53,257 | 67.9 | 4.2 | 0.00 |
| with-skill (24) | 100% | 24,818 | 72,686 | 97,504 | 73.6 | 7.9 | 3.04 |
| **delta** | **+0pp** | **+42%** | +103% | +83% | +8% | +88% | +0.79 |

(`reasoning` field was 0 for all sessions — Kimi K2.6 doesn't emit thinking tokens, so we aren't undercounting.)

### Per case (fresh tokens, input + output)

| case | wo | w | Δ |
|---|---:|---:|---:|
| 02_logic_conditional | 21,796 | 23,280 | +7% |
| 06_exc_typeerror | 17,225 | 20,268 | +18% |
| 08_async_await_missing | 17,760 | 23,221 | +31% |
| 04_state_classvar | 18,104 | 25,708 | +42% |
| 05_exc_keyerror | 17,863 | 25,326 | +42% |
| 03_state_aliasing | 15,051 | 24,985 | +66% |
| 07_async_race | 14,405 | 23,871 | +66% |
| 01_logic_offbyone | 17,932 | 31,885 | +78% |

### Per case (wall time)

| case | wo (s) | w (s) | Δ |
|---|---:|---:|---:|
| 02_logic_conditional | 72.0 | 62.0 | −14% |
| 03_state_aliasing | 67.0 | 58.3 | −13% |
| 06_exc_typeerror | 69.7 | 60.7 | −13% |
| 05_exc_keyerror | 74.4 | 61.4 | −17% |
| 01_logic_offbyone | 57.6 | 54.7 | −5% |
| 07_async_race | 58.8 | 61.3 | +4% |
| 08_async_await_missing | 74.8 | 77.9 | +4% |
| 04_state_classvar | 68.8 | **152.3** | **+121%** |

Case 04 was an outlier with very high variance (stdev 130s with-skill vs 14s without) — one run dominated the mean.

### Skill activation rate

The agent ran pdb in **22 of 24** with-skill runs (92%; mean 3.04 invocations/run). Only 2 runs skipped pdb entirely.

(Note: the original numbers reported here showed 18/24 and 0.79/run. That was a bug in `extract_metrics.py` — the regex matched `python -m pdb` but not the macOS-default `python3 -m pdb` opencode actually used. Numbers above are corrected. Conclusions are unchanged; if anything, the skill was followed *more* than originally believed and still didn't help.)

## Interpretation

1. **Accuracy is at ceiling.** Kimi K2.6 solves 100% of these bugs in both conditions. There is no headroom for the skill to demonstrate a fix-rate gain. Any conclusion about "the skill makes the agent more correct" is unfalsifiable from this data.

2. **Tokens are uniformly worse with the skill.** Every case used more fresh tokens with the skill (+7% to +78%). Even after stripping cache_read entirely, the skill costs ~42% more. The driver is the pdb invocation itself: stdout from `python -m pdb …` gets re-read each turn, and the AGENTS.md preamble adds baseline input.

3. **Wall time told a more interesting story.** 5/8 cases were *faster* with the skill (−5% to −17%). The likely mechanism: pdb resolves "what's the value of X at line N" in one bash call vs the agent thinking longer and editing speculatively. But the gain doesn't justify the token cost, and case 04 had one slow run that flipped its mean to +121%.

4. **The skill is consistently followed.** 92% activation rate (corrected) — the agent ran pdb in 22 of 24 with-skill runs, ~3 invocations per run. The AGENTS.md nudge is being honored across nearly every run; it just doesn't translate to a measurable gain.

## What this run cannot tell us

The hypothesis is *"pdb helps the agent fix bugs."* On bugs solvable by reading 15 lines of source, the model needs no help — so the experiment can't measure the help pdb provides. The setup is wrong for the question. To test the hypothesis, you need bugs where source-reading is insufficient.

## Action items

- Build a v2 with **longer programs** (≥150 LOC) and bugs that **require runtime inspection** — see v2 doc.
- A leaner AGENTS.md (5 lines vs 32) might keep the activation signal without the token tax — worth a future ablation.
- 5 runs per cell (vs 3) would tighten variance; case 04 demonstrates 3 is not enough.
