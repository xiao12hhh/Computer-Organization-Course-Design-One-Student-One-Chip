#!/bin/bash
set -eu
root=$(cd "$(dirname "$0")/.." && pwd)
desktop=$(xdg-user-dir DESKTOP)
mkdir -p "$desktop"
for spec in '6:Week09-Shift-LFSR' '7:Week09-Keyboard-FSM' '11:Week11-CPU-Sum55'; do
  mode=${spec%%:*};name=${spec#*:}
  file="$desktop/$name.desktop"
  cat > "$file" <<EOF
[Desktop Entry]
Type=Application
Name=$name
Exec=bash "$root/tools/run-lab.sh" $mode
Path=$root
Terminal=false
Icon=applications-engineering
EOF
  chmod +x "$file"
  gio set "$file" metadata::trusted true 2>/dev/null || true
done
cat > "$desktop/Week12-NEMU.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Week12-NEMU-Debugger
Exec=$HOME/course-nemu/build/riscv32-nemu-interpreter
Path=$root
Terminal=true
Icon=utilities-terminal
EOF
chmod +x "$desktop/Week12-NEMU.desktop"
gio set "$desktop/Week12-NEMU.desktop" metadata::trusted true 2>/dev/null || true
if [ ! -e "$desktop/Weeks09-12" ]; then ln -s "$root" "$desktop/Weeks09-12"; fi
echo 'Installed Week09/Week11/Week12 desktop launchers'
