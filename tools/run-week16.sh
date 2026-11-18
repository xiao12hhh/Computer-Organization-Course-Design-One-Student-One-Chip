#!/usr/bin/env bash
set -eu
cd "$(dirname "$0")/.."
source pa2/env.sh
export NPC_BIN="$PWD/build/minirv-npc/npc"
case "${1:-char}" in
  char)
    printf '\033[2J\033[H字符版马里奥运行在 RTL minirv 上，速度较慢；Ctrl+C 退出。\n'
    exec "$NPC_BIN" --max 0 build/litenes-char/build/litenes-course-minirv-npc.bin ;;
  graphics)
    printf '图形版运行在 NEMU 上：I 开始，WASD 方向，J/K 动作。关闭游戏窗口退出。\n'
    exec "$NEMU_HOME/build/riscv32-nemu-interpreter" -b build/litenes-graphics/build/litenes-course-riscv32-nemu.bin ;;
  rtc) python3 npc/minirv/test_rtc.py;cat build/minirv-npc/official-rtc.txt ;;
  test) python3 npc/minirv/test_core.py ;;
  *) echo 'usage: bash tools/run-week16.sh char|graphics|rtc|test' >&2;exit 2 ;;
esac
if [ -t 0 ]; then printf '\n按回车关闭窗口。';read -r _;fi
