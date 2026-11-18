#!/usr/bin/env bash
# Local Ubuntu 22.04 toolchain, no root needed; no host libc is linked.
set -eu
root="$HOME/course-tools"
source_dir="$(dirname "$(realpath "$0")")"
mkdir -p "$root/debs" "$root/riscv/freestanding"
cd "$root/debs"
apt-get download gcc-11-riscv64-linux-gnu cpp-11-riscv64-linux-gnu binutils-riscv64-linux-gnu libgcc-11-dev-riscv64-cross libgcc-s1-riscv64-cross
for file in *.deb; do dpkg-deb -x "$file" "$root/riscv"; done
cp "$source_dir/freestanding/limits.h" "$root/riscv/freestanding/"
target="$root/riscv/usr/bin/riscv64-linux-gnu-gcc"
if [ -L "$target" ]; then rm "$target"; fi
cat > "$target" <<'EOF'
#!/bin/sh
gcc="$(dirname "$0")/riscv64-linux-gnu-gcc-11"
exec "$gcc" -ffreestanding -nostdinc -isystem "$(dirname "$0")/../../freestanding" -isystem "$("$gcc" -print-file-name=include)" "$@"
EOF
chmod +x "$target"
