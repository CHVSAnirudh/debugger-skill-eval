# debugger-skill-eval results

## Overall (mean per invocation)

| condition | n | accuracy | tokens_total | tokens_in | tokens_out | cost ($) | wall (s) | tool_calls | pdb_calls |
|---|---|---|---|---|---|---|---|---|---|
| without-skill | 12 | 100% | 100127 | 29224 | 1733 | 0.0458 | 76.1 | 6.9 | 0.00 |
| with-skill | 12 | 92% | 158199 | 34115 | 2620 | 0.0623 | 79.4 | 11.1 | 3.17 |
| **delta (with-without)** | - | -8% | +58071 | +4891 | +888 | +0.0166 | +3.3 | +4.2 | +3.17 |

## Per-case (mean per invocation)

| case | condition | n | accuracy | tokens_total | wall (s) | pdb_calls |
|---|---|---|---|---|---|---|
| V1_blind_csv | without-skill | 3 | 100% | 144998 | 90.3 | 0.00 |
| V1_blind_csv | with-skill | 3 | 100% | 166338 | 82.7 | 1.00 |
| V2_pandas_chained | without-skill | 3 | 100% | 115724 | 83.8 | 0.00 |
| V2_pandas_chained | with-skill | 3 | 100% | 188968 | 78.7 | 4.00 |
| V3_late_binding | without-skill | 3 | 100% | 70462 | 62.7 | 0.00 |
| V3_late_binding | with-skill | 3 | 67% | 185791 | 94.5 | 5.33 |
| V4_generator_exhaust | without-skill | 3 | 100% | 69325 | 67.6 | 0.00 |
| V4_generator_exhaust | with-skill | 3 | 100% | 91700 | 61.8 | 2.33 |
