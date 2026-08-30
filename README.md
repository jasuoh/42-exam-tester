<div align="center">

# ⌨️ ExamShell
### Practice testers for 42 Common Core exams — Python Rank 03 & C Rank 02

*Real sandboxed grading, real edge cases, zero internet required.*

</div>

A practice tester built in the style of the real `examshell` / moulinette for
the **42 Common Core Python Exam Rank 03** — and, further down, a second,
independent one for **Exam Rank 02 (C)**.

Six levels in order, one random exercise per level out of a pool of 40, each
graded against dozens of tests, and you only move up at **100 %** — same
rules as the real thing.

```bash
make install     # optional: venv + rich for the pretty UI
make run         # interactive menu
```

No dependencies are required. Without `rich` the tester falls back to plain
ANSI output, so it runs on any exam machine with nothing but Python 3.8+.

**At a glance**

| | Python · Exam Rank 03 | C · Exam Rank 02 |
|---|---|---|
| Levels / exercises | 6 levels · 44 exercises | 4 levels · 59 exercises |
| Extra practice | 🧠 Training pool (20, by difficulty) | 🧠 Training pool (9, by difficulty) |
| Grading | in-process sandbox, `deep_eq` | compile + run + diff stdout |
| Solutions live in | `rendu/` | `c_rendu/` |
| Entry point | `make run` · `python3 -m src` | `make c-run` · `python3 -m c_exam` |

