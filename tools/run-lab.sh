#!/bin/bash
set -eu
cd "$(dirname "$0")/../nvboard-labs"
exec make DEMO="${1:-6}" run
