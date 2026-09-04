#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for src/ui.py — the parsing/escaping helpers that do not need
an actual terminal. Rendering itself is checked by hand (see the README)."""

import unittest

from src import ui


class ColorTests(unittest.TestCase):
    def tearDown(self):
        ui.configure()   # restore auto-detected defaults for later tests

    def test_no_styling_when_color_is_off(self):
        ui.configure(color=False)
        self.assertEqual(ui.c("text", "RED", "BOLD"), "text")

    def test_styling_when_color_is_on(self):
        ui.configure(rich=False, color=True)
        styled = ui.c("text", "RED")
        self.assertNotEqual(styled, "text")
        self.assertIn("text", styled)
        self.assertTrue(styled.startswith(ui.C.RED))
        self.assertTrue(styled.endswith(ui.C.RESET))

    def test_no_styles_requested_is_a_no_op(self):
        ui.configure(rich=False, color=True)
        self.assertEqual(ui.c("text"), "text")


class EscapeTests(unittest.TestCase):
    def test_brackets_are_neutralised_for_rich_markup(self):
        if not ui.HAVE_RICH:
            self.skipTest("rich is not installed in this environment")
        escaped = ui._esc("[q]")
        self.assertNotEqual(escaped, "[q]")
        self.assertIn("q", escaped)

    def test_escaping_is_idempotent_on_plain_text(self):
        self.assertIn("hello", ui._esc("hello"))


class FileExtTests(unittest.TestCase):
    def test_python_exercise_gets_py(self):
        self.assertEqual(ui._file_ext({"oracle": lambda: None}), ".py")

    def test_c_function_kind_gets_c(self):
        self.assertEqual(ui._file_ext({"oracle_c": "int f(void);",
                                       "prototype": "int f(void);"}), ".c")

    def test_c_program_kind_gets_c(self):
        # "program"-kind C exercises (own main(), no harness) carry no
        # "prototype" — only "oracle_c" is common to every C exercise.
        self.assertEqual(ui._file_ext({"oracle_c": "int main(void){}",
                                       "kind": "program"}), ".c")


class FirstDiffIndexTests(unittest.TestCase):
    def test_identical_strings_return_none(self):
        self.assertIsNone(ui.first_diff_index("abc", "abc"))

    def test_divergence_points_at_the_first_differing_character(self):
        self.assertEqual(ui.first_diff_index("hello", "hallo"), 1)

    def test_one_string_a_prefix_of_the_other_points_past_the_shorter_one(self):
        self.assertEqual(ui.first_diff_index("abc", "abcdef"), 3)
        self.assertEqual(ui.first_diff_index("abcdef", "abc"), 3)

    def test_empty_strings_are_identical(self):
        self.assertIsNone(ui.first_diff_index("", ""))

    def test_completely_different_strings_diverge_at_zero(self):
        self.assertEqual(ui.first_diff_index("abc", "xyz"), 0)


class PassRateTierTests(unittest.TestCase):
    def test_solid_at_and_above_80_percent(self):
        self.assertEqual(ui._pass_rate_tier(0.8), "green")
        self.assertEqual(ui._pass_rate_tier(1.0), "green")

    def test_shaky_between_50_and_80_percent(self):
        self.assertEqual(ui._pass_rate_tier(0.5), "yellow")
        self.assertEqual(ui._pass_rate_tier(0.79), "yellow")

    def test_struggling_below_50_percent(self):
        self.assertEqual(ui._pass_rate_tier(0.0), "red")
        self.assertEqual(ui._pass_rate_tier(0.49), "red")


class SplitSubjectTests(unittest.TestCase):
    def setUp(self):
        self.subject = (
            "Assignment name  : py_demo\n"
            "Expected files   : py_demo.py\n"
            "Allowed functions: None\n"
            + "-" * 20 + "\n\n"
            "Some prose explaining the exercise.\n\n"
            "    def demo(x: int) -> int:\n\n"
            "Examples:\n"
            "    demo(1) -> 2\n"
            "    demo(2) -> 4\n"
        )

    def test_header_lines_are_extracted(self):
        header, _, _, _ = ui._split_subject(self.subject)
        joined = "\n".join(header)
        self.assertIn("Assignment name  : py_demo", joined)
        self.assertIn("Allowed functions: None", joined)

    def test_signature_is_found(self):
        _, _, signature, _ = ui._split_subject(self.subject)
        self.assertEqual(signature, "def demo(x: int) -> int:")

    def test_prose_excludes_header_and_examples(self):
        _, prose, _, _ = ui._split_subject(self.subject)
        self.assertIn("Some prose explaining the exercise.", prose)
        self.assertNotIn("Assignment name", prose)
        self.assertNotIn("demo(1)", prose)

    def test_examples_are_captured(self):
        _, _, _, examples = ui._split_subject(self.subject)
        self.assertIn("demo(1) -> 2", examples)
        self.assertIn("demo(2) -> 4", examples)


if __name__ == "__main__":
    unittest.main()
