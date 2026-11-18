#!/usr/bin/env bash
set -eu
here="$(dirname "$(realpath "$0")")"
source "$here/env.sh"
if ! command -v riscv64-linux-gnu-gcc >/dev/null; then bash "$here/setup_toolchain.sh"; fi
clone_at() {
  url=$1;dest=$2;base=$3;branch=$4
  if [ ! -d "$dest/.git" ]; then
    git clone --depth 1 -b "$branch" "$url" "$dest"
    git -C "$dest" fetch --depth 1 origin "$base"
    git -C "$dest" checkout --detach "$base"
  fi
  test "$(git -C "$dest" rev-parse HEAD)" = "$base"
}
clone_at https://github.com/NJU-ProjectN/nemu.git "$NEMU_HOME" 8e7a0fecc95b5b5d2c1f6be0ec1b703da93356c0 ics2024
clone_at https://github.com/NJU-ProjectN/abstract-machine.git "$AM_HOME" 9bc0a93c52c928a6de970f39a507be94cfb63a9f ics2026
clone_at https://github.com/NJU-ProjectN/am-kernels.git "$HOME/course-am-kernels" 9c433f7cf4b4e05d09543bf7e269b23502d1b2b6 ics2026
python3 "$here/../pa1/install.py" "$NEMU_HOME" --rv32im
python3 "$here/install_am.py" "$AM_HOME"
cp "$here/course_pa2_defconfig" "$NEMU_HOME/configs/"
make -C "$NEMU_HOME" course_pa2_defconfig
make -C "$NEMU_HOME" -j2
