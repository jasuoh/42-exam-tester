"""Translated subjects (examshell/subject_lang.py): the lookup, and every
translation file checked against the bank's English subject."""

from __future__ import annotations

import os
import tempfile
import unittest
from typing import Dict, List
from unittest import mock

from c_exam import bank as c_bank
from c_exam import training_bank as c_training
from examshell import (
    exam_bank,
    exam_bank_r04,
    exam_bank_r05,
    subject_lang,
    training_bank,
    ui,
)
from examshell._types import Exercise

# every exercise of both testers, by its (unique) name
ALL: Dict[str, Exercise] = {}
for _bank in (
    exam_bank.EXERCISES,
    exam_bank_r04.EXERCISES,
    exam_bank_r05.EXERCISES,
    training_bank.TRAINING_EXERCISES,
    c_bank.EXERCISES,
    c_training.TRAINING_EXERCISES,
):
    ALL.update(_bank)

TRANSLATED = [lang for lang, _ in subject_lang.LANGUAGES if lang != "en"]


def _code_lines(text: str) -> List[str]:
    """The example lines a translation must keep as they are: the
    indented ones (calls, outputs, shell sessions)."""
    return [line for line in text.splitlines() if line.startswith("    ")]


class LookupTests(unittest.TestCase):
    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        os.makedirs(os.path.join(tmp.name, "fr"))
        with open(os.path.join(tmp.name, "fr", "py_inter.txt"), "w") as fh:
            fh.write("\nÉcrivez une fonction.\n\n")
        patcher = mock.patch.object(subject_lang, "SUBJECTS_DIR", tmp.name)
        patcher.start()
        self.addCleanup(patcher.stop)
        self.ex = ALL["py_inter"]

    def test_the_header_stays_english(self) -> None:
        subject = subject_lang.translated("py_inter", self.ex, "fr")[
            "subject"
        ]
        self.assertEqual(
            subject,
            subject_lang.header(self.ex["subject"])
            + "\n\nÉcrivez une fonction.\n",
        )

    def test_only_the_subject_changes(self) -> None:
        fr = subject_lang.translated("py_inter", self.ex, "fr")
        self.assertEqual(
            {k: v for k, v in fr.items() if k != "subject"},
            {k: v for k, v in self.ex.items() if k != "subject"},
        )
        self.assertIn("Écrivez", fr["subject"])
        self.assertNotIn("Écrivez", self.ex["subject"])

    def test_english_missing_or_unknown_falls_back(self) -> None:
        for lang in ("en", "es", "xx", ""):
            self.assertIs(
                subject_lang.translated("py_inter", self.ex, lang), self.ex
            )

    def test_examples_marker_in_every_language(self) -> None:
        for marker in ("Examples:", "Exemples :", "Ejemplos:", "Примеры:"):
            subject = "x\n%s\n    f(1) -> 2\n" % marker
            _, prose, _, examples = ui._split_subject(subject)
            self.assertEqual(examples, "    f(1) -> 2", marker)
            self.assertEqual(prose, "x", marker)


class TranslationFileTests(unittest.TestCase):
    """What the files in examshell/subjects/ must look like."""

    def test_every_file_belongs_to_an_exercise(self) -> None:
        for lang in os.listdir(subject_lang.SUBJECTS_DIR):
            self.assertIn(lang, TRANSLATED)
            folder = os.path.join(subject_lang.SUBJECTS_DIR, lang)
            for name in os.listdir(folder):
                self.assertTrue(name.endswith(".txt"), name)
                self.assertIn(name[: -len(".txt")], ALL, lang)

    def test_every_exercise_in_every_language(self) -> None:
        for lang in TRANSLATED:
            missing = sorted(
                name
                for name in ALL
                if not os.path.isfile(subject_lang.path(lang, name))
            )
            self.assertEqual(missing, [], lang)

    def test_translations_keep_signature_and_examples(self) -> None:
        for lang in TRANSLATED:
            for name, ex in sorted(ALL.items()):
                if not os.path.isfile(subject_lang.path(lang, name)):
                    continue  # reported by the completeness test
                with self.subTest(lang=lang, exercise=name):
                    self._check(lang, name, ex)

    def _check(self, lang: str, name: str, ex: Exercise) -> None:
        en = ui._split_subject(ex["subject"])
        tr_ex = subject_lang.translated(name, ex, lang)
        tr = ui._split_subject(tr_ex["subject"])
        self.assertEqual(tr[0], en[0], "header")
        self.assertEqual(tr[2], en[2], "signature")
        self.assertEqual(
            _code_lines(tr[3]), _code_lines(en[3]), "example lines"
        )
        self.assertTrue(tr[1].strip(), "no prose")
        body = subject_lang.body(tr_ex["subject"])
        english = subject_lang.body(ex["subject"])
        self.assertNotEqual(body, english)
        kept = set(english.splitlines())  # a few signatures are longer
        for line in body.splitlines():
            self.assertEqual(line, line.rstrip(), "trailing spaces")
            if line not in kept:
                self.assertLessEqual(len(line), 80, line)


if __name__ == "__main__":
    unittest.main()
