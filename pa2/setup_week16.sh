#!/usr/bin/env bash
set -eu
here="$(dirname "$(realpath "$0")")"
root="$(dirname "$here")"
source "$here/env.sh"
if [ ! -d "$HOME/course-riscv-tests/.git" ]; then
  git clone --depth 1 https://github.com/NJU-ProjectN/riscv-tests-am.git "$HOME/course-riscv-tests"
  git -C "$HOME/course-riscv-tests" fetch --depth 1 origin 676cbc7a4e520fca1c3d4dd1b586b2550769e02e
  git -C "$HOME/course-riscv-tests" checkout --detach 676cbc7a4e520fca1c3d4dd1b586b2550769e02e
fi
python3 "$here/install_io.py"
cp "$here/course_io_defconfig" "$NEMU_HOME/configs/"
make -C "$NEMU_HOME" course_io_defconfig
make -C "$NEMU_HOME" -j2
make -C "$root/npc/minirv"
cd "$root"
python3 pa2/prepare_litenes.py --mode char
make -C build/litenes-char ARCH=minirv-npc image
python3 pa2/prepare_litenes.py --mode graphics
make -C build/litenes-graphics ARCH=riscv32-nemu image
