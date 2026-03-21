"""Flask application factory for Word Regex Search.

Copyright (c) 2026 The Smart Guild LLC
Maintainer: Todd O'Connell <toddsoc@linux.com>
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os

from flask import Flask, render_template, request
from werkzeug.middleware.proxy_fix import ProxyFix

from .search import InvalidRegexError, RegexTimeoutError, WordDirectory


def create_app() -> Flask:
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    app.config["RESULT_LIMIT"] = int(os.getenv("RESULT_LIMIT", "200"))
    app.config["REGEX_TIMEOUT_SECONDS"] = float(os.getenv("REGEX_TIMEOUT_SECONDS", "0.05"))

    word_directory = WordDirectory.from_environment()

    @app.get("/")
    def index() -> str:
        return render_template(
            "index.html",
            pattern="^$",
            matches=[],
            error=None,
            searched=False,
            result_limit=app.config["RESULT_LIMIT"],
            word_count=word_directory.word_count,
            word_list_path=str(word_directory.path),
        )

    @app.post("/")
    def search() -> str:
        pattern = request.form.get("pattern", "").strip()
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

        return render_template(
            "index.html",
            pattern=pattern,
            matches=matches,
            error=error,
            searched=True,
            result_limit=app.config["RESULT_LIMIT"],
            word_count=word_directory.word_count,
            word_list_path=str(word_directory.path),
        )

    return app
