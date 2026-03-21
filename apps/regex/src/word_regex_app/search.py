"""Dictionary loading and regex search helpers.

Copyright (c) 2026 The Smart Guild LLC
Maintainer: Todd O'Connell <toddsoc@linux.com>
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import regex


class InvalidRegexError(ValueError):
    pass


class RegexTimeoutError(RuntimeError):
    pass


@dataclass(frozen=True)
class DictionaryConfig:
    dictionary_id: str
    name: str
    path: Path


@dataclass(frozen=True)
class WordDirectory:
    path: Path
    words: tuple[str, ...]

    @classmethod
    def from_path(cls, path: Path) -> "WordDirectory":
        return cls(path=path, words=load_words(str(path)))

    @property
    def word_count(self) -> int:
        return len(self.words)

    def search(self, pattern_text: str, limit: int, timeout_seconds: float) -> list[str]:
        try:
            pattern = regex.compile(pattern_text)
        except regex.error as exc:
            raise InvalidRegexError(str(exc)) from exc

        matches = []
        try:
            for word in self.words:
                if pattern.search(word, timeout=timeout_seconds):
                    matches.append(word)
                    if len(matches) >= limit:
                        break
        except TimeoutError as exc:
            raise RegexTimeoutError() from exc

        return matches


def app_root() -> Path:
    current = Path(__file__).resolve()
    for parent in current.parents:
        if (parent / "data").is_dir():
            return parent
    raise FileNotFoundError(f"Could not locate app data directory from: {current}")


def data_dir() -> Path:
    return app_root() / "data"


def dictionaries_config_path() -> Path:
    return data_dir() / "dictionaries.json"


@lru_cache(maxsize=1)
def load_dictionary_configs() -> tuple[DictionaryConfig, ...]:
    config_path = dictionaries_config_path()
    allowed_base = data_dir().resolve()
    if not config_path.exists() or not config_path.is_file():
        raise FileNotFoundError(f"Dictionary config not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as handle:
        raw_configs = json.load(handle)

    if not isinstance(raw_configs, list) or not raw_configs:
        raise ValueError("Dictionary config must contain a non-empty list of dictionaries.")

    dictionaries = []
    seen_ids: set[str] = set()

    for index, entry in enumerate(raw_configs, start=1):
        if not isinstance(entry, dict):
            raise ValueError(f"Dictionary config entry {index} must be an object.")

        dictionary_id = str(entry.get("id", "")).strip()
        name = str(entry.get("name", "")).strip()
        file_name = str(entry.get("file", "")).strip()

        if not dictionary_id or not name or not file_name:
            raise ValueError(
                f"Dictionary config entry {index} must define non-empty 'id', 'name', and 'file' values."
            )

        if dictionary_id in seen_ids:
            raise ValueError(f"Duplicate dictionary id in config: {dictionary_id}")

        path = (allowed_base / file_name).resolve()
        if not path.is_relative_to(allowed_base):
            raise ValueError(
                f"Configured dictionary file must stay within {allowed_base}: {file_name}"
            )
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Configured dictionary file not found: {path}")

        seen_ids.add(dictionary_id)
        dictionaries.append(DictionaryConfig(dictionary_id=dictionary_id, name=name, path=path))

    return tuple(dictionaries)


def default_dictionary() -> DictionaryConfig:
    return load_dictionary_configs()[0]


def resolve_dictionary(dictionary_id: str | None) -> DictionaryConfig:
    if dictionary_id:
        for dictionary in load_dictionary_configs():
            if dictionary.dictionary_id == dictionary_id:
                return dictionary
    return default_dictionary()


@lru_cache(maxsize=8)
def load_words(path_str: str) -> tuple[str, ...]:
    path = Path(path_str)
    with path.open("r", encoding="utf-8") as handle:
        return tuple(
            line.strip()
            for line in handle
            if line.strip() and not line.startswith("#")
        )
