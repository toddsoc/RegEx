"""Flask application factory for Word Regex Search.

Copyright (c) 2026 The Smart Guild LLC
Maintainer: Todd O'Connell <toddsoc@linux.com>
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

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


def create_app() -> Flask:
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    app.config["RESULT_LIMIT"] = int(os.getenv("RESULT_LIMIT", "200"))
    app.config["REGEX_TIMEOUT_SECONDS"] = float(os.getenv("REGEX_TIMEOUT_SECONDS", "0.05"))

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

        if not pattern:
            error = "Enter a regex pattern before searching."
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
