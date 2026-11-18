"""Run upstream am-tests' unmodified RTC test until three seconds are printed."""
from pathlib import Path
import os,subprocess,time
root=Path(__file__).resolve().parents[2];tests=Path.home()/'course-am-kernels/tests/am-tests'
build=root/'build/minirv-npc';log=build/'official-rtc.txt'
r=subprocess.run(['make','-s','ARCH=minirv-npc','mainargs=t','insert-arg'],cwd=tests,text=True,capture_output=True,timeout=180)
(build/'official-rtc-build.log').write_text(r.stdout+r.stderr)
assert r.returncode==0,r.stderr[-3000:]
with log.open('w') as out:
    p=subprocess.Popen([str(build/'npc'),'--max','0',str(tests/'build/amtest-minirv-npc.bin')],stdout=out,stderr=subprocess.STDOUT)
    try:
        deadline=time.monotonic()+40
        while time.monotonic()<deadline and p.poll() is None:
            text=log.read_text()
            if all(s in text for s in ['1 second).','2 seconds).','3 seconds).']):break
            time.sleep(.1)
        else:raise AssertionError(log.read_text()[-3000:])
    finally:
        if p.poll() is None:p.terminate();p.wait(timeout=5)
print('PASS official AM rtc_test printed seconds 1, 2, 3; intentionally stopped its infinite loop')
