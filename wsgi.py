"""WSGI entrypoint for Word Regex Search.

Copyright (c) 2026 The Smart Guild LLC
Maintainer: Todd O'Connell <toddsoc@linux.com>
SPDX-License-Identifier: MIT
"""

from word_regex_app import create_app

app = create_app()