**Jump to:** [Quick start](#quick-start) · [How the exam works](#how-the-exam-works)
· [Exercise pool](#exercise-pool) · [Training pool](#training-pool-leetcode-style)
· [How grading works](#how-grading-works) ·
[Quality-of-life features](#quality-of-life-features-both-testers) ·
[Make targets](#make-targets) ·
[CLI](#cli) · [Testing](#testing-this-project) · [Layout](#layout) ·
**[→ jump to the C tester](#c-exam-rank-02-tester)**

---

## 🚀 Quick start

```bash
make exam                    # jump straight into the 6-level exam
make stub EX=py_inter        # create rendu/py_inter.py with the signature
$EDITOR rendu/py_inter.py    # solve it
make grade EX=py_inter       # grade it (exit code 0 = OK, 1 = KO)
make grade-all               # grade everything you've written so far
```

Inside the exam you type `grademe`, exactly like the real one.

## 🎯 How the exam works

1. **Six levels**, in order 1 → 6.
2. One **random exercise per level**, drawn from that level's pool (levels 1
   and 2 have eight to draw from, levels 3–6 have six).
3. Write your solution in `rendu/<exercise_name>.py` and define the required
   function. `rendu/` is created for you.
4. Type `grademe`. **You only advance at 100 %.**

Commands during the exam:

| Command | |
|---|---|
| `grademe` | test your solution |
| `subject` | show the assignment again |
| `status` | show your progress |
| `new` | draw a different exercise for this level |
| `stub` | create the solution file for you |
| `quit` | abort (you still get a summary) |

Modes from the main menu: **Start exam** (the full run above — draws only
from the Standard 14, one per level), **Practice mode** (drill *any* of
the 40, Standard or Extra, no progression), **List all exercises**,
**Training mode** (LeetCode-style exercises by difficulty — see below,
never part of the exam).

Every generated stub (`stub` / `make stub`) also embeds a small
**self-check block**: a handful of the exercise's own curated cases with
their expected output, computed from the reference solution, so
`python3 rendu/<exercise>.py` gives instant `ok` / `FAIL` feedback while
you're still writing the function — no need to go through the full sandboxed
`grademe` for a quick sanity check. It's inert during real grading (the
block only runs when the file is executed directly, never when it's
imported), and it only covers a few examples — `grademe` still checks dozens
of edge cases and fuzz inputs these don't.

## 📚 Exercise pool

44 exercises, but they are not all the same kind of exercise, and —
important — **`make exam` only ever draws from the Standard 14**:

* **Standard (14)** — the original pool, based on the publicly documented
  Rank-03 exercises. These are the ones that can plausibly show up on the
  *real* 42 exam, and the only ones a real `make exam` run can draw.
  Marked in **bold** below and with ★ in `--list`.
* **Extra (30)** — added for broader practice: more variety, a wider
  difficulty range, a couple of deliberately easy warm-ups in levels 1–2.
  Good drilling, but not verified against any real exam sheet, and
  **never drawn into a real exam run** — reach them through **Practice
  mode** instead (marked with ○ in `--list`).

| Level | Standard (drawn by `make exam`) | Extra (practice mode only) |
|------:|----------|-------|
| 1 | **`py_cryptic_sorter`** · **`py_inter`** · **`py_bracket_validator`** | `py_vowel_counter` · `py_capitalizer` · `py_leet_speak` · `py_char_frequency` · `py_string_reverser` · `py_char_counter` |
| 2 | **`py_echo_validator`** · **`py_mirror_matrix`** | `py_digit_extractor` · `py_case_counter` · `py_run_length_encoder` · `py_second_largest` · `py_even_odd_counter` · `py_sum_of_squares` · `py_longest_common_prefix` · `py_camel_to_snake_converter` |
| 3 | **`py_number_base_converter`** · **`py_pattern_tracker`** · **`py_hidenp`** | `py_word_reverser` · `py_run_length_decoder` · `py_binary_gap` · `py_string_rotation_checker` |
| 4 | **`py_anagram`** · **`py_shadow_merge`** · **`py_string_permutation_checker`** | `py_unique_elements` · `py_pangram_checker` · `py_max_subarray_sum` · `py_roman_numeral` |
| 5 | **`py_string_sculptor`** · **`py_twist_sequence`** | `py_matrix_transposer` · `py_longest_word` · `py_zigzag_flatten` · `py_pascals_triangle_row` |
| 6 | **`py_whisper_cipher`** | `py_matrix_rotator` · `py_prime_finder` · `py_longest_palindromic_substring` · `py_two_sum_indices` |

Within the extra pool, `py_string_reverser` and `py_char_counter` (level 1),
plus `py_even_odd_counter` and `py_sum_of_squares` (level 2), are the
deliberately easy ones — a good place to start if you're new to the exam
format.

`python3 -m src --list` prints this pool with the exact function name for
each exercise, ★/○ marking which pool each belongs to; the full signature
and subject show up once you draw or practice it.

## 🧠 Training pool (LeetCode-style)

A second, completely separate pool of exercises for open-ended practice —
grouped by **difficulty** instead of exam level, and **never** drawn into
`make exam` or shown in `--list`. Reach it through the main menu's
**Training mode**, `make train`, or `python3 -m src --train`.

| Difficulty | Exercises |
|---|---|
| Easy   | `py_fizzbuzz_list` · `py_first_unique_char` · `py_missing_number` · `py_contains_duplicate` · `py_single_number` · `py_climbing_stairs` |
| Medium | `py_group_anagrams` · `py_product_except_self` · `py_kth_largest` · `py_three_sum` · `py_spiral_matrix` · `py_container_with_most_water` · `py_string_compression` |
| Hard   | `py_merge_intervals` · `py_longest_increasing_subsequence` · `py_trapping_rain_water` · `py_coin_change` · `py_edit_distance` · `py_largest_rectangle_histogram` · `py_longest_common_subsequence` |

These are graded through the exact same sandbox as the exam pool (same
edge-case + fuzz testing, mutation/print detection, import checks), just
picked and listed differently. `python3 -m src --list-training` prints the
pool; `python3 -m src --train easy` opens the picker filtered to the easy
exercises, `--train py_kth_largest` drills that one exercise directly.

## 🧪 How grading works

Most exercises run against **~30–60 tests**: every curated edge case in the
bank (empty inputs, case handling, boundaries, punctuation, negative
numbers, ties…) plus randomised fuzz tests — fewer for the handful of
exercises with a naturally small input domain (e.g. a Pascal's-triangle row
index only takes so many interesting values). Expected values come from a
reference implementation, never from a hand-written answer key, so they
cannot drift out of sync with the subject.

Your file is **never imported into the tester**. It runs in a subprocess that:

* has a clean `sys.path` — it cannot import the bank and read the answers,
* gets `/dev/null` on stdin, so a stray `input()` fails instead of hanging,
* arms an alarm around **every single call**, so an infinite loop costs you
  three seconds and not your session,
* gives up early after repeated timeouts instead of grinding through 40
  cases at the full timeout each,
* reports through a result file, so anything your code prints cannot
  corrupt the verdict.

Comparison is **type-strict and recursive**: `True` is not `1`, and a tuple
is not a list — the same pickiness the moulinette has.

Beyond pass/fail, the grader tells you when:

* your function **printed** the answer instead of returning it (the single
  most common way to fail an exam you had actually solved),
* your function **mutated its input** when the subject asked for a new
  value,
* your **signature is wrong** — one clear message instead of forty
  identical `TypeError`s,
* you used an **import**, which the real exam forbids (a warning by
  default, a failure with `--strict-imports`).

## 🎛️ Quality-of-life features (both testers)

Everything below lives in `src/settings.py`, `src/stats.py`,
`src/session_store.py` and `src/report_export.py` — one small shared layer
used by **both** `python3 -m src` and `python3 -m c_exam`, so it works the
same way and stores its files in the same place (`~/.examshell/`) no matter
which tester you're using. None of it is required reading: the exam and
practice flow work exactly as before if you never touch any of this.

Everything here is **best-effort**: if `~/.examshell/` can't be created or
written to (a locked-down exam machine, a read-only `$HOME`), these features
just silently do nothing — they never make grading fail.

### 🎨 Themes

Three colour themes, picked with `--theme`:

| Theme | For |
|---|---|
| `dark` (default) | the original palette — bright colours, dark terminal background |
| `light` | a white/light terminal background (darker, more saturated colours so nothing washes out) |
| `highcontrast` | colour-blind friendly — swaps the usual red/green pass-fail colours for the [Okabe–Ito](https://jfly.uni-koeln.de/color/) blue/vermillion/orange palette, which stays distinguishable under the common forms of colour-vision deficiency |

```bash
python3 -m src --theme highcontrast     # try it for one run
python3 -m src --theme light --save-config   # remember it for every future run
```

`--save-config` writes `--theme` (and `--timeout`/`--fuzz`/`--show-fails`,
`--cc` for the C tester) to `~/.examshell/config.json` and exits — no exam
or practice session starts. From then on, any run that doesn't pass the
flag explicitly picks up the saved value; an explicit flag on the command
line always wins over the saved one.

### 📊 Local stats

Every `grademe` (in an exam or in practice) and every `--grade` appends one
line to `~/.examshell/stats.jsonl` — purely local, never sent anywhere.

```bash
python3 -m src --stats      # or: make stats
python3 -m c_exam --stats   # or: make c-stats
```

Shows your overall attempts and pass rate, your best full-exam completion
time, and a per-exercise breakdown (`3/7 passed`, …) — a quick way to see
which exercises you actually need more reps on.

### 📄 Session reports

Every exam run — passed or aborted — writes a small Markdown summary to
`~/.examshell/reports/` (login, score, time, per-level attempts/time, any
badges earned) and prints the path at the end. Nothing to configure; it's
just a record you can keep, diff between attempts, or paste into a study
log.

### ⏸️ Resuming an aborted exam

`quit` during an exam now saves your progress (level, passed exercises,
the exercise currently drawn, attempts, elapsed time) to
`~/.examshell/saved_exam_py.json` (`saved_exam_c.json` for the C tester).
The next time you start an exam, you're asked whether to resume:

```
Resume saved exam for alice — level 3? [Y/n]:
```

Say no (or let the exam finish normally) and the save is discarded. This
is a convenience for closed laptops and accidental `quit`s, not a way to
game the real exam's rules — the real moulinette has no resume button
either.

### 🔎 Fuzzy search in the exercise picker

Practice mode's and Training mode's exercise pickers accept `/text` as a
quick filter — type `/` followed by part of an exercise or function name
to narrow the list, `/` alone to clear it:

```
Selection (number, /text to filter, or 'b' to go back): /matrix
```

### 🏅 Achievements

Shown at the end of a **passed** exam, in the summary panel and in the
saved report: 🏅 *Flawless* (every level cleared on the first `grademe`),
🎉 *First full clear!* (your first ever 100% run for that tester), and ⏱
*New personal best time!* (faster than any previous completion) — bragging
rights only, they don't affect scoring.

**→ [TUTORIAL.md](TUTORIAL.md)** walks through all six of the above
step by step, with real command output.

## 🛠️ Make targets

| Target | What it does |
|---|---|
| `make` | show the help |
| `make run` | interactive menu (exam · practice · list) |
| `make exam` | start the exam directly |
| `make practice` | drill exercises — `make practice EX=py_inter` for one |
| `make list` | print the exercise pool |
| `make train` | Training mode — `make train EX=easy` or `EX=py_kth_largest` |
| `make list-training` | print the training pool (by difficulty) |
| `make stub EX=…` | create an empty solution file (never overwrites) |
| `make grade EX=…` | grade one solution, no menu |
| `make grade-all` | grade every **exam** solution in `rendu/` at once, one overview (training solutions: `make grade EX=…`) |
| `make stats` | your local practice history — attempts, pass rate, best exam time |
| `make unit` | fast unit tests for the tool's own logic |
| `make check` | self-test both exercise banks' content |
| `make test` | `unit` + `check` |
| `make lint` | parse-check the sources, plus ruff/pyflakes if installed |
| `make status` | show which solutions you have written so far |
| `make install` | create `venv/` and install `rich` |
| `make clean` | remove caches and stray artefacts |
| `make fclean` | `clean` + remove `venv/` |
| `make re` | `fclean` + `install` + `check` |
| `make rendu-clean` | delete your solutions (asks for confirmation first) |

Options: `EX=<exercise>`, `SEED=<n>`, `RENDU=<dir>`,
`FLAGS='--strict-imports'`, `PYTHON=python3.11`.

```bash
make exam SEED=42                 # reproducible exam, same draw every time
make exam FLAGS=--strict-imports  # any import fails grading, like the moulinette
```

## ⌨️ CLI

The Makefile is a thin wrapper; everything is reachable directly:

```
python3 -m src                       # interactive menu
python3 -m src --exam --seed 42      # reproducible exam
python3 -m src --practice py_inter   # drill one exam exercise
python3 -m src --train               # training mode (LeetCode-style, by difficulty)
python3 -m src --train easy          # …filtered to easy exercises
python3 -m src --train py_kth_largest  # …drill one training exercise directly
python3 -m src --grade inter         # grade once (unique suffixes work)
python3 -m src --grade-all           # grade every exam solution in rendu/
python3 -m src --check               # validate both exercise banks
python3 -m src --stats               # your local practice history
python3 -m src --theme light --save-config   # remember a theme for next time
python3 -m src --list
python3 -m src --list-training
python3 -m src --help
```

Run it from the repository root — `src/` is a package, not a standalone
script, so `python3 src/examshell.py` will not work.

Useful flags: `--rendu DIR`, `--timeout SEC`, `--fuzz N`, `--show-fails N`,
`--strict-imports`, `--theme {dark,light,highcontrast}`, `--save-config`,
`--no-color`, `--no-rich`. See
[Quality-of-life features](#quality-of-life-features-both-testers) above
for what `--theme`, `--save-config` and `--stats` actually do.

## ✅ Testing this project

Two independent safety nets, run separately because they check different
things:

* **`make check`** validates both exercise *banks* (`exam_bank.py` and
  `training_bank.py`): every reference solution is run back through the
  real sandbox and must score 100 %, every subject must match its function,
  every fuzzer must work, no level/difficulty group may be empty. Run it
  after touching either bank file.
* **`make unit`** validates the *tool's own code* (stdlib `unittest`, no
  extra dependency): comparison logic (`deep_eq`), import detection,
  exercise resolution, `--grade-all`'s bookkeeping, subject parsing, and so
  on. Run it after touching `grader.py`, `ui.py` or `examshell.py`.
  `deep_eq` is defined once in `grader.py` — the exact same source is
  spliced into the sandboxed runner, so unit-testing it here also covers
  what actually grades your code.

`make test` runs both.

## 🗂️ Layout

| File | |
|---|---|
| `src/__main__.py` | entry point for `python3 -m src` |
| `src/examshell.py` | CLI, menu, exam and practice flow |
| `src/grader.py` | test building, the sandbox, the self-test |
| `src/ui.py` | all rendering — `rich` when available, ANSI otherwise |
| `src/bank_common.py` | tiny helpers shared by both exercise banks |
| `src/exam_bank.py` | the 6-level exam bank ⚠ **contains the answers** |
| `src/training_bank.py` | the LeetCode-style training bank ⚠ **contains the answers** |
| `src/settings.py` | `~/.examshell/config.json` — theme/timeout/fuzz/show-fails, shared by both testers |
| `src/stats.py` | `~/.examshell/stats.jsonl` — local grading history, shared by both testers |
| `src/session_store.py` | exam save/resume state, shared by both testers |
| `src/report_export.py` | Markdown session reports in `~/.examshell/reports/`, shared by both testers |
| `tests/` | unit tests for the tool itself |
| `rendu/` | your solutions (git-ignored) |

---

> The exact exercise set depends on your campus and changes over time. The
> **standard** pool above is based on the publicly documented Rank-03 Python
> exercises; the **extra** pool is this project's own addition for more
> practice. Don't rote-learn the solutions — understand the logic.

---

# 🔧 C Exam Rank 02 tester

A second, independent practice tester in the same repo, for the **42
Common Core C Exam Rank 02** — same shape (levels, `grademe`, a stub with a
quick self-check), completely different grading mechanism underneath: your
file is **compiled**, not imported.

```bash
make c-run           # interactive menu
make c-exam          # jump straight into the exam
```

Solutions live in `c_rendu/` (separate from the Python tool's `rendu/`).
Uses your system's `cc` by default — no extra dependency, works on any
machine with a C compiler.

**Jump to:** [How it works](#how-it-works) · [Exercise pool](#exercise-pool-1)
· [Fuzzing](#-fuzzing-partial) · [Training pool](#-training-pool-leetcode-style-1)
· [Make targets](#make-targets-1) · [CLI](#cli-1) · [Layout](#layout-1) ·
**[↑ back to the Python tool](#quick-start)**

## 🔍 How it works

Real Exam Rank 02 subjects come in two shapes, and this bank has both —
each graded differently:

* **"Write a function"** (e.g. `ft_atoi`, `ft_split`, `sort_list`) — the
  bank supplies a reference implementation (`oracle_c`) and a small type
  description (`args`/`returns`/curated `cases`). From that, the tester
  **generates a `main()`** that calls the function under test once per
  case, each call's output isolated by a marker. That generated `main()`
  is compiled once against the reference implementation and once against
  your file, both binaries run, and their output is compared call-by-call
  — the same "exactness" philosophy as the Python tool's type-strict
  comparison, just at the level of raw stdout bytes. Your submission
  **must not define `main()`** here — the tester supplies its own, and a
  leftover `main()` in your file collides with it at link time (reported
  clearly, not as a cryptic linker error).
* **"Write a program"** (e.g. `rotone`, `fizzbuzz`, `hidenp`, `pgcd`) —
  these real subjects hand you argc/argv and expect a full program, so
  there's no harness: your file **must** define `main()`. It's compiled
  standalone, then run once per case with that case's argv, and its
  stdout is compared directly against `oracle_c` (also a full program)
  run the same way.

A few exercises pass or return a singly-linked list (`t_list`, one int
`data` field and a `next` pointer) — for those, both your file and the
grader's harness `#include "list.h"`, and `make c-stub`/`make c-grade`
write that header into `c_rendu/` for you the same way the real exam
hands you one.

Beyond pass/fail, `grademe` tells you when:

* your program **crashed** (segfault, abort, …) — very common in C, and
  much more informative than "0/N passed" on its own,
* your program **timed out** (infinite loop) — per test case in "program"
  mode, per whole run in "function" mode,
* a **compiler warning** was raised (`-Wall -Wextra` always run; add
  `--strict-norm` to turn warnings into hard failures with `-Werror`,
  mirroring the Python tool's `--strict-imports`),
* you used a **forbidden libc call** for that exercise (e.g. `atoi` itself
  for `ft_atoi`) — a warning, not a hard failure, matching the Python
  tool's default posture on imports.

`--cc` isn't just a convenience flag: every oracle in both C banks is
also verified against a second compiler (GCC, alongside the default
`cc`/Clang) before being trusted, since the two don't always agree — GCC's
C23 default reads an empty-parens function pointer declaration `int
(*cmp)()` as "takes no parameters" where every older C standard (and
Clang's current default) reads it as "unspecified parameters", so a
prototype that compiles under one can fail to compile under the other.
`make c-check` scans every prototype for that specific pattern regardless
of which `cc` you run it with.

Every generated **"function"**-kind stub also ships a `#ifdef
SELF_TEST`-guarded `main()` with a couple of worked examples, so you can
try your implementation immediately:

```bash
cc -DSELF_TEST c_rendu/ft_atoi.c -o /tmp/t && /tmp/t
```

That guard is what keeps it safe: normal grading never defines `SELF_TEST`,
so the real compile never sees two `main()`s. Unlike the Python tool's
embedded self-check, this one doesn't auto-compare against expected
values — eyeball it against the subject's Examples, or just run `grademe`
for the real, automatic check. **"Program"**-kind stubs don't need that
guard at all — you already have your own `main()`, so just compile and run
the file directly: `cc c_rendu/rotone.c -o /tmp/t && /tmp/t abc`.

## 📚 Exercise pool

**59 exercises, across 4 levels**, split the same way as the Python
bank — Standard vs Extra:

* **Standard (56)** — the complete pool of a real Exam Rank 02 practice
  repository, its own per-level folder structure used directly (not
  blended across sources with different level splits). Names, prototypes,
  behaviour and level placement are all real. Exact level placement still
  varies by campus and changes over time, same caveat as the Python side.
  Marked in **bold** below and with ★ in `--list`; the only pool a real
  `make c-exam` run can draw from.
* **Extra (3)** — this project's own invented additions for more
  text-manipulation practice, one per level 1–3, not verified against any
  real exam sheet, **never drawn into a real exam run** — reach them
  through **Practice mode** instead (marked with ○ in `--list`).

| Level | Standard (drawn by `make c-exam`) | Extra (practice mode only) |
|------:|----------|-------|
| 1 (12) | **`first_word`** 🖥️ · **`fizzbuzz`** 🖥️ · **`ft_putstr`** · **`ft_strcpy`** · **`ft_strlen`** · **`ft_swap`** · **`repeat_alpha`** 🖥️ · **`rev_print`** 🖥️ · **`rot_13`** 🖥️ · **`rotone`** 🖥️ · **`search_and_replace`** 🖥️ · **`ulstr`** 🖥️ | `count_vowels` 🖥️ |
| 2 (19) | **`alpha_mirror`** 🖥️ · **`camel_to_snake`** 🖥️ · **`do_op`** 🖥️ · **`ft_atoi`** · **`ft_strcmp`** · **`ft_strcspn`** · **`ft_strdup`** · **`ft_strpbrk`** · **`ft_strrev`** · **`ft_strspn`** · **`is_power_of_2`** · **`last_word`** 🖥️ · **`max`** · **`print_bits`** · **`reverse_bits`** · **`snake_to_camel`** 🖥️ · **`swap_bits`** · **`union`** 🖥️ · **`wdmatch`** 🖥️ | `is_palindrome_str` 🖥️ |
| 3 (15) | **`add_prime_sum`** 🖥️ · **`epur_str`** 🖥️ · **`expand_str`** 🖥️ · **`ft_atoi_base`** · **`ft_list_size`** 🔗 · **`ft_range`** · **`ft_rrange`** · **`hidenp`** 🖥️ · **`lcm`** · **`paramsum`** 🖥️ · **`pgcd`** 🖥️ · **`print_hex`** 🖥️ · **`rstr_capitalizer`** 🖥️ · **`str_capitalizer`** 🖥️ · **`tab_mult`** 🖥️ | `longest_word_str` 🖥️ |
| 4 (10) | **`flood_fill`** 🧩 · **`fprime`** 🖥️ · **`ft_itoa`** · **`ft_list_foreach`** 🔗 · **`ft_list_remove_if`** 🔗 · **`ft_split`** · **`rev_wstr`** 🖥️ · **`rostring`** 🖥️ · **`sort_int_tab`** · **`sort_list`** 🔗 | — |

🖥️ = "program" kind (your own `main()`, argv-driven) · 🔗 = uses a shared
linked-list header (`list.h` for the simple `int`-data `t_list` used by
`sort_list`/`ft_list_size`, `ft_list.h` for the `void *data` generic one
used by `ft_list_foreach`/`ft_list_remove_if` — two different real headers
for two different real subjects, same as the actual exam) · 🧩 =
`flood_fill.h` (`t_point` + a 2D char grid).

The three Extra exercises mirror text exercises the Python side already
has (`py_vowel_counter`, `py_echo_validator`, `py_longest_word`) so you
can practice the same logic in both languages.

`ft_list_foreach`/`ft_list_remove_if` are graded against a fixed test
callback the harness supplies (an accumulator, and an int-equality
comparator respectively) rather than a callback of the student's own
choosing — that's what lets a generic harness test a function-pointer
argument at all, at the cost of not exercising arbitrary callback logic.

### 🎲 Fuzzing (partial)

`--fuzz N` (default 8, like the Python tool's) adds N random extra cases
to every **"function"-kind exercise whose args are all "safe" to
randomise** — plain `int`/`char`/`str`/`int_arr`/`int_list`/`buf`
arguments with no exercise-specific precondition. Unlike the Python
tool, there is no per-exercise custom fuzzer: C has no oracle-only
in-process check, so a fuzzed value can only be validated by actually
compiling and running it, and a value the oracle doesn't expect could
trigger undefined behaviour identically on both sides (a false failure
that's nobody's fault). So exercises using a linked list, `t_point`,
a char grid, or a fixed callback keep their curated cases only —
`make c-check` marks which exercises got fuzzed with `(+fuzz)`.
**"Program"-kind exercises are never fuzzed** — their argv shapes vary
too much (a bare string vs. multiple flags vs. numeric parsing) to
randomise generically without mostly generating meaningless input.

```bash
python3 -m c_exam --grade ft_atoi --fuzz 20
python3 -m c_exam --check --fuzz 20       # also fuzzes the self-test
```

## 🧠 Training pool (LeetCode-style)

A second, independent bank for open-ended practice — the C counterpart to
the Python tool's own training pool above, same shape: grouped by
**difficulty** instead of exam level, never drawn into `make c-exam` or
shown in `--list`. Reach it through the main menu's **Training mode**,
`make c-train`, or `python3 -m c_exam --train`.

| Difficulty | Exercises |
|---|---|
| Easy   | `array_sum` · `find_max` · `is_palindrome_num` |
| Medium | `count_pairs_sum` · `kadane_max_sum` · `count_unique` |
| Hard   | `lis_length` · `count_inversions` · `max_gap` |

Deliberately smaller than the Python tool's 20 — every exercise here uses
only plain `int`/`int *` arguments and an `int` return with no precondition
on how the array is ordered, so `--fuzz` (see above) already covers all
nine automatically; `make c-check`/`python3 -m c_exam --check` validates
this bank the same real-compiler way as the exam pool.
`python3 -m c_exam --list-training` prints the pool; `python3 -m c_exam
--train easy` opens the picker filtered to the easy exercises, `--train
array_sum` drills that one exercise directly.

## 🛠️ Make targets

| Target | What it does |
|---|---|
| `make c-run` | interactive menu (exam · practice · list · training) |
| `make c-exam` | start the exam directly |
| `make c-practice` | drill exercises — `make c-practice EX=ft_atoi` for one |
| `make c-list` | print the exercise pool |
| `make c-train` | Training mode — `make c-train EX=easy` or `EX=array_sum` |
| `make c-list-training` | print the training pool (by difficulty) |
| `make c-stub EX=…` | create a solution stub (never overwrites) |
| `make c-grade EX=…` | grade one solution, no menu |
| `make c-grade-all` | grade every solution in `c_rendu/` at once, one overview |
| `make c-stats` | your local practice history — attempts, pass rate, best exam time |
| `make c-unit` | fast unit tests for the C tester's own logic |
| `make c-check` | self-test both C exercise banks (every oracle, through the real sandbox) |
| `make c-test` | `c-unit` + `c-check` |

Options: `EX=<exercise>`, `SEED=<n>`, `RENDU=<dir>` (that's `c_rendu` by
default here), `CC=<compiler>` (default `cc`).

## ⌨️ CLI

```
python3 -m c_exam                       # interactive menu
python3 -m c_exam --exam --seed 42      # reproducible exam
python3 -m c_exam --practice ft_atoi    # drill one exercise
python3 -m c_exam --train               # training mode (LeetCode-style, by difficulty)
python3 -m c_exam --train easy          # …filtered to easy exercises
python3 -m c_exam --grade atoi          # grade once (unique suffixes work)
python3 -m c_exam --grade-all           # grade every solution in c_rendu/
python3 -m c_exam --check               # validate both banks
python3 -m c_exam --stats               # your local practice history
python3 -m c_exam --list
python3 -m c_exam --list-training
python3 -m c_exam --help
```

Useful flags: `--rendu DIR`, `--cc COMPILER`, `--timeout SEC`, `--strict-norm`,
`--fuzz N`, `--show-fails N`, `--theme {dark,light,highcontrast}`,
`--save-config`, `--no-color`, `--no-rich`. Same shared theme/config/stats/
resume/report layer as the Python tester — see
[Quality-of-life features](#quality-of-life-features-both-testers) up top,
and [Fuzzing (partial)](#-fuzzing-partial) above for what `--fuzz` covers here.

## 🗂️ Layout

| File | |
|---|---|
| `c_exam/__main__.py` | entry point for `python3 -m c_exam` |
| `c_exam/examshell.py` | CLI, menu, exam and practice flow |
| `c_exam/grader.py` | harness codegen, the compile/run/diff sandbox, fuzzing, the self-test |
| `c_exam/bank.py` | the exam exercise bank ⚠ **contains the answers** |
| `c_exam/training_bank.py` | the LeetCode-style training bank ⚠ **contains the answers** |
| `c_rendu/` | your solutions (git-ignored) |

Rendering is **shared** with the Python tool — `c_exam/examshell.py` uses
`src/ui.py` directly, unchanged in behavior, including `exercise_table`/
`training_table`. `src/grader.py`'s `Report` is reused too; only the
grading mechanism itself (`c_exam/grader.py`) is new. Themes, saved
config, local stats, exam save/resume and session reports
(`src/settings.py`, `src/stats.py`, `src/session_store.py`,
`src/report_export.py`) are shared the same way — see
[Quality-of-life features](#quality-of-life-features-both-testers).
