# debugger-skill-eval results

## Overall (mean per invocation)

| condition | n | accuracy | tokens_total | tokens_in | tokens_out | cost ($) | wall (s) | tool_calls | pdb_calls |
|---|---|---|---|---|---|---|---|---|---|
| without-skill | 12 | 100% | 66770 | 19490 | 1675 | 0.0325 | 66.5 | 4.8 | 0.00 |
| with-skill | 12 | 100% | 253397 | 39478 | 5460 | 0.0927 | 146.7 | 14.5 | 4.58 |
| **delta (with-without)** | - | +0% | +186627 | +19988 | +3785 | +0.0602 | +80.2 | +9.8 | +4.58 |

## Per-case (mean per invocation)

| case | condition | n | accuracy | tokens_total | wall (s) | pdb_calls |
|---|---|---|---|---|---|---|
| H1_rolling_stats | without-skill | 3 | 100% | 66039 | 71.4 | 0.00 |
| H1_rolling_stats | with-skill | 3 | 100% | 275324 | 119.2 | 3.33 |
| H2_token_bucket | without-skill | 3 | 100% | 56066 | 57.9 | 0.00 |
| H2_token_bucket | with-skill | 3 | 100% | 119730 | 66.2 | 2.67 |
| H3_graph_bfs | without-skill | 3 | 100% | 88370 | 76.9 | 0.00 |
| H3_graph_bfs | with-skill | 3 | 100% | 217942 | 132.0 | 4.33 |
| H4_expr_parser | without-skill | 3 | 100% | 56605 | 59.8 | 0.00 |
| H4_expr_parser | with-skill | 3 | 100% | 400593 | 269.3 | 8.00 |
