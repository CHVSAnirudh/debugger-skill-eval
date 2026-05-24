# v4 — Weaker model (gpt-oss-20b) (2026-05-19)

## Question

v1/v2/v3 ran on Kimi K2.6, where the skill never improved accuracy (and on v3 hurt it). My open hypothesis after v3: a smaller / less capable model would benefit more from the structured pdb workflow.

This run re-runs **all three case sets** (v1 + v2 + v3 — same cases, same harness, same `AGENTS.md`) against **gpt-oss-20b** (OpenAI's 20B-parameter open-source model via Fireworks).

## Setup

- **Model:** `fireworks-ai/accounts/fireworks/models/gpt-oss-20b` (passed via `opencode run --model`).
- **Cases:** all 16 cases re-used unchanged (`cases/`, `cases_hard/`, `cases_v3/`).
- **Runs:** 3 per (case × condition) → **96 invocations** (matching the prior Kimi runs).
- **Total cost: $0.12** — gpt-oss-20b is roughly **38× cheaper** than Kimi K2.6 per token for this workload.

## Headline result: the skill helps the weaker model

| sweep | Kimi K2.6 Δacc | gpt-oss-20b Δacc |
|---|---:|---:|
| v1 (easy) | +0pp | **+8pp** |
| v2 (hard) | +0pp | +0pp |
| v3 (real-world) | **−8pp** | **+25pp** |

On v3 specifically, gpt-oss went from 33% → 58% with the skill. With Kimi the same case set went 100% → 92%. The skill's sign flipped from "hurts" to "helps" when the underlying model got weaker.

## Detailed numbers

### gpt-oss-20b overall (mean per invocation)

| sweep | condition | n | accuracy | fresh | total | wall (s) | cost | pdb |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| v1 | without-skill | 24 | 62% | 14,728 | 34,373 | 45.0 | $0.0009 | 0 |
| v1 | with-skill | 24 | 71% | 19,313 | 73,239 | 68.2 | $0.0013 | 0 |
| v2 | without-skill | 12 | 75% | 18,683 | 53,514 | 58.0 | $0.0013 | 0 |
| v2 | with-skill | 12 | 75% | 21,205 | 62,861 | 67.0 | $0.0015 | 0 |
| v3 | without-skill | 12 | 33% | 16,055 | 35,086 | 34.8 | $0.0011 | 0 |
| v3 | with-skill | 12 | **58%** | 21,308 | 65,011 | 56.6 | $0.0015 | 0 |

### Side-by-side (mean per invocation)

| sweep | metric | Kimi wo | Kimi w | Kimi Δ | gpt-oss wo | gpt-oss w | gpt-oss Δ |
|---|---|---:|---:|---:|---:|---:|---:|
| v3 | accuracy | 100% | 92% | **−8pp** | 33% | 58% | **+25pp** |
| v3 | fresh tokens | 30,956 | 36,735 | +19% | 16,055 | 21,308 | +33% |
| v3 | wall (s) | 76.1 | 79.4 | +4% | 34.8 | 56.6 | +63% |
| v3 | cost | $0.0458 | $0.0623 | +36% | $0.0011 | $0.0015 | +36% |
| v3 | pdb/run | 0.00 | 3.17 | +3.17 | 0.00 | **0.00** | +0.00 |

## The surprising mechanism: the skill helps **without** the agent ever invoking pdb

**gpt-oss-20b never mentioned pdb anywhere across all 96 runs.** I audited every channel where a mention could appear:

| channel | scope | "pdb" mentions |
|---|---|---:|
| Bash commands | 48 with-skill sessions | 0 |
| File writes | 48 with-skill sessions | 0 |
| File edits | 48 with-skill sessions | 0 |
| Assistant text outputs | 48 with-skill sessions | 0 |
| Hidden reasoning chain-of-thought | 48 with-skill sessions (up to 28k chars/session) | 0 |

The reasoning blocks ARE populated — gpt-oss-20b emits substantial internal monologue (one V1 session had 28,008 chars of reasoning) — but it never thinks about pdb. The `AGENTS.md` content does reach the model (input tokens go from 14.4k → 18.6k with-skill in v3, ~4k extra accounting for the file's contents), so the skill IS in context. The model just ignores the pdb-specific part of it.

I confirmed this by inspecting individual sessions:

### V2_pandas_chained (0% → 67% with skill)
- **without-skill runs:** 2 of 3 made **zero tool calls** — the model produced text and stopped without ever editing `buggy.py`. The third run did one read + one write but the fix was wrong.
- **with-skill runs:** all 3 read the file, edited it toward the correct `.loc` idiom, and (in 2 of 3 cases) ran `python buggy.py` to verify. The skill didn't teach pdb — it prevented premature give-up.

### V4_generator_exhaust (33% → 67% with skill)
Same pattern: with-skill runs were more likely to run the script, see the wrong output, and iterate on a real fix.

The skill is functioning as a "you must reproduce and verify" enforcement — that's where the +25pp comes from on v3.

### Behavioral diffs (with vs without skill, gpt-oss-20b)

| metric | v3 without-skill | v3 with-skill | Δ |
|---|---:|---:|---:|
| zero-action runs (no tool calls at all) | 4 of 12 (33%) | 3 of 12 (25%) | -8pp |
| avg tool calls per run | 2.0 | 4.3 | **+115%** |
| avg edit calls per run | 0.4 | 1.0 | **+150%** |
| avg bash calls per run | 0.2 | 0.5 | **+150%** |

The skill roughly doubles the work the model does. None of that work involves pdb. The lift is from "do more, give up less," not from the debugger.

## Per-case breakdown for gpt-oss-20b

### v1 (easy bugs)

| case | wo | w | Δ |
|---|---:|---:|---:|
| 01_logic_offbyone | 67% | 33% | **−33pp** |
| 02_logic_conditional | 100% | 67% | **−33pp** |
| 03_state_aliasing | 33% | 67% | +33pp |
| 04_state_classvar | 100% | 100% | 0 |
| 05_exc_keyerror | 33% | 100% | **+67pp** |
| 06_exc_typeerror | 100% | 100% | 0 |
| 07_async_race | 33% | 33% | 0 |
| 08_async_await_missing | 33% | 67% | +33pp |

High variance. Net +8pp but two cases regressed by one run each. With 3 runs/cell this is partly noise.

### v2 (hard bugs)

| case | wo | w | Δ |
|---|---:|---:|---:|
| H1_rolling_stats | 67% | 67% | 0 |
| H2_token_bucket | 100% | 100% | 0 |
| H3_graph_bfs | 67% | 67% | 0 |
| H4_expr_parser | 67% | 67% | 0 |

Completely flat. The skill neither helps nor hurts on this case set with gpt-oss.

### v3 (real-world bugs)

| case | wo | w | Δ |
|---|---:|---:|---:|
| V1_blind_csv | 67% | 67% | 0 |
| V2_pandas_chained | **0%** | 67% | **+67pp** |
| V3_late_binding | 33% | 33% | 0 |
| V4_generator_exhaust | 33% | 67% | +33pp |

V2 is the headline: 0% without-skill → 67% with-skill. The skill rescued a complete failure mode. V4 also showed real lift. V1 and V3 didn't move.

## Comparison: where the two models diverge

| dimension | Kimi K2.6 | gpt-oss-20b |
|---|---|---|
| Baseline accuracy (no skill) | 100% / 100% / 100% across v1/v2/v3 | 62% / 75% / 33% |
| pdb usage when skill present | 3.04 / 4.58 / 3.17 per run | 0 / 0 / 0 |
| Skill activation pattern | Follows the literal pdb instruction | Follows the workflow but skips the pdb step |
| Skill effect on accuracy | 0 / 0 / **−8pp** | **+8** / 0 / **+25pp** |
| Cost per run (with skill) | ~$0.04–0.09 | ~$0.0015 (38× cheaper) |
| Failure mode without skill | Solves anyway by reading | Gives up before touching the file |

## What this finally tells us

After 4 sweeps and 192 invocations across two models, here's the picture that I believe holds up:

1. **The original hypothesis ("debugger workflow helps") is partly validated, but the mechanism isn't what I thought.** The skill helps a weak model — but not by enabling pdb. It helps by forcing the model into a "reproduce → fix → verify" loop instead of letting it give up after one read.

2. **For capable models, the skill is a tax** (consistent with v1–v3 on Kimi). Adding it can also hurt accuracy if it nudges the model into a longer-than-needed investigation path (the v3 Kimi −8pp result).

3. **The "use pdb" part of `AGENTS.md` is doing none of the work on gpt-oss-20b**, which never runs pdb. The reproduce/verify scaffolding around it is doing all the lifting. A leaner AGENTS.md focused only on workflow (and not on pdb invocation syntax) would likely give similar lift at lower token cost.

4. **Sample sizes are small.** 3 runs per cell means a single run flipping can move a case by 33pp. The aggregate v3 +25pp delta on gpt-oss is real (8 of 12 with-skill runs passed vs 4 of 12 without), but per-case calls should be taken with caution.

## Updated recommendations

| use case | recommendation |
|---|---|
| Capable model on bugs it can read | **Skip the skill.** It's net negative. |
| Capable model on bugs it can't read (e.g. data-dependent, multi-repo) | Probably skip pdb-specific instructions; a reproduce/verify reminder is enough. |
| Weak model (≤20B params) on anything beyond toy code | **Use a workflow scaffold** — but drop the pdb-specific bits. The structured loop is what matters, not the debugger choice. |

## Open follow-ups

1. **Test a "workflow-only" AGENTS.md** that says "reproduce, fix, verify" but doesn't mention pdb. If it matches the current results on gpt-oss, my theory is confirmed and the v1 token tax shrinks.
2. **Try a *middle* model** (Llama-3-70B, Mistral-Large) to see where the sign flips between "skill helps" and "skill is a tax."
3. **Increase runs/cell to 5–10** before drawing firm conclusions on individual cases.
4. **Take this to a real-world bug benchmark** (BugsInPy, QuixBugs) for external validity.
