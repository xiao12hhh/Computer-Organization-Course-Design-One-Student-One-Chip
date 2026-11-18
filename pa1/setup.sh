#!/bin/bash
set -eu
repo=${1:-"$HOME/course-nemu"}
base=8e7a0fecc95b5b5d2c1f6be0ec1b703da93356c0
if [ ! -d "$repo/.git" ]; then
  git clone --depth 1 --branch ics2024 https://github.com/NJU-ProjectN/nemu.git "$repo"
  git -C "$repo" fetch --depth 1 origin "$base"
  git -C "$repo" checkout --detach "$base"
fi
python3 "$(dirname "$0")/install.py" "$repo"
export NEMU_HOME=$(cd "$repo" && pwd)
if [ ! -f "$repo/.config" ]; then make -C "$repo" course_pa1_defconfig; fi
make -C "$repo" -j2
printf '\nStart debugger: %s/build/riscv32-nemu-interpreter\n' "$repo"
