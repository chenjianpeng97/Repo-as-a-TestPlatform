@echo off
REM Non-coder entry: git pull, then double-click or run this from the dogfood directory.
cd /d "%~dp0"
uv run tuner-workbench
