#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/../nvboard"
export NVBOARD_HOME="${NVBOARD_HOME:-$HOME/ysyx-workbench/nvboard}"
exec make DEMO="${1:-0}" run
