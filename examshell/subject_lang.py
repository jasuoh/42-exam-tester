#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
subject_lang.py  ·  the subject in another language, like the real exam

The real exam's subject folder has the text in several languages
(subject.en.txt, subject.fr.txt, ...). Here the banks hold the English
subject; examshell/subjects/<lang>/<exercise>.txt holds a translation of
everything below its header. The header (Assignment name, Expected
files, Allowed functions) stays English, as it does in the real exam, so
it is always taken from the bank.

Exercise names are unique across both testers, so one folder serves the
Python and the C banks. A missing or unreadable file shows the English
subject — a translation is a convenience, never a reason to break.
"""

from __future__ import annotations

import os
from typing import Tuple

from ._types import Exercise

# (code, name in its own language), in the order the app offers them
LANGUAGES: Tuple[Tuple[str, str], ...] = (
    ("en", "English"),
    ("fr", "Français"),
    ("es", "Español"),
    ("ru", "Русский"),
)
DEFAULT = "en"
SUBJECTS_DIR = os.path.join(os.path.dirname(__file__), "subjects")
HEADER_LINES = 4  # Assignment name, Expected files, Allowed functions, ---


def is_language(code: object) -> bool:
    return any(code == lang for lang, _ in LANGUAGES)


def path(lang: str, ex_name: str) -> str:
    return os.path.join(SUBJECTS_DIR, lang, ex_name + ".txt")


def header(subject: str) -> str:
    """The English header block, the dashed line included."""
    return "\n".join(subject.splitlines()[:HEADER_LINES])


def body(subject: str) -> str:
    """Everything below the header — what a translation file holds."""
    lines = subject.splitlines()[HEADER_LINES:]
    return "\n".join(lines).strip("\n")


def translated(ex_name: str, ex: Exercise, lang: str) -> Exercise:
    """`ex` with its subject in `lang`, or `ex` itself for English and
    wherever there's no translation. Only the subject changes; grading
    and stubs keep using the bank's own entry."""
    if lang == DEFAULT or not is_language(lang):
        return ex
    try:
        with open(path(lang, ex_name), encoding="utf-8") as fh:
            text = fh.read().strip("\n")
    except OSError:
        return ex
    if not text:
        return ex
    copy = dict(ex)
    copy["subject"] = header(ex["subject"]) + "\n\n" + text + "\n"
    return copy
