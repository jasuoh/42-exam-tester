#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
report_export.py  ·  Markdown exam session report, shared by both testers

Writes a small, human-readable summary of one exam run to
~/.examshell/reports/ — something a student can keep, diff between
attempts, or paste into a study log. Auto-generated at the end of every
exam run (passed or aborted); never required reading, purely a record.

Best-effort like the rest of this package: a write failure is a missed
convenience, never a reason to fail the exam.
"""

import os
import time

from .settings import DATA_DIR

REPORTS_DIR = os.path.join(DATA_DIR, "reports")


def write_exam_report(tool, session, n_levels, passed, achievements=()):
    """Write the report, return its path on success or None on failure."""
    stamp = time.strftime("%Y%m%d_%H%M%S")
    path = os.path.join(REPORTS_DIR, "%s_%s_%s.md" % (tool, stamp, session.login))

    lines = []
    title = "Exam PASSED" if passed else "Exam aborted"
    lines.append("# %s — %s" % (title, session.login))
    lines.append("")
    lines.append("- Date: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    lines.append("- Tester: %s" % ("Python (Rank 03)" if tool == "py" else "C (Rank 02)"))
    lines.append("- Score: %d/100" % session.score())
    lines.append("- Levels cleared: %d/%d" % (len(session.passed), n_levels))
    lines.append("- Total time: %s" % session.elapsed())
    lines.append("- Total attempts: %d" % session.attempts)
    if achievements:
        lines.append("- Achievements: " + ", ".join(achievements))
    lines.append("")
    lines.append("## Levels")
    lines.append("")
    lines.append("| Level | Exercise | Attempts | Time |")
    lines.append("|---|---|---|---|")
    for level, name, attempts, seconds in session.history:
        secs = int(seconds)
        lines.append("| %d | %s | %d | %02d:%02d:%02d |"
                     % (level, name, attempts,
                        secs // 3600, (secs % 3600) // 60, secs % 60))
    lines.append("")

    try:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(lines))
        return path
    except OSError:
        return None
