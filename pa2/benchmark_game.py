"""Measure 120 NES frames; fail if the selected mode misses the FPS target.

NEMU uses SDL dummy video to avoid display overhead. Native uses the real desktop.
Elapsed time includes process startup; renders are every second NES frame.
"""
from pathlib import Path
import argparse
import json
import os
import re
import subprocess
import time

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--min-fps', type=float, default=30)
parser.add_argument('--label', default='baseline')
parser.add_argument('--exe', type=Path)
parser.add_argument('--image', type=Path)
parser.add_argument('--native', action='store_true')
parser.add_argument('--compare', type=Path, help='JSON with 60 expected framebuffer hashes')
args = parser.parse_args()
if not re.fullmatch(r'[a-zA-Z0-9_-]+', args.label):
    parser.error('--label must contain only letters, digits, underscores or hyphens')
root = Path(__file__).resolve().parents[1]
out = root / 'build/performance'
out.mkdir(parents=True, exist_ok=True)
exe = args.exe or (
    root / 'build/litenes-graphics-test/build/litenes-course-native.elf'
    if args.native else Path.home() / 'course-nemu/build/riscv32-nemu-interpreter')
image = args.image or root / 'build/litenes-graphics-test/build/litenes-course-riscv32-nemu.bin'
command = [str(exe)] if args.native else [str(exe), '-b', str(image)]
env = os.environ.copy() if args.native else dict(os.environ, SDL_VIDEODRIVER='dummy')
start = time.monotonic()
run = subprocess.run(command, env=env, text=True, capture_output=True, timeout=120)
elapsed = time.monotonic() - start
text = run.stdout + run.stderr
(out / (args.label + '.log')).write_text(text)
frames = re.findall(r'NES_FRAME (\d+) HASH ([0-9a-f]+)', text)
success = 'Exit code = 00h' if args.native else 'HIT GOOD TRAP'
assert run.returncode == 0 and success in text, (run.returncode, text[-2000:])
if frames:
    assert [int(f) for f, _ in frames] == list(range(2, 121, 2))
else:
    assert 'NES_DONE 120' in text, 'Expected a bounded 120-frame run'
result = {
    'label': args.label, 'frames': 120, 'elapsed_seconds': elapsed,
    'emulated_fps': 120 / elapsed, 'rendered_fps': 60 / elapsed,
    'frame_hashes': frames, 'target_fps': args.min_fps,
    'meets_min_fps': 120 / elapsed >= args.min_fps,
}
(out / (args.label + '.json')).write_text(json.dumps(result, indent=2) + '\n')
print(f'{args.label}: 120 NES frames in {elapsed:.2f}s = '
      f'{120 / elapsed:.2f} emulated FPS; target >= {args.min_fps:.0f}')
if args.compare:
    expected = json.loads(args.compare.read_text())['frame_hashes']
    assert len(frames) == 60 and [list(f) for f in frames] == expected, 'Framebuffer hashes differ'
    print('PASS: all 60 framebuffer hashes match', args.compare)
assert result['meets_min_fps'], 'Frame rate below playable target'
