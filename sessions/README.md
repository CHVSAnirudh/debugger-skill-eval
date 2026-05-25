# Sample sessions

Raw opencode session exports from the v2 (hard-cases) sweep on **Kimi K2.6** with the debugger skill enabled. These are the runs where the model used `pdb` most heavily — useful as concrete evidence the agent actually engages with the debugger.

All exports are sanitized (`opencode export --sanitize`).

| # | case | run | session JSON | pdb calls | total tokens |
|---|---|---:|---|---:|---:|
| 1 | H4_expr_parser | 3 | [ses_1c09de905ffelieLX8pAlt3EYN.json](ses_1c09de905ffelieLX8pAlt3EYN.json) | 13 | 736,491 |
| 2 | H2_token_bucket | 3 | [ses_1c0b476e0ffe4QYs6UvKJlzhol.json](ses_1c0b476e0ffe4QYs6UvKJlzhol.json) | 8 | 217,700 |
| 3 | H3_graph_bfs | 1 | [ses_1c0afb756ffepYLPPWEmYv9Dhj.json](ses_1c0afb756ffepYLPPWEmYv9Dhj.json) | 7 | 208,042 |
| 4 | H1_rolling_stats | 1 | [ses_1c0be92c1ffeH8w5SAoLbZ90em.json](ses_1c0be92c1ffeH8w5SAoLbZ90em.json) | 6 | 451,417 |
| 5 | H3_graph_bfs | 3 | [ses_1c0accff1ffecNCsD3pzfXOTUd.json](ses_1c0accff1ffecNCsD3pzfXOTUd.json) | 6 | 360,014 |

All 5 sessions ended with `accuracy=True`.

## How to view

JSON files are large and best viewed in a editor or via `jq`. Each file contains:
- `info` — session metadata, total tokens, cost
- `messages` — full assistant/user/tool message history with timestamps and per-message token usage
- `parts` — individual content parts inside each message (text, reasoning, tool calls)

The pdb invocations appear as `part.type == "tool"` entries where `tool == "bash"` and `state.input.command` starts with `python3 -m pdb`.

To replay one locally:

```bash
opencode import sessions/ses_1c09de905ffelieLX8pAlt3EYN.json
```
