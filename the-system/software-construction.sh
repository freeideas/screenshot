#!/usr/bin/env bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR/.."

if [[ "$(pwd)" != "$(cd "$PROJECT_ROOT" && pwd)" ]]; then
    echo "Please run this script from the project root:"
    echo "  cd $(cd "$PROJECT_ROOT" && pwd)"
    exit 1
fi

if [[ "$(uname)" == "Darwin" ]]; then
    UV_BIN="$SCRIPT_DIR/bin/uv.mac"
else
    UV_BIN="$SCRIPT_DIR/bin/uv.linux"
fi

"$UV_BIN" run --script "$SCRIPT_DIR/scripts/software-construction.py" "$@"
