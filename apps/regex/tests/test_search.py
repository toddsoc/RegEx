from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from word_regex_app.search import (
    DictionaryConfig,
    InvalidRegexError,
    RegexTimeoutError,
    WordDirectory,
    default_dictionary,
    load_dictionary_configs,
    load_words,
    resolve_dictionary,
)


class LoadWordsTests(unittest.TestCase):
    def test_load_words_skips_comments_and_blank_lines(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            word_file = Path(temp_dir) / "words.txt"
            word_file.write_text("# comment\nalpha\n\n beta \n", encoding="utf-8")

            load_words.cache_clear()

            self.assertEqual(load_words(str(word_file)), ("alpha", "beta"))


class DictionaryConfigTests(unittest.TestCase):
    def tearDown(self) -> None:
        load_dictionary_configs.cache_clear()

    def test_default_dictionary_is_first_configured_entry(self) -> None:
        dictionaries = (
            DictionaryConfig("default", "Default Dictionary", Path("/tmp/default.txt")),
            DictionaryConfig("alt", "Alt Dictionary", Path("/tmp/alt.txt")),
        )

        with patch("word_regex_app.search.load_dictionary_configs", return_value=dictionaries):
            self.assertEqual(default_dictionary(), dictionaries[0])

    def test_resolve_dictionary_uses_matching_id(self) -> None:
        dictionaries = (
            DictionaryConfig("default", "Default Dictionary", Path("/tmp/default.txt")),
            DictionaryConfig("alt", "Alt Dictionary", Path("/tmp/alt.txt")),
        )

        with patch("word_regex_app.search.load_dictionary_configs", return_value=dictionaries):
            self.assertEqual(resolve_dictionary("alt"), dictionaries[1])

    def test_resolve_dictionary_falls_back_to_default(self) -> None:
        dictionaries = (
            DictionaryConfig("default", "Default Dictionary", Path("/tmp/default.txt")),
            DictionaryConfig("alt", "Alt Dictionary", Path("/tmp/alt.txt")),
        )

        with patch("word_regex_app.search.load_dictionary_configs", return_value=dictionaries):
            self.assertEqual(resolve_dictionary("missing"), dictionaries[0])


class WordDirectoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.word_directory = WordDirectory(
            path=Path("/tmp/words.txt"),
            words=("apple", "apricot", "banana", "avocado"),
        )

    def test_search_returns_matching_words_up_to_limit(self) -> None:
        matches = self.word_directory.search(r"^a", limit=2, timeout_seconds=0.05)

        self.assertEqual(matches, ["apple", "apricot"])

    def test_search_raises_invalid_regex_error(self) -> None:
        with self.assertRaises(InvalidRegexError):
            self.word_directory.search("(", limit=10, timeout_seconds=0.05)

    def test_search_raises_timeout_error_when_pattern_times_out(self) -> None:
        timed_out_pattern = unittest.mock.Mock()
        timed_out_pattern.search.side_effect = TimeoutError()

        with patch("word_regex_app.search.regex.compile", return_value=timed_out_pattern):
            with self.assertRaises(RegexTimeoutError):
                self.word_directory.search(r"^a", limit=10, timeout_seconds=0.01)


if __name__ == "__main__":
    unittest.main()
