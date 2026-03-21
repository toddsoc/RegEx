#!/usr/bin/env bash
# Copyright (c) 2026 The Smart Guild LLC
# Maintainer: Todd O'Connell <toddsoc@linux.com>
# SPDX-License-Identifier: MIT

set -euo pipefail

PORT="${PORT:-8080}"
TAILSCALE_BIN="${TAILSCALE_BIN:-tailscale}"
SUDO_BIN="${SUDO_BIN:-sudo}"
APP_PATH="${APP_PATH:-/RegEx/}"

if ! command -v "$TAILSCALE_BIN" >/dev/null 2>&1; then
    echo "tailscale CLI not found in PATH" >&2
    exit 1
fi

if ! command -v "$SUDO_BIN" >/dev/null 2>&1; then
    echo "sudo not found in PATH" >&2
    exit 1
fi

echo "Resetting existing Tailscale Serve configuration..."
"$SUDO_BIN" "$TAILSCALE_BIN" serve reset

echo "Publishing HTTPS for localhost:${PORT}${APP_PATH} to your tailnet..."
"$SUDO_BIN" "$TAILSCALE_BIN" serve --bg "$PORT"

echo
"$TAILSCALE_BIN" serve status
echo
echo "App path: ${APP_PATH}"
