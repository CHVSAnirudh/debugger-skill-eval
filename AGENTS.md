# Python Debugger Workflow

When fixing a Python bug in this project, you **must** use `pdb` (the Python debugger) to localize the root cause before editing code. Do not rely on adding `print` statements or guessing from the source — use the debugger.

## Non-interactive pdb (you cannot interact with stdin)

You run commands via a shell, so use pdb's `-cc` flag to pass debugger commands as arguments. Each `-cc` is one pdb command, executed in order before the program runs.

### Pre-mortem (logic, state, mutation bugs)

Set breakpoints and inspect state at suspect lines:

```
python -m pdb -cc 'b <line_number>' -cc 'c' -cc 'pp locals()' -cc 'p <variable>' -cc 'c' <script.py>
```

Useful pdb commands inside `-cc`:
- `b <file>:<line>` or `b <line>` — set breakpoint
- `c` — continue until next breakpoint
- `n` — next line (step over)
- `s` — step into call
- `p <expr>` — print expression
- `pp <expr>` — pretty-print
- `w` — print current stack (where)
- `l` — list source around current line
- `a` — print arguments of current function
- `q` — quit

### Post-mortem (when the program crashes)

After a script raises an unhandled exception, enter post-mortem on the failed frame:

```
python -m pdb -c continue -c 'pp locals()' -c 'w' -c 'l' <script.py>
```

`-c continue` runs until the exception; pdb then drops you at the failing frame. The follow-up `-c` commands inspect that frame.

## Required workflow for any Python bug

1. **Reproduce** — run the script with the given inputs, capture actual vs. expected.
2. **Inspect with pdb** — use the appropriate pattern above. Look at the actual values of variables, not what you think they are.
3. **Form a hypothesis** only after pdb output confirms a specific root cause.
4. **Apply the minimal fix.**
5. **Verify** by re-running pdb or the script.

Skipping the pdb step is not acceptable for this project, even for bugs that look obvious from reading the source.
