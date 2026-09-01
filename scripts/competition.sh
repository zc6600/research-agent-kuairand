#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/.." && pwd -P)"

exec python3 "$WORKSPACE_DIR/competitions/kuairand/runner.py" "$@"
