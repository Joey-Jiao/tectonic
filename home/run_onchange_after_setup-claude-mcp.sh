#!/bin/sh
set -e

if ! command -v claude >/dev/null 2>&1; then
    exit 0
fi

ensure_mcp() {
    name=$1
    url=$2
    if ! claude mcp list 2>/dev/null | grep -q "^${name}:"; then
        claude mcp add --scope user --transport http "$name" "$url"
    fi
}

ensure_mcp strata http://campbell:8716/mcp/
