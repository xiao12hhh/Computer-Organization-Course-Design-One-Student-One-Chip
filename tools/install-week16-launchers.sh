#!/usr/bin/env bash
set -eu
root="$(cd "$(dirname "$0")/.." && pwd)"
desktop="$(xdg-user-dir DESKTOP)"
while read -r name mode; do
  file="$desktop/$name.desktop"
  printf '[Desktop Entry]\nType=Application\nName=%s\nExec=bash "%s/tools/run-week16.sh" %s\nTerminal=true\nIcon=utilities-terminal\n' "$name" "$root" "$mode" > "$file"
  chmod +x "$file"
  DBUS_SESSION_BUS_ADDRESS="unix:path=/run/user/$(id -u)/bus" gio set "$file" metadata::trusted true || true
done <<'EOF'
Week15-NPC-Tests test
Week16-Mario-Characters char
Week16-Mario-NEMU graphics
Week16-Mario-Fast fast
Week16-RTC-Test rtc
EOF
