#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
source pa2/env.sh
case "${1:-13}" in
  13) exec "$NEMU_HOME/build/riscv32-nemu-interpreter" ;;
  14) python3 pa2/test_demo.py; printf '\n按回车关闭窗口。'; read -r _ ;;
  *) echo 'usage: bash tools/run-pa.sh 13|14' >&2; exit 2 ;;
esac
