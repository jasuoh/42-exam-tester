#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
stats.py  ·  local practice history, shared by both testers

Every grademe / --grade appends one line to ~/.examshell/stats.jsonl (JSON
Lines: one grading event per line, so a crash mid-write only ever corrupts
the last line, never the whole file). Purely local, purely additive — this
is a convenience for the student to see their own progress, never sent
anywhere, never read by grading itself.

Best-effort like settings.py: recording a stat must never be the reason a
grading run fails, so every write swallows OSError.
"""

import json
import os
import time

from .settings import DATA_DIR

STATS_PATH = os.path.join(DATA_DIR, "stats.jsonl")


def record(tool, exercise, level, ok, passed, total, mode):
    """Append one grading event. `tool` is "py" or "c"; `mode` is
    "exam" / "practice" / "train" / "grade" / "exam-complete"."""
    entry = {
        "ts": time.time(), "tool": tool, "exercise": exercise,
        "level": level, "ok": bool(ok), "passed": passed, "total": total,
        "mode": mode,
    }
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STATS_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
    except OSError:
        pass


def load_all(tool=None):
    """All recorded events, optionally filtered to one tool. Malformed
    lines (a torn write) are skipped rather than raising."""
    try:
        with open(STATS_PATH, encoding="utf-8") as fh:
            lines = fh.readlines()
    except OSError:
        return []
    events = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if tool is None or entry.get("tool") == tool:
            events.append(entry)
    return events


def consecutive_fails(tool, exercise):
    """How many times in a row (most recent first) `exercise` was graded
    and failed, ignoring --exam attempts — the exam is one-shot per
    exercise anyway, and this is used to decide when to nudge a stuck
    student in practice/training, never during the exam itself."""
    events = [e for e in load_all(tool)
             if e.get("exercise") == exercise and e.get("mode") != "exam"]
    events.sort(key=lambda e: e.get("ts", 0))
    streak = 0
    for e in reversed(events):
        if e.get("ok"):
            break
        streak += 1
    return streak


def weakest_exercises(tool, candidate_names):
    """`candidate_names` the student has failed at least once (in
    practice/training — --exam attempts are excluded, same reasoning as
    consecutive_fails), ranked worst-first: currently on a fail streak
    first, then lowest lifetime pass rate as a tiebreaker. Excludes both
    an exercise never attempted AND one with a spotless record — "weak"
    means "struggled with", not "haven't tried yet" (that's the plain
    exercise list) and not "nailed on the first try either" (that would
    just pad the queue with exercises there's nothing to gain from
    reviewing). Powers `--train weak` / the 'w' key in training_mode()."""
    events = [e for e in load_all(tool) if e.get("mode") != "exam"]
    per_exercise = {}
    for e in events:
        name = e.get("exercise")
        if name not in candidate_names:
            continue
        row = per_exercise.setdefault(name, {"attempts": 0, "passes": 0})
        row["attempts"] += 1
        if e.get("ok"):
            row["passes"] += 1
    weak = [name for name, row in per_exercise.items() if row["passes"] < row["attempts"]]

    def rank_key(name):
        row = per_exercise[name]
        streak = consecutive_fails(tool, name)
        pass_rate = row["passes"] / row["attempts"]
        return (-streak, pass_rate)

    return sorted(weak, key=rank_key)


def best_exam_time(tool):
    """Fastest recorded full-exam completion (seconds), or None."""
    times = [e["seconds"] for e in load_all(tool)
             if e.get("mode") == "exam-complete" and "seconds" in e]
    return min(times) if times else None


def record_exam_complete(tool, seconds, attempts, score):
    entry = {
        "ts": time.time(), "tool": tool, "mode": "exam-complete",
        "seconds": seconds, "attempts": attempts, "score": score,
    }
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(STATS_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, sort_keys=True) + "\n")
    except OSError:
        pass


def summarize(tool=None):
    """Aggregate stats for the `--stats` screen.

    Returns a dict: total attempts, overall pass rate, per-exercise
    (attempts, passes), and the best full-exam time if any.
    """
    events = [e for e in load_all(tool) if e.get("mode") != "exam-complete"]
    completions = [e for e in load_all(tool) if e.get("mode") == "exam-complete"]

    per_exercise = {}
    for e in events:
        name = e.get("exercise")
        if not name:
            continue
        row = per_exercise.setdefault(name, {"attempts": 0, "passes": 0})
        row["attempts"] += 1
        if e.get("ok"):
            row["passes"] += 1

    total_attempts = len(events)
    total_passes = sum(1 for e in events if e.get("ok"))
    best_seconds = min((c["seconds"] for c in completions), default=None)
    return {
        "total_attempts": total_attempts,
        "total_passes": total_passes,
        "pass_rate": (total_passes / total_attempts) if total_attempts else 0.0,
        "per_exercise": per_exercise,
        "exam_completions": len(completions),
        "best_seconds": best_seconds,
    }
