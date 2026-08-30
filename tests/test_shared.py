#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unit tests for the shared quality-of-life layer used by both testers:
settings.py, stats.py, session_store.py, report_export.py. Every test
patches each module's own path constants to a throwaway temp directory —
never touches the student's real ~/.examshell/."""

import argparse
import os
import random
import tempfile
import unittest
from unittest.mock import patch

from src import report_export, session_store, settings, stats
from src.examshell import Session


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.config_path = os.path.join(self.tmpdir.name, "config.json")
        patcher = patch.object(settings, "CONFIG_PATH", self.config_path)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_load_config_missing_file_is_empty(self):
        self.assertEqual(settings.load_config(), {})

    def test_load_config_corrupt_file_is_empty(self):
        with open(self.config_path, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        self.assertEqual(settings.load_config(), {})

    def test_load_config_non_dict_json_is_empty(self):
        with open(self.config_path, "w", encoding="utf-8") as fh:
            fh.write("[1, 2, 3]")
        self.assertEqual(settings.load_config(), {})

    def test_save_and_load_round_trip(self):
        ok = settings.save_config({"theme": "light", "timeout": 5})
        self.assertTrue(ok)
        self.assertEqual(settings.load_config(), {"theme": "light", "timeout": 5})

    def test_save_config_drops_non_persistable_keys(self):
        settings.save_config({"theme": "dark", "totally_made_up": "x"})
        saved = settings.load_config()
        self.assertIn("theme", saved)
        self.assertNotIn("totally_made_up", saved)

    def test_save_config_drops_none_values(self):
        settings.save_config({"theme": "dark", "fuzz": None})
        saved = settings.load_config()
        self.assertIn("theme", saved)
        self.assertNotIn("fuzz", saved)

    def test_save_config_survives_unwritable_dir(self):
        # DATA_DIR unset/unwritable: os.makedirs should fail -> best-effort False
        with patch.object(settings, "DATA_DIR", "/this/does/not/exist/at/all"), \
             patch.object(settings, "CONFIG_PATH",
                          "/this/does/not/exist/at/all/config.json"):
            self.assertFalse(settings.save_config({"theme": "dark"}))

    def test_merged_prefers_explicit_cli_flag(self):
        args = argparse.Namespace(theme="highcontrast")
        config = {"theme": "light"}
        self.assertEqual(settings.merged(args, config, "theme", "dark"), "highcontrast")

    def test_merged_falls_back_to_config_file(self):
        args = argparse.Namespace(theme=None)
        config = {"theme": "light"}
        self.assertEqual(settings.merged(args, config, "theme", "dark"), "light")

    def test_merged_falls_back_to_default(self):
        args = argparse.Namespace(theme=None)
        self.assertEqual(settings.merged(args, {}, "theme", "dark"), "dark")

    def test_merged_missing_attr_on_args_falls_back(self):
        args = argparse.Namespace()
        self.assertEqual(settings.merged(args, {}, "theme", "dark"), "dark")


class StatsTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.stats_path = os.path.join(self.tmpdir.name, "stats.jsonl")
        patcher = patch.object(stats, "STATS_PATH", self.stats_path)
        patcher.start()
        self.addCleanup(patcher.stop)
        data_patcher = patch.object(stats, "DATA_DIR", self.tmpdir.name)
        data_patcher.start()
        self.addCleanup(data_patcher.stop)

    def test_load_all_on_missing_file_is_empty(self):
        self.assertEqual(stats.load_all(), [])

    def test_record_then_load_round_trips(self):
        stats.record("py", "py_inter", 1, True, 10, 10, "practice")
        events = stats.load_all()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["exercise"], "py_inter")
        self.assertTrue(events[0]["ok"])

    def test_load_all_filters_by_tool(self):
        stats.record("py", "py_inter", 1, True, 10, 10, "practice")
        stats.record("c", "ft_atoi", 2, False, 3, 9, "practice")
        self.assertEqual(len(stats.load_all("py")), 1)
        self.assertEqual(len(stats.load_all("c")), 1)
        self.assertEqual(len(stats.load_all()), 2)

    def test_load_all_skips_malformed_lines(self):
        with open(self.stats_path, "w", encoding="utf-8") as fh:
            fh.write('{"tool": "py", "ok": true}\n')
            fh.write("not json at all\n")
            fh.write("\n")  # blank line
            fh.write('{"tool": "py", "ok": false}\n')
        self.assertEqual(len(stats.load_all("py")), 2)

    def test_best_exam_time_none_when_no_completions(self):
        stats.record("py", "py_inter", 1, True, 10, 10, "practice")
        self.assertIsNone(stats.best_exam_time("py"))

    def test_best_exam_time_is_the_minimum(self):
        stats.record_exam_complete("py", 120.0, 6, 100)
        stats.record_exam_complete("py", 90.0, 6, 100)
        stats.record_exam_complete("py", 150.0, 8, 100)
        self.assertEqual(stats.best_exam_time("py"), 90.0)

    def test_summarize_empty(self):
        summary = stats.summarize("py")
        self.assertEqual(summary["total_attempts"], 0)
        self.assertEqual(summary["pass_rate"], 0.0)
        self.assertEqual(summary["per_exercise"], {})
        self.assertIsNone(summary["best_seconds"])

    def test_summarize_aggregates_attempts_and_passes(self):
        stats.record("py", "py_inter", 1, True, 10, 10, "practice")
        stats.record("py", "py_inter", 1, False, 3, 10, "practice")
        stats.record("py", "py_bracket_validator", 1, True, 5, 5, "practice")
        summary = stats.summarize("py")
        self.assertEqual(summary["total_attempts"], 3)
        self.assertEqual(summary["total_passes"], 2)
        self.assertAlmostEqual(summary["pass_rate"], 2 / 3)
        self.assertEqual(summary["per_exercise"]["py_inter"],
                         {"attempts": 2, "passes": 1})
        self.assertEqual(summary["per_exercise"]["py_bracket_validator"],
                         {"attempts": 1, "passes": 1})

    def test_summarize_excludes_exam_complete_from_per_exercise(self):
        stats.record("py", "py_inter", 1, True, 10, 10, "exam")
        stats.record_exam_complete("py", 100.0, 6, 100)
        summary = stats.summarize("py")
        self.assertEqual(summary["total_attempts"], 1)  # exam-complete excluded
        self.assertEqual(summary["exam_completions"], 1)
        self.assertEqual(summary["best_seconds"], 100.0)


class SessionStoreTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        patcher = patch.object(session_store, "DATA_DIR", self.tmpdir.name)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _session(self):
        s = Session(login="alice")
        s.start()
        s.level = 3
        s.passed = ["py_inter", "py_bracket_validator"]
        s.attempts = 5
        s.history = [(1, "py_inter", 1, 12.5), (2, "py_bracket_validator", 2, 30.0)]
        return s

    def test_load_with_nothing_saved_is_none(self):
        self.assertIsNone(session_store.load("py"))

    def test_save_then_load_round_trips_the_shape(self):
        session = self._session()
        rng = random.Random(42)
        ok = session_store.save("py", session, rng, "py_hidenp", level_attempts=2)
        self.assertTrue(ok)
        data = session_store.load("py")
        self.assertIsNotNone(data)
        self.assertEqual(data["login"], "alice")
        self.assertEqual(data["level"], 3)
        self.assertEqual(data["current_ex"], "py_hidenp")
        self.assertEqual(data["passed"], ["py_inter", "py_bracket_validator"])
        self.assertEqual(data["attempts"], 5)
        self.assertEqual(data["level_attempts"], 2)

    def test_rng_state_round_trips_identically(self):
        session = self._session()
        rng = random.Random(1234)
        rng.random()  # advance the state away from the seed-fresh state
        expected_next = [rng.random() for _ in range(5)]
        rng2 = random.Random(1234)
        rng2.random()
        session_store.save("py", session, rng2, "py_hidenp")
        data = session_store.load("py")
        restored = session_store.rng_from_saved(data)
        got_next = [restored.random() for _ in range(5)]
        self.assertEqual(got_next, expected_next)

    def test_load_rejects_a_hand_edited_incomplete_file(self):
        path = session_store._path("py")
        os.makedirs(self.tmpdir.name, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write('{"login": "alice"}')  # missing required keys
        self.assertIsNone(session_store.load("py"))

    def test_load_rejects_corrupt_json(self):
        path = session_store._path("py")
        os.makedirs(self.tmpdir.name, exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("{not json")
        self.assertIsNone(session_store.load("py"))

    def test_clear_removes_the_file(self):
        session = self._session()
        session_store.save("py", session, random.Random(1), "py_hidenp")
        self.assertIsNotNone(session_store.load("py"))
        session_store.clear("py")
        self.assertIsNone(session_store.load("py"))

    def test_clear_on_nothing_saved_does_not_raise(self):
        session_store.clear("py")  # must not raise

    def test_py_and_c_tools_use_separate_files(self):
        session = self._session()
        session_store.save("py", session, random.Random(1), "py_hidenp")
        self.assertIsNone(session_store.load("c"))
        self.assertIsNotNone(session_store.load("py"))


class ReportExportTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.reports_dir = os.path.join(self.tmpdir.name, "reports")
        patcher = patch.object(report_export, "REPORTS_DIR", self.reports_dir)
        patcher.start()
        self.addCleanup(patcher.stop)

    def _session(self):
        s = Session(login="bob")
        s.start()
        s.passed = ["py_inter"]
        s.attempts = 3
        s.history = [(1, "py_inter", 3, 45.0)]
        return s

    def test_write_report_returns_a_path_that_exists(self):
        session = self._session()
        path = report_export.write_exam_report("py", session, 6, True, ["🏅 Flawless"])
        self.assertIsNotNone(path)
        self.assertTrue(os.path.isfile(path))

    def test_report_content_has_key_fields(self):
        session = self._session()
        path = report_export.write_exam_report("py", session, 6, True, ["🏅 Flawless"])
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("Exam PASSED", content)
        self.assertIn("bob", content)
        self.assertIn("Python (Rank 03)", content)
        self.assertIn("🏅 Flawless", content)
        self.assertIn("py_inter", content)

    def test_aborted_report_has_no_achievements_line(self):
        session = self._session()
        path = report_export.write_exam_report("c", session, 4, False)
        with open(path, encoding="utf-8") as fh:
            content = fh.read()
        self.assertIn("Exam aborted", content)
        self.assertIn("C (Rank 02)", content)
        self.assertNotIn("Achievements", content)

    def test_write_report_survives_unwritable_dir(self):
        with patch.object(report_export, "REPORTS_DIR", "/this/does/not/exist/at/all"):
            session = self._session()
            path = report_export.write_exam_report("py", session, 6, True)
        self.assertIsNone(path)


if __name__ == "__main__":
    unittest.main()
