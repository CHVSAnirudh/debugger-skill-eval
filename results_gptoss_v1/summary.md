# debugger-skill-eval results

## Overall (mean per invocation)

| condition | n | accuracy | tokens_total | tokens_in | tokens_out | cost ($) | wall (s) | tool_calls | pdb_calls |
|---|---|---|---|---|---|---|---|---|---|
| without-skill | 24 | 62% | 34373 | 13544 | 1183 | 0.0009 | 45.0 | 2.5 | 0.00 |
| with-skill | 24 | 71% | 73239 | 17265 | 2048 | 0.0013 | 68.2 | 4.8 | 0.00 |
| **delta (with-without)** | - | +8% | +38866 | +3721 | +865 | +0.0004 | +23.1 | +2.3 | +0.00 |

## Per-case (mean per invocation)

| case | condition | n | accuracy | tokens_total | wall (s) | pdb_calls |
|---|---|---|---|---|---|---|
| 01_logic_offbyone | without-skill | 3 | 67% | 30416 | 42.8 | 0.00 |
| 01_logic_offbyone | with-skill | 3 | 33% | 21387 | 35.5 | 0.00 |
| 02_logic_conditional | without-skill | 3 | 100% | 47711 | 60.2 | 0.00 |
| 02_logic_conditional | with-skill | 3 | 67% | 110479 | 86.7 | 0.00 |
| 03_state_aliasing | without-skill | 3 | 33% | 23866 | 26.6 | 0.00 |
| 03_state_aliasing | with-skill | 3 | 67% | 55409 | 53.2 | 0.00 |
| 04_state_classvar | without-skill | 3 | 100% | 43506 | 56.9 | 0.00 |
| 04_state_classvar | with-skill | 3 | 100% | 45039 | 56.2 | 0.00 |
| 05_exc_keyerror | without-skill | 3 | 33% | 30740 | 29.9 | 0.00 |
| 05_exc_keyerror | with-skill | 3 | 100% | 68162 | 79.8 | 0.00 |
| 06_exc_typeerror | without-skill | 3 | 100% | 44306 | 62.3 | 0.00 |
| 06_exc_typeerror | with-skill | 3 | 100% | 52265 | 57.0 | 0.00 |
| 07_async_race | without-skill | 3 | 33% | 20395 | 31.3 | 0.00 |
| 07_async_race | with-skill | 3 | 33% | 25298 | 39.3 | 0.00 |
| 08_async_await_missing | without-skill | 3 | 33% | 34048 | 50.3 | 0.00 |
| 08_async_await_missing | with-skill | 3 | 67% | 207874 | 137.7 | 0.00 |
