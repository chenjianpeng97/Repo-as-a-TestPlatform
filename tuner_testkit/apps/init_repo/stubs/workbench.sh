#!/usr/bin/env sh
cd "$(dirname "$0")"
exec uv run tuner-workbench "$@"
