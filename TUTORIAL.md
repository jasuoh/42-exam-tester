# Tutorial: the quality-of-life features

This walks through the extras described in the README's
[Quality-of-life features](README.md#-quality-of-life-features-both-testers)
section, step by step. Everything here applies to **both** testers —
examples below use `python3 -m src` (or `make …`); swap in
`python3 -m c_exam` (or `make c-…`) for the C tester and it behaves
identically, since both share the same `src/settings.py`, `src/stats.py`,
`src/session_store.py` and `src/report_export.py`.

None of this is required. The exam and practice flow work exactly as they
always have if you never touch any of it.

## 1. Pick a theme, save it once

Three themes exist: `dark` (the original, default), `light` (for a
white/light terminal background), and `highcontrast` (colour-blind
friendly — swaps the usual red/green pass-fail colours for a blue/orange
palette that stays distinguishable under the common forms of colour-vision
deficiency).

Try one for a single run:

```bash
python3 -m src --theme light --list
```

If you like it, save it so every future run picks it up automatically,
without retyping `--theme` every time:

```bash
python3 -m src --theme light --save-config
```

This writes `~/.examshell/config.json`:

```json
{
  "theme": "light"
}
```

and exits immediately — no exam or practice session starts. Check it any
time:

```bash
cat ~/.examshell/config.json
```

An explicit `--theme` on the command line always overrides the saved one,
so `python3 -m src --theme dark --exam` still works for a single run even
after saving `light`.

`--save-config` also remembers `--timeout`, `--fuzz`, `--show-fails`, and
`--cc` (C tester only) the same way — useful if you always run with a
longer timeout on a slow machine, for example:

```bash
python3 -m src --timeout 8 --fuzz 20 --save-config
```

`--fuzz` itself means slightly different things per tester: the Python
tool has a hand-written fuzzer for every exercise, so `--fuzz N` always
adds N extra cases everywhere. The C tool generates fuzz values generically
from an exercise's argument types instead (no per-exercise oracle to
validate against ahead of time), so it only applies to exercises whose
arguments are all plain `int`/`char`/`str`/array values with no ordering
precondition — `make c-check`/`python3 -m c_exam --check` marks which
ones with `(+fuzz)`, and grading itself announces the real case count
either way (`"… (28 tests)"`).

## 2. Practice, then check `--stats`

Every `grademe` — in an exam, in practice, in training mode — and every
`--grade EXERCISE` quietly appends one line to `~/.examshell/stats.jsonl`.
Nothing to turn on; it just happens.

```bash
make stub EX=py_inter
$EDITOR rendu/py_inter.py
make grade EX=py_inter
```

Then:

```bash
make stats
# or: python3 -m src --stats
```

```
  Your practice history

  Total attempts : 4
     Pass rate : 75%
  Exams completed : 1
  Best exam time : 00:18:42

  Commands:
    py_inter  - 3/4 passed
```

Use this to spot which exercises actually need more reps, instead of
guessing from memory. It's purely local — nothing is uploaded anywhere.

## 3. Let an exam save itself when you `quit`

Start an exam, clear a level or two, then quit early:

```bash
make exam
...
  [alice@exam · lvl2]$ quit
```

Behind the scenes this writes `~/.examshell/saved_exam_py.json` — your
login, level, passed exercises, the exercise currently drawn, attempts,
and elapsed time. Start an exam again later and you'll be asked:

```
Resume saved exam for alice — level 2? [Y/n]:
```

Answer `y` (or just hit Enter) and you're back exactly where you left
off, including the *same* exercise for the level you were on — it isn't
redrawn. Answer `n` and the save is discarded, starting fresh.

The save is also cleared automatically the moment you finish an exam
(pass or fail all the way through), so a resume prompt never lingers
after a completed run.

## 4. Filter the exercise picker with `/text`

Open practice mode with no specific exercise:

```bash
make practice
```

```
  [1] py_bracket_validator          bracket_validator()
  [2] py_capitalizer                capitalizer()
  ...
  Selection (number, /text to filter, or 'b' to go back):
```

Type `/` followed by part of a name to narrow the list:

```
Selection (number, /text to filter, or 'b' to go back): /matrix
```

```
  [1] py_mirror_matrix               mirror_matrix()
  filter /matrix — 1/40 shown  ('/' alone clears it)
  Selection (number, /text to filter, or 'b' to go back):
```

The numbers you see always match what you type — filtering renumbers the
list, so `[1]` always means "the first thing currently on screen," never
a stale global index. Type `/` alone to clear the filter and see
everything again. Training mode's picker works the same way, alongside
its existing `e`/`m`/`h` difficulty filter.

## 5. Read your session report, collect a badge

After any exam run — passed or aborted — look at the last line printed:

```
  Session report saved to /home/alice/.examshell/reports/py_20260823_121116_alice.md
```

Open it; it's plain Markdown with your score, per-level attempts and
time, and any badges you earned:

```markdown
# Exam PASSED — alice

- Date: 2026-08-23 12:11:16
- Tester: Python (Rank 03)
- Score: 100/100
- Levels cleared: 6/6
- Total time: 00:22:10
- Total attempts: 7
- Achievements: 🏅 Flawless — no retries, 🎉 First full clear!

## Levels

| Level | Exercise | Attempts | Time |
|---|---|---|---|
| 1 | py_inter | 1 | 00:03:12 |
...
```

Badges are computed only against **your own** history in
`~/.examshell/stats.jsonl`: 🏅 *Flawless* means every level was cleared on
the very first `grademe`; 🎉 *First full clear!* means it's the first time
you've ever finished this tester's exam end to end; ⏱ *New personal best
time!* means this run beat every previous completion. They're for
motivation, not part of the score.

## Everything at once

```bash
python3 -m src --theme highcontrast --timeout 6 --save-config
make exam
# ... solve a couple of levels, then `quit` ...
make exam                 # offers to resume
make practice              # try /text filtering in the picker
make stats                 # see your history so far
```
