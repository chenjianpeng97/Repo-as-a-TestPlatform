#!/usr/bin/env sh
# Non-coder entry: git pull, then ./workbench.sh from the dogfood directory.
cd "$(dirname "$0")"
exec uv run tuner-workbench "$@"
