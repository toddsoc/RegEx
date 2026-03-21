"""Flask application factory for Word Regex Search.

Copyright (c) 2026 The Smart Guild LLC
Maintainer: Todd O'Connell <toddsoc@linux.com>
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from urllib.parse import urlsplit

from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from .search import (
    InvalidRegexError,
    RegexTimeoutError,
    WordDirectory,
    default_dictionary,
    load_dictionary_configs,
    resolve_dictionary,
)


def _parse_int_env(name: str, default: int, minimum: int = 1) -> int:
    value = os.getenv(name, str(default))
    try:
        parsed = int(value)
    except ValueError:
        return default
    return max(parsed, minimum)


def _parse_float_env(name: str, default: float, minimum: float = 0.001) -> float:
    value = os.getenv(name, str(default))
    try:
        parsed = float(value)
    except ValueError:
        return default
    return max(parsed, minimum)


def _is_same_origin_request() -> bool:
    origin = request.headers.get("Origin", "").strip()
    referer = request.headers.get("Referer", "").strip()
    host = request.host

    if origin:
        origin_parts = urlsplit(origin)
        return bool(origin_parts.scheme and origin_parts.netloc and origin_parts.netloc == host)

    if referer:
        referer_parts = urlsplit(referer)
        return bool(referer_parts.scheme and referer_parts.netloc and referer_parts.netloc == host)

    return False


def create_app() -> Flask:
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    app.config["RESULT_LIMIT"] = _parse_int_env("RESULT_LIMIT", 200)
    app.config["REGEX_TIMEOUT_SECONDS"] = _parse_float_env("REGEX_TIMEOUT_SECONDS", 0.05)
    app.config["MAX_PATTERN_LENGTH"] = _parse_int_env("MAX_PATTERN_LENGTH", 256)

    def render_search_page(
        *,
        pattern: str,
        matches: list[str],
        error: str | None,
        searched: bool,
        selected_dictionary_id: str,
    ) -> str:
        dictionary = resolve_dictionary(selected_dictionary_id)

        return render_template(
            "index.html",
            pattern=pattern,
            matches=matches,
            error=error,
            searched=searched,
            result_limit=app.config["RESULT_LIMIT"],
            dictionaries=load_dictionary_configs(),
            selected_dictionary_id=dictionary.dictionary_id,
        )

    @app.get("/")
    def index() -> str:
        return render_search_page(
            pattern="^$",
            matches=[],
            error=None,
            searched=False,
            selected_dictionary_id=default_dictionary().dictionary_id,
        )

    @app.post("/")
    def search() -> str:
        pattern = request.form.get("pattern", "").strip()
        selected_dictionary_id = request.form.get("dictionary", "").strip()
        dictionary = resolve_dictionary(selected_dictionary_id)
        word_directory = WordDirectory.from_path(dictionary.path)
        matches = []
        error = None

        if not _is_same_origin_request():
            error = "Request blocked: invalid request origin."
        elif not pattern:
            error = "Enter a regex pattern before searching."
        elif len(pattern) > app.config["MAX_PATTERN_LENGTH"]:
            error = (
                "Regex pattern is too long. "
                f"Maximum allowed length is {app.config['MAX_PATTERN_LENGTH']} characters."
            )
        else:
            try:
                matches = word_directory.search(
                    pattern_text=pattern,
                    limit=app.config["RESULT_LIMIT"],
                    timeout_seconds=app.config["REGEX_TIMEOUT_SECONDS"],
                )
            except InvalidRegexError as exc:
                error = f"Invalid regex: {exc}"
            except RegexTimeoutError:
                error = "The regex took too long to evaluate. Tighten the pattern and try again."

        return render_search_page(
            pattern=pattern,
            matches=matches,
            error=error,
            searched=True,
            selected_dictionary_id=dictionary.dictionary_id,
        )

    return app
