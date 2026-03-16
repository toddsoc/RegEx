from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import regex


class InvalidRegexError(ValueError):
    pass


class RegexTimeoutError(RuntimeError):
    pass


def _candidate_word_lists() -> list[Path]:
    env_path = os.getenv("WORD_LIST_PATH")
    base_dir = Path(__file__).resolve().parent.parent
    candidates = []
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(
        [
            Path("/usr/share/dict/words"),
            base_dir / "data" / "words.txt",
        ]
    )
    return candidates


def resolve_word_list_path() -> Path:
    for candidate in _candidate_word_lists():
        if candidate.exists() and candidate.is_file():
            return candidate

    searched = ", ".join(str(candidate) for candidate in _candidate_word_lists())
    raise FileNotFoundError(f"No word list found. Checked: {searched}")


@lru_cache(maxsize=4)
def load_words(path_str: str) -> tuple[str, ...]:
    path = Path(path_str)
    with path.open("r", encoding="utf-8") as handle:
        return tuple(
            line.strip()
            for line in handle
            if line.strip() and not line.startswith("#")
        )


@dataclass(frozen=True)
class WordDirectory:
    path: Path
    words: tuple[str, ...]

    @classmethod
    def from_environment(cls) -> "WordDirectory":
        path = resolve_word_list_path()
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