"""Exercise the actual native launcher with timed SDL start/move/jump/quit events."""
from pathlib import Path
import hashlib
import os
import re
import subprocess

root = Path(__file__).resolve().parents[1]
out = root / 'build/performance'
out.mkdir(parents=True, exist_ok=True)
hook = out / 'native-input.so'
subprocess.run(['cc', '-shared', '-fPIC', str(root / 'pa2/test_native_sdl.c'),
                '-lSDL2', '-lSDL2_image', '-ldl', '-o', str(hook)], check=True)
prefix = out / 'native'
images = [out / ('native-' + name + '.png') for name in ('title', 'playing')]
for path in images:
    path.unlink(missing_ok=True)
result = subprocess.run(['bash', 'tools/run-week16.sh', 'fast'], cwd=root,
    env=dict(os.environ, LD_PRELOAD=str(hook), COURSE_NATIVE_CAPTURE=str(prefix)),
    text=True, capture_output=True, timeout=15)
text = result.stdout + result.stderr
(out / 'native-input.log').write_text(text)
assert result.returncode == 0 and 'Exit code = 00h' in text, text[-2000:]
fps = [int(n) for n in re.findall(r'FPS = (\d+)', text)]
assert len(fps) >= 3 and min(fps[1:]) >= 30, fps
assert all(path.exists() for path in images)
assert hashlib.sha256(images[0].read_bytes()).digest() != hashlib.sha256(images[1].read_bytes()).digest()
print('PASS native launcher: start/move/jump events, changing screenshots, SDL quit; FPS:', fps)
