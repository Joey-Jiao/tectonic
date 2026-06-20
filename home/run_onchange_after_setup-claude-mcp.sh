#!/bin/sh
set -e

if ! command -v claude >/dev/null 2>&1; then
    exit 0
fi

ensure_stdio_mcp() {
    name=$1
    shift
    expected="$*"
    current=$(claude mcp list 2>/dev/null | grep "^${name}:" || true)
    if [ -n "$current" ] && echo "$current" | grep -qF "$expected"; then
        return
    fi
    if [ -n "$current" ]; then
        claude mcp remove "$name" 2>/dev/null || true
    fi
    claude mcp add --scope user --transport stdio "$name" "$@"
}

ensure_stdio_mcp strata strata serve
