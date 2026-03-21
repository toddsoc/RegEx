#!/usr/bin/env bash

set -euo pipefail

PORT="${PORT:-8080}"
TAILSCALE_BIN="${TAILSCALE_BIN:-tailscale}"
SUDO_BIN="${SUDO_BIN:-sudo}"

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

echo "Publishing HTTPS for localhost:${PORT} to your tailnet..."
"$SUDO_BIN" "$TAILSCALE_BIN" serve --bg "$PORT"

echo
"$TAILSCALE_BIN" serve status
