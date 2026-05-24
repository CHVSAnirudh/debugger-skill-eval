# v2 — Harder bugs (2026-05-19)

## Question

v1 showed the skill didn't help on 15-line one-liner bugs because the model already solved them by reading source. v2 asks: does the skill help when the buggy code is ~100-200 LOC and the bug genuinely benefits from runtime inspection?

## Setup

- Same harness, same model (Kimi K2.6 / Fireworks), same `AGENTS.md`.
- Cases under `cases_hard/` (4 cases, ~100-200 LOC each), all stdlib only.
- 4 × 2 × 3 = **24 invocations**. Total cost: $1.50.

### The cases

| case | LOC | bug | why pdb should help |
|---|---:|---|---|
| H1_rolling_stats | 115 | cache invalidation only on eviction, not on new-extremum | bug shows only across multiple `add`+read interleavings — inspecting cache state mid-sequence makes it obvious |
| H2_token_bucket | 95 | `int(elapsed * rate)` truncates fractional refills | bug is value-dependent — running with a 0.5s refill and printing `new_tokens` exposes truncation |
| H3_graph_bfs | 85 | stack instead of queue + distance overwrites on revisit, gives DFS path-length | reading the loop looks fine; printing `queue` and `distances` mid-traversal shows the wrong dequeue order |
| H4_expr_parser | 120 | `*`/`/` parses with `if` + right-recursion → not left-associative | reading the term() body looks plausible; tracing parse of `20/2/5` shows the recursion goes wrong |

All four pass tests when given a known fix and fail on the buggy code (`accuracy=False` baseline).

## Results

### Headline

| | accuracy | fresh tokens | cache_read | total tokens | wall (s) | tool calls | pdb invocations |
|---|---|---:|---:|---:|---:|---:|---:|
| without-skill (12) | 100% | 21,165 | 45,605 | 66,770 | 66.5 | 4.8 | 0.00 |
| with-skill (12) | 100% | 44,938 | 208,459 | 253,397 | 146.7 | 14.5 | 4.58 |
| **delta** | **+0pp** | **+112%** | **+357%** | **+279%** | **+121%** | +203% | +0.25 |

Cost: **$0.39 vs $1.11** (with-skill nearly 3× more).

### Per case (fresh tokens, input + output)

| case | wo | w | Δ |
|---|---:|---:|---:|
| H3_graph_bfs | 27,618 | 49,106 | +78% |
| H1_rolling_stats | 24,492 | 45,273 | +85% |
| H2_token_bucket | 16,055 | 31,321 | +95% |
| H4_expr_parser | 16,496 | 54,054 | **+228%** |

### Skill activation (corrected)

**8 of 12** with-skill runs invoked pdb (67%, mean 4.58 invocations per run). The original number in this doc was 3/12 — that was wrong, due to a regex bug in `extract_metrics.py` that didn't match `python3 -m pdb` (only `python -m pdb`). The corrected per-case breakdown:

| case | pdb-using runs (of 3) | mean pdb invocations |
|---|---|---:|
| H1_rolling_stats | 2 | 3.33 |
| H2_token_bucket | 1 | 2.67 |
| H3_graph_bfs | 2 | 4.33 |
| H4_expr_parser | 3 | **8.00** |

So activation didn't collapse — the original claim in this doc was based on bad data. The skill was being followed roughly as much as in v1 (67% vs 92%). What v2 actually shows is: the skill is followed, used heavily on H4 in particular (8 pdb calls per run), and *still* produces +279% total tokens for +0% accuracy.

### Variance is large

Per-run with-skill totals (tokens_total):

| case | run 1 | run 2 | run 3 |
|---|---:|---:|---:|
| H1_rolling_stats | 451,417 | 95,249 | 279,305 |
| H2_token_bucket | 82,770 | 58,721 | 217,700 |
| H3_graph_bfs | 208,042 | 85,769 | 360,014 |
| H4_expr_parser | 160,483 | 304,806 | **736,491** |

The H4 run-3 outlier alone is ~12× a typical without-skill run. Without that one run, H4's with-skill mean drops from 400k to 233k.

## Interpretation

### Kimi K2.6 still solves them by reading source

100% accuracy in both conditions on cases I designed specifically to be hard to spot statically. So either the bugs aren't as static-hard as I thought, or Kimi is more thorough than I gave it credit for. Either way, **accuracy is still at ceiling and the skill cannot demonstrate help on this axis**.

### The agent does follow the skill — and it still doesn't help

Corrected activation: 67% (8/12 with-skill runs used pdb, mean 4.58/run). H4_expr_parser alone averaged 8 pdb invocations per run. So the model isn't ignoring the workflow — it just isn't getting value from following it. The reading-source path is fast enough and accurate enough that pdb-then-edit adds latency and tokens without changing the verdict.

### The token tax is real whether pdb is used or not

Even in the 4 with-skill runs that *didn't* invoke pdb (per the corrected count), they still used +84%+ more fresh tokens than without-skill — purely from carrying the AGENTS.md text in context. In runs that *did* invoke pdb (most of them), the additional cost from each pdb call's stdout being re-fed into context compounds.

### Larger code → larger variance

Three with-skill runs blew past 250k tokens. The agent occasionally goes into a long iteration loop on hard cases (re-reading files, running tests, checking outputs) which 3× a normal run. The without-skill condition has fewer such blowups — possibly because without the "follow this debugger workflow" framing, the agent commits faster.

## What this experiment cannot conclude

Same caveat as v1: with accuracy at ceiling, the headline hypothesis (pdb improves fix rate) is still untestable here. v2 *did* refine one signal — that the skill **costs more on longer programs**, both because of the file-size overhead and because the agent's behavior gets more variable. But "doesn't help" is not the same as "actively hurts on truly hard bugs" — which we still don't have a clean test for.

## Worth trying next

1. **Bugs that the model demonstrably can't solve without runtime data.** Examples: bugs in code that depends on the *actual values* of opaque inputs (e.g., parsing a file the model can only see by reading), bugs in code that uses an external library the model misunderstands, real-world bugs from BugsInPy where the static signal is genuinely insufficient.
2. **A much weaker model.** Kimi K2.6 might just be too capable. Llama-3-8B or similar would likely benefit more from structured workflows.
3. **Cap turns and re-test.** Set `--max-turns 5` on opencode runs to force the model to use pdb instead of iterating speculatively. If the skill cuts the failure rate under a tight budget, that's a real win.
4. **A leaner skill file.** 32-line AGENTS.md adds noticeable cache-read overhead. A 5-line variant might keep activation without the tax.

## Honest take

After two sweeps (72 invocations, $3.04 total), the most defensible claim is: **for capable models on bugs they can solve, adding a "use the debugger" skill is a token tax with no accuracy benefit.** The skill is engineered to provide value only on bugs the model *can't otherwise solve*, and we still don't have those bugs in this eval. The next milestone is building a case set where Kimi K2.6 drops below 100% baseline — only then can the skill demonstrate (or fail to demonstrate) what we actually want to measure.
