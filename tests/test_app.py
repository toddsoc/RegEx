from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from word_regex_app import create_app
from word_regex_app.search import RegexTimeoutError


class AppRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.word_file = Path(self.temp_dir.name) / "words.txt"
        self.word_file.write_text("apple\nbanana\napricot\n", encoding="utf-8")

        env_patch = patch.dict(os.environ, {"WORD_LIST_PATH": str(self.word_file)}, clear=False)
        env_patch.start()
        self.addCleanup(env_patch.stop)

        self.app = create_app()
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_index_page_loads(self) -> None:
        response = self.client.get("/")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Regex Lookup", body)
        self.assertIn("The Smart Guild LLC", body)
        self.assertIn('value="^$"', body)

    def test_search_returns_matches(self) -> None:
        response = self.client.post("/", data={"pattern": "^a"})
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("apple", body)
        self.assertIn("apricot", body)
        self.assertNotIn("banana", body)

    def test_search_rejects_empty_pattern(self) -> None:
        response = self.client.post("/", data={"pattern": "   "})
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Enter a regex pattern before searching.", body)

    def test_search_reports_invalid_regex(self) -> None:
        response = self.client.post("/", data={"pattern": "("})
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid regex:", body)

    def test_search_reports_timeout(self) -> None:
        with patch("word_regex_app.WordDirectory.search", side_effect=RegexTimeoutError()):
            response = self.client.post("/", data={"pattern": "^a"})

        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("The regex took too long to evaluate.", body)


if __name__ == "__main__":
    unittest.main()
