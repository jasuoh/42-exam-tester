#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for the pure logic in c_exam/grader.py — literal encoding,
comment/string stripping, forbidden-call detection, case-chunk parsing —
plus one real end-to-end grade() call through an actual compiler.

The end-to-end tests are skipped automatically when no C compiler is on
PATH, so the suite still runs clean on a compiler-less machine (mirrors
how tests/test_grader.py's sandbox tests don't need anything special, but
here a missing `cc` genuinely can't be worked around)."""

import random
import shutil
import tempfile
import unittest

from c_exam import grader

HAVE_CC = shutil.which(grader.DEFAULT_CC) is not None
skip_without_cc = unittest.skipUnless(HAVE_CC, "no C compiler (%r) on PATH"
                                      % grader.DEFAULT_CC)


class CLiteralTests(unittest.TestCase):
    def test_char_literal_escapes_special_chars(self):
        self.assertEqual(grader.c_char_literal("a"), "'a'")
        self.assertEqual(grader.c_char_literal("\n"), "'\\n'")
        self.assertEqual(grader.c_char_literal("'"), "'\\''")
        self.assertEqual(grader.c_char_literal("\\"), "'\\\\'")

    def test_string_literal_escapes_special_chars(self):
        self.assertEqual(grader.c_string_literal("hello"), '"hello"')
        self.assertEqual(grader.c_string_literal('a"b'), '"a\\"b"')
        self.assertEqual(grader.c_string_literal("a\nb"), '"a\\nb"')
        self.assertEqual(grader.c_string_literal(""), '""')

    def test_string_literal_escapes_non_ascii(self):
        self.assertIn("\\x", grader.c_string_literal("\x01"))


class StripCommentsAndStringsTests(unittest.TestCase):
    def test_line_comment_is_removed(self):
        stripped = grader._strip_comments_and_strings("int main(void) // hi\n{ return 0; }")
        self.assertNotIn("hi", stripped)
        self.assertIn("int main(void)", stripped)

    def test_block_comment_is_removed(self):
        stripped = grader._strip_comments_and_strings("/* main( */ int x;")
        self.assertNotIn("main(", stripped)

    def test_string_contents_are_removed(self):
        stripped = grader._strip_comments_and_strings('char *s = "call strlen(x) here";')
        self.assertNotIn("strlen(", stripped)

    def test_real_code_is_untouched(self):
        src = "int ft_strlen(char *str)\n{\n    return 0;\n}\n"
        self.assertEqual(grader._strip_comments_and_strings(src), src)


class ForbiddenCallTests(unittest.TestCase):
    def test_finds_a_real_call(self):
        stripped = grader._strip_comments_and_strings("int x = strlen(str);")
        self.assertEqual(grader.find_forbidden(stripped, ["strlen"]), ["strlen"])

    def test_ignores_a_call_inside_a_comment(self):
        stripped = grader._strip_comments_and_strings("// strlen(str) is banned\nint y;")
        self.assertEqual(grader.find_forbidden(stripped, ["strlen"]), [])

    def test_does_not_false_positive_on_a_prefix(self):
        # "ft_strlen(" contains "strlen(" as a substring but not as its own
        # word — \b must not match inside another identifier.
        stripped = grader._strip_comments_and_strings("int x = ft_strlen(str);")
        self.assertEqual(grader.find_forbidden(stripped, ["strlen"]), [])


class DuplicateMainTests(unittest.TestCase):
    def test_detects_ld64_wording(self):
        self.assertTrue(grader._is_duplicate_main(
            "duplicate symbol '_main' in:\n  a.o\n  b.o\nld: 1 duplicate symbols"))

    def test_detects_gnu_ld_wording(self):
        self.assertTrue(grader._is_duplicate_main(
            "b.o: in function `main':\nb.c:1: multiple definition of `main'"))

    def test_unrelated_error_is_not_flagged(self):
        self.assertFalse(grader._is_duplicate_main(
            "error: expected ';' before '}' token"))


class KrFuncPtrRegexTests(unittest.TestCase):
    """int (*cmp)() compiles fine under Apple Clang's default standard but
    not under GCC's C23 default (() there now means "no parameters", not
    "unspecified" like every older C standard) — this regex is what lets
    make c-check catch that without needing a second compiler on hand."""

    def test_flags_empty_parens_function_pointer(self):
        self.assertTrue(grader._KR_FUNC_PTR_RE.search("int (*cmp)();"))

    def test_does_not_flag_a_typed_function_pointer(self):
        self.assertFalse(grader._KR_FUNC_PTR_RE.search(
            "int (*cmp)(void *, void *);"))

    def test_does_not_flag_a_void_typed_function_pointer(self):
        self.assertFalse(grader._KR_FUNC_PTR_RE.search("void (*f)(void *);"))

    def test_does_not_flag_a_plain_prototype(self):
        self.assertFalse(grader._KR_FUNC_PTR_RE.search(
            "int ft_strlen(char *str);"))


class FuzzableTests(unittest.TestCase):
    def test_all_safe_kinds_is_fuzzable(self):
        ex = {"args": ["int", "char", "str", "int_arr", "int_list", "buf", "int_ptr"]}
        self.assertTrue(grader.is_fuzzable(ex))

    def test_fixed_callback_kind_does_not_block_fuzzing(self):
        ex = {"args": ["int_list", "cmp_ascending"]}
        self.assertTrue(grader.is_fuzzable(ex))

    def test_unsafe_kind_blocks_fuzzing(self):
        for kind in ("point", "char_grid", "voidlist", "voidlist_ptr"):
            with self.subTest(kind=kind):
                self.assertFalse(grader.is_fuzzable({"args": [kind]}))

    def test_program_kind_is_never_fuzzable(self):
        ex = {"kind": "program", "args": ["str"]}
        self.assertFalse(grader.is_fuzzable(ex))

    def test_no_args_is_fuzzable(self):
        self.assertTrue(grader.is_fuzzable({"args": []}))


class BuildFuzzCasesTests(unittest.TestCase):
    def setUp(self):
        self.rng = random.Random(1234)

    def test_generates_the_requested_count(self):
        ex = {"args": ["int", "str"]}
        cases = grader.build_fuzz_cases(ex, self.rng, 10)
        self.assertEqual(len(cases), 10)

    def test_one_value_per_non_fixed_callback_arg(self):
        ex = {"args": ["int", "cmp_ascending", "str"]}
        cases = grader.build_fuzz_cases(ex, self.rng, 5)
        for case in cases:
            self.assertEqual(len(case), 2)   # cmp_ascending consumes no value

    def test_int_values_are_in_range(self):
        ex = {"args": ["int"]}
        for case in grader.build_fuzz_cases(ex, self.rng, 200):
            self.assertTrue(-1000 <= case[0] <= 1000)

    def test_char_values_are_printable_ascii(self):
        ex = {"args": ["char"]}
        for case in grader.build_fuzz_cases(ex, self.rng, 200):
            self.assertEqual(len(case[0]), 1)
            self.assertTrue(32 <= ord(case[0]) <= 126)

    def test_buf_values_stay_well_under_the_harness_buffer(self):
        ex = {"args": ["buf"]}
        for case in grader.build_fuzz_cases(ex, self.rng, 50):
            self.assertLess(len(case[0]), 128)

    def test_str_values_use_a_safe_alphabet(self):
        ex = {"args": ["str"]}
        for case in grader.build_fuzz_cases(ex, self.rng, 50):
            for ch in case[0]:
                self.assertIn(ch, grader._FUZZ_STR_ALPHABET)

    def test_int_arr_and_int_list_are_small_int_lists(self):
        ex = {"args": ["int_arr", "int_list"]}
        for case in grader.build_fuzz_cases(ex, self.rng, 50):
            for arr in case:
                self.assertIsInstance(arr, list)
                self.assertLessEqual(len(arr), 6)
                for v in arr:
                    self.assertTrue(-50 <= v <= 50)

    def test_is_deterministic_given_the_same_rng_state(self):
        ex = {"args": ["int", "str", "int_arr"]}
        cases_a = grader.build_fuzz_cases(ex, random.Random(99), 20)
        cases_b = grader.build_fuzz_cases(ex, random.Random(99), 20)
        self.assertEqual(cases_a, cases_b)


class GenerateHarnessCasesOverrideTests(unittest.TestCase):
    def test_defaults_to_ex_cases(self):
        ex = {"function": "ft_strlen", "prototype": "int ft_strlen(char *str);",
             "args": ["str"], "returns": "int", "cases": [["a"], ["bb"]]}
        harness = grader.generate_harness(ex)
        self.assertEqual(harness.count("===CASE"), 2)

    def test_override_replaces_ex_cases(self):
        ex = {"function": "ft_strlen", "prototype": "int ft_strlen(char *str);",
             "args": ["str"], "returns": "int", "cases": [["a"]]}
        harness = grader.generate_harness(ex, [["a"], ["b"], ["c"]])
        self.assertEqual(harness.count("===CASE"), 3)


class SplitCasesTests(unittest.TestCase):
    def test_splits_by_marker(self):
        out = "===CASE 0===\nfoo\n===CASE 1===\nbar\n"
        self.assertEqual(grader.split_cases(out), {0: "foo\n", 1: "bar\n"})

    def test_missing_markers_yield_no_chunks(self):
        self.assertEqual(grader.split_cases("garbage, no markers"), {})


@skip_without_cc
class GradeEndToEndTests(unittest.TestCase):
    EX = {
        "function": "ft_strlen", "prototype": "int ft_strlen(char *str);",
        "args": ["str"], "returns": "int",
        "oracle_c": "int ft_strlen(char *str)\n{\n"
                   "    int i = 0;\n    while (str[i]) i++;\n    return i;\n}\n",
        "cases": [["hello"], [""], ["ab"]],
    }

    def _write(self, tmp, body):
        path = tmp + "/ft_strlen.c"
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        return path

    def test_correct_solution_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, self.EX["oracle_c"])
            report = grader.grade("ft_strlen", self.EX, tmp)
            self.assertTrue(report.ok, report.failures)
            self.assertEqual(report.passed, report.total)

    def test_wrong_solution_fails_with_details(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, "int ft_strlen(char *str)\n{\n"
                             "    (void)str;\n    return 42;\n}\n")
            report = grader.grade("ft_strlen", self.EX, tmp)
            self.assertFalse(report.ok)
            self.assertEqual(report.passed, 0)
            self.assertEqual(report.failures[0].got, "42")

    def test_unguarded_main_is_reported_as_forbidden(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, self.EX["oracle_c"] + "\nint main(void) { return 0; }\n")
            report = grader.grade("ft_strlen", self.EX, tmp)
            self.assertEqual(report.fatal, "FORBIDDEN_MAIN")

    def test_selftest_guarded_main_does_not_trip_the_check(self):
        # the exact shape c_exam/examshell.py's stub ships — must grade fine
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, self.EX["oracle_c"] +
                       "\n#ifdef SELF_TEST\nint main(void) { return 0; }\n#endif\n")
            report = grader.grade("ft_strlen", self.EX, tmp)
            self.assertTrue(report.ok, report.failures)

    def test_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            report = grader.grade("ft_strlen", self.EX, tmp)
            self.assertEqual(report.fatal, "FILE_MISSING")

    def test_fuzz_adds_extra_cases_and_still_passes_for_the_oracle(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, self.EX["oracle_c"])
            report = grader.grade("ft_strlen", self.EX, tmp,
                                  rng=random.Random(7), fuzz=5)
            self.assertTrue(report.ok, report.failures)
            self.assertEqual(report.total, len(self.EX["cases"]) + 5)

    def test_fuzz_zero_is_a_no_op(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, self.EX["oracle_c"])
            report = grader.grade("ft_strlen", self.EX, tmp,
                                  rng=random.Random(7), fuzz=0)
            self.assertEqual(report.total, len(self.EX["cases"]))

    def test_fuzz_is_skipped_for_an_unfuzzable_exercise(self):
        ex = dict(self.EX, args=["point"])   # not in FUZZABLE_VALUE_KINDS
        # point-kind args need real decls this stub EX lacks — just check
        # is_fuzzable directly rather than compiling; grade() consults it
        # via the same function, see test_grade_ignores_fuzz_for_program_kind
        # below for the end-to-end confirmation on a real exercise shape.
        self.assertFalse(grader.is_fuzzable(ex))

    def test_grade_ignores_fuzz_for_program_kind(self):
        program_ex = {
            "function": "echoprog", "kind": "program",
            "oracle_c": "#include <stdio.h>\n"
                       "int main(int argc, char **argv)\n{\n"
                       "    (void)argc;\n    printf(\"%s\\n\", argv[1]);\n"
                       "    return 0;\n}\n",
            "cases": [["hi"], ["there"]],
        }
        with tempfile.TemporaryDirectory() as tmp:
            self._write_named(tmp, "echoprog.c", program_ex["oracle_c"])
            report = grader.grade("echoprog", program_ex, tmp,
                                  rng=random.Random(7), fuzz=50)
            self.assertTrue(report.ok, report.failures)
            self.assertEqual(report.total, 2)   # fuzz never applies to "program" kind

    def _write_named(self, tmp, filename, body):
        path = tmp + "/" + filename
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(body)
        return path

    def test_broken_oracle_is_a_graceful_bank_error_not_a_crash(self):
        broken_ex = dict(self.EX, oracle_c="this is not valid C at all {{{")
        with tempfile.TemporaryDirectory() as tmp:
            self._write(tmp, self.EX["oracle_c"])
            report = grader.grade("ft_strlen", broken_ex, tmp)
            self.assertEqual(report.fatal, "BANK_ERROR")


if __name__ == "__main__":
    unittest.main()
