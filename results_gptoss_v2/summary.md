# debugger-skill-eval results

## Overall (mean per invocation)

| condition | n | accuracy | tokens_total | tokens_in | tokens_out | cost ($) | wall (s) | tool_calls | pdb_calls |
|---|---|---|---|---|---|---|---|---|---|
| without-skill | 12 | 75% | 53514 | 16478 | 2205 | 0.0013 | 58.0 | 3.8 | 0.00 |
| with-skill | 12 | 75% | 62861 | 18525 | 2679 | 0.0015 | 67.0 | 4.2 | 0.00 |
| **delta (with-without)** | - | +0% | +9348 | +2047 | +474 | +0.0002 | +9.0 | +0.4 | +0.00 |

## Per-case (mean per invocation)

| case | condition | n | accuracy | tokens_total | wall (s) | pdb_calls |
|---|---|---|---|---|---|---|
| H1_rolling_stats | without-skill | 3 | 67% | 40845 | 53.2 | 0.00 |
| H1_rolling_stats | with-skill | 3 | 67% | 47711 | 68.4 | 0.00 |
| H2_token_bucket | without-skill | 3 | 100% | 75444 | 62.4 | 0.00 |
| H2_token_bucket | with-skill | 3 | 100% | 62136 | 60.7 | 0.00 |
| H3_graph_bfs | without-skill | 3 | 67% | 47095 | 46.3 | 0.00 |
| H3_graph_bfs | with-skill | 3 | 67% | 62770 | 64.9 | 0.00 |
| H4_expr_parser | without-skill | 3 | 67% | 50670 | 69.9 | 0.00 |
| H4_expr_parser | with-skill | 3 | 67% | 78828 | 74.0 | 0.00 |
