#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parent / "find_guidance.py"
SKILL_DIR = SCRIPT.parent.parent


def run_helper(*args: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=SKILL_DIR,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


class FindGuidanceTests(unittest.TestCase):
    def assert_query_finds(self, query: str, expected_heading: str) -> None:
        result = run_helper(query, "--top", "1")
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn(expected_heading, result.stdout)

    def test_russian_network_query(self) -> None:
        self.assert_query_finds("сетевой авторитет", "Network Authority Boundaries")

    def test_two_character_ui_query(self) -> None:
        self.assert_query_finds("UI", "UI Screen")

    def test_two_character_rx_query(self) -> None:
        self.assert_query_finds("Rx", "Direct Calls, Events, Rx, And R3")

    def test_two_character_di_query(self) -> None:
        self.assert_query_finds("DI", "Lifecycle, Composition, And DI")

    def test_nested_heading_includes_parent_context(self) -> None:
        self.assert_query_finds("serialized controls", "UI Screen > Start Direct")

    def test_top_must_be_positive(self) -> None:
        result = run_helper("network", "--top", "0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be >= 1", result.stderr)


if __name__ == "__main__":
    unittest.main()
