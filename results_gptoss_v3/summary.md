# debugger-skill-eval results

## Overall (mean per invocation)

| condition | n | accuracy | tokens_total | tokens_in | tokens_out | cost ($) | wall (s) | tool_calls | pdb_calls |
|---|---|---|---|---|---|---|---|---|---|
| without-skill | 12 | 33% | 35086 | 14404 | 1652 | 0.0011 | 34.8 | 2.0 | 0.00 |
| with-skill | 12 | 58% | 65011 | 18604 | 2704 | 0.0015 | 56.6 | 4.3 | 0.00 |
| **delta (with-without)** | - | +25% | +29925 | +4200 | +1052 | +0.0004 | +21.8 | +2.3 | +0.00 |

## Per-case (mean per invocation)

| case | condition | n | accuracy | tokens_total | wall (s) | pdb_calls |
|---|---|---|---|---|---|---|
| V1_blind_csv | without-skill | 3 | 67% | 79349 | 47.3 | 0.00 |
| V1_blind_csv | with-skill | 3 | 67% | 104170 | 89.8 | 0.00 |
| V2_pandas_chained | without-skill | 3 | 0% | 19420 | 38.1 | 0.00 |
| V2_pandas_chained | with-skill | 3 | 67% | 87658 | 58.9 | 0.00 |
| V3_late_binding | without-skill | 3 | 33% | 20594 | 26.5 | 0.00 |
| V3_late_binding | with-skill | 3 | 33% | 32346 | 41.2 | 0.00 |
| V4_generator_exhaust | without-skill | 3 | 33% | 20981 | 27.5 | 0.00 |
| V4_generator_exhaust | with-skill | 3 | 67% | 35871 | 36.6 | 0.00 |
