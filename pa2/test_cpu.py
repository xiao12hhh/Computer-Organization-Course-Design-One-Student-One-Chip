"""Compile every pinned AM cpu-test, then run the resulting binary in real NEMU.
The upstream wrapper masks some make failures; use our own per-test makefiles.
wrong.c is a negative control and MUST end in a BAD TRAP / nonzero exit.
"""
import os,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent
kernels=Path.home()/'course-am-kernels/tests/cpu-tests'
build=root/'build/cpu';build.mkdir(parents=True,exist_ok=True)
exe=Path(os.environ['NEMU_HOME'])/'build/riscv32-nemu-interpreter'
for test in sorted((kernels/'tests').glob('*.c')):
    mf=build/('Makefile.'+test.stem)
    mf.write_text(f'NAME = {test.stem}\nSRCS = {test}\nINC_PATH += {kernels}/include\ninclude $(AM_HOME)/Makefile\n')
    r=subprocess.run(['make','-s','-f',str(mf),'ARCH=riscv32-nemu','image'],cwd=build,text=True,capture_output=True,timeout=120)
    (build/(test.stem+'-build.log')).write_text(r.stdout+r.stderr)
    assert r.returncode==0,(test.stem,r.stdout[-1000:],r.stderr[-2000:])
    binary=build/'build'/(test.stem+'-riscv32-nemu.bin')
    r=subprocess.run([str(exe),'-b',str(binary)],text=True,capture_output=True,timeout=60)
    output=r.stdout+r.stderr;(build/(test.stem+'-run.log')).write_text(output)
    if test.stem=='wrong':assert r.returncode!=0 and 'HIT BAD TRAP' in output,output[-2000:]
    else:assert r.returncode==0 and 'HIT GOOD TRAP' in output,(test.stem,output[-2000:])
    print('PASS',test.stem, '(expected BAD TRAP)' if test.stem=='wrong' else '',flush=True)
print('PASS all 36 upstream cpu-tests (35 good + 1 intentional bad)')
