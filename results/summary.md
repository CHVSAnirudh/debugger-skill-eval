# debugger-skill-eval results

## Overall (mean per invocation)

| condition | n | accuracy | tokens_total | tokens_in | tokens_out | cost ($) | wall (s) | tool_calls | pdb_calls |
|---|---|---|---|---|---|---|---|---|---|
| without-skill | 24 | 100% | 53257 | 16742 | 774 | 0.0247 | 67.9 | 4.2 | 0.00 |
| with-skill | 24 | 100% | 97504 | 23377 | 1441 | 0.0396 | 73.6 | 7.9 | 3.04 |
| **delta (with-without)** | - | +0% | +44247 | +6635 | +667 | +0.0149 | +5.7 | +3.7 | +3.04 |

## Per-case (mean per invocation)

| case | condition | n | accuracy | tokens_total | wall (s) | pdb_calls |
|---|---|---|---|---|---|---|
| 01_logic_offbyone | without-skill | 3 | 100% | 47929 | 57.6 | 0.00 |
| 01_logic_offbyone | with-skill | 3 | 100% | 90257 | 54.7 | 3.67 |
| 02_logic_conditional | without-skill | 3 | 100% | 48650 | 72.0 | 0.00 |
| 02_logic_conditional | with-skill | 3 | 100% | 122197 | 62.0 | 5.00 |
| 03_state_aliasing | without-skill | 3 | 100% | 56483 | 67.0 | 0.00 |
| 03_state_aliasing | with-skill | 3 | 100% | 89016 | 58.3 | 2.00 |
| 04_state_classvar | without-skill | 3 | 100% | 51686 | 68.8 | 0.00 |
| 04_state_classvar | with-skill | 3 | 100% | 127530 | 152.3 | 5.33 |
| 05_exc_keyerror | without-skill | 3 | 100% | 64814 | 74.4 | 0.00 |
| 05_exc_keyerror | with-skill | 3 | 100% | 99529 | 61.4 | 2.00 |
| 06_exc_typeerror | without-skill | 3 | 100% | 53725 | 69.7 | 0.00 |
| 06_exc_typeerror | with-skill | 3 | 100% | 79963 | 60.7 | 1.67 |
| 07_async_race | without-skill | 3 | 100% | 51046 | 58.8 | 0.00 |
| 07_async_race | with-skill | 3 | 100% | 82267 | 61.3 | 3.00 |
| 08_async_await_missing | without-skill | 3 | 100% | 51720 | 74.8 | 0.00 |
| 08_async_await_missing | with-skill | 3 | 100% | 89273 | 77.9 | 1.67 |
