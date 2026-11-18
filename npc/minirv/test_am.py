"""Build official cpu-tests for actual minirv, run in RTL, verify both trap classes."""
import os,subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[2];build=root/'build/minirv-am';build.mkdir(parents=True,exist_ok=True)
kernels=Path.home()/'course-am-kernels/tests/cpu-tests';exe=root/'build/minirv-npc/npc'
tests=sorted((kernels/'tests').glob('*.c'))
for test in tests:
    mf=build/('Makefile.'+test.stem)
    mf.write_text(f'NAME = {test.stem}\nSRCS = {test}\nINC_PATH += {kernels}/include\ninclude $(AM_HOME)/Makefile\n')
    r=subprocess.run(['make','-s','-f',str(mf),'ARCH=minirv-npc','image'],cwd=build,text=True,capture_output=True,timeout=180)
    (build/(test.stem+'-build.log')).write_text(r.stdout+r.stderr)
    assert r.returncode==0,(test.stem,r.stdout[-1500:],r.stderr[-3000:])
    image=build/'build'/(test.stem+'-minirv-npc.bin')
    r=subprocess.run([str(exe),'--diff','--quiet',str(image)],text=True,capture_output=True,timeout=120)
    out=r.stdout+r.stderr;(build/(test.stem+'-run.log')).write_text(out)
    if test.stem=='wrong':assert r.returncode==1 and 'HIT BAD TRAP' in out,(test.stem,out)
    else:assert r.returncode==0 and 'HIT GOOD TRAP' in out,(test.stem,out)
    print('PASS minirv AM',test.stem,flush=True)
print('PASS minirv cpu-tests: 35 GOOD TRAP + 1 expected BAD TRAP, full instruction comparison')
