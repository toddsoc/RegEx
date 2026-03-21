from __future__ import annotations

import unittest

from word_regex_app import create_app
from word_regex_app.search import RegexTimeoutError


class AppRouteTests(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.client = self.app.test_client()

    def test_index_page_loads(self) -> None:
        response = self.client.get("/")
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Regex Lookup", body)
        self.assertIn("The Smart Guild LLC", body)
        self.assertIn('value="^$"', body)
        self.assertIn('name="dictionary"', body)
        self.assertIn('Default Dictionary', body)
        self.assertNotIn('Loaded words', body)
        self.assertNotIn('Source file', body)

    def test_index_generates_prefixed_urls_when_forwarded_prefix_is_present(self) -> None:
        response = self.client.get("/", headers={"X-Forwarded-Prefix": "/RegEx"})
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('href="/RegEx/static/styles.css"', body)
        self.assertIn('action="/RegEx/"', body)

    def test_search_returns_matches(self) -> None:
        response = self.client.post("/", data={"pattern": "^a", "dictionary": "default"})
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Found", body)

    def test_invalid_dictionary_selection_falls_back_to_default(self) -> None:
        response = self.client.post("/", data={"pattern": "^$", "dictionary": "missing"})
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn('value="default" selected', body)

    def test_search_rejects_empty_pattern(self) -> None:
        response = self.client.post("/", data={"pattern": "   ", "dictionary": "default"})
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Enter a regex pattern before searching.", body)

    def test_search_reports_invalid_regex(self) -> None:
        response = self.client.post("/", data={"pattern": "(", "dictionary": "default"})
        body = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Invalid regex:", body)

    def test_search_reports_timeout(self) -> None:
        with unittest.mock.patch("word_regex_app.WordDirectory.search", side_effect=RegexTimeoutError()):
            response = self.client.post("/", data={"pattern": "^a", "dictionary": "default"})

        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("The regex took too long to evaluate.", body)


if __name__ == "__main__":
    unittest.main()
