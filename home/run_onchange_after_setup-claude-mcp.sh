#!/bin/sh
set -e

if ! command -v claude >/dev/null 2>&1; then
    exit 0
fi

ensure_mcp() {
    name=$1
    url=$2
    current=$(claude mcp list 2>/dev/null | grep "^${name}:" || true)
    if [ -n "$current" ] && echo "$current" | grep -qF "$url"; then
        return
    fi
    if [ -n "$current" ]; then
        claude mcp remove "$name" 2>/dev/null || true
    fi
    claude mcp add --scope user --transport http "$name" "$url"
}

ensure_mcp strata http://localhost:8716/mcp/
