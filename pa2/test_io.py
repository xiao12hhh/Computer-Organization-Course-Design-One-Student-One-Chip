"""MMIO tests through compiled guest code, including injected SDL key events."""
from pathlib import Path
import os,subprocess
root=Path(__file__).resolve().parents[1];test=root/'pa2/io-test';build=root/'build';build.mkdir(exist_ok=True)
nemu=Path(os.environ['NEMU_HOME'])/'build/riscv32-nemu-interpreter';npc=root/'build/minirv-npc/npc'
subprocess.run(['cc','-shared','-fPIC',str(root/'pa2/test_sdl.c'),'-lSDL2','-lSDL2_image','-ldl','-o',str(build/'test-sdl.so')],check=True)
for arch,key in [('minirv-npc',False),('riscv32-nemu',False),('riscv32-nemu',True)]:
    subprocess.run(['make','-s','ARCH='+arch,'KEY_TEST='+str(int(key)),'image'],cwd=test,check=True)
    image=test/'build'/('course-'+('key' if key else 'io')+'-test-'+arch+'.bin')
    env=dict(os.environ,SDL_VIDEODRIVER='dummy')
    if key:env.update(COURSE_KEYS='1',LD_PRELOAD=str(build/'test-sdl.so'))
    cmd=[str(npc),str(image)] if arch=='minirv-npc' else [str(nemu),'-b',str(image)]
    r=subprocess.run(cmd,env=env,text=True,capture_output=True,timeout=20)
    text=r.stdout+r.stderr;(build/('io-'+arch+('-key' if key else '')+'.log')).write_text(text)
    assert r.returncode==0 and 'MMIO PASS' in text and 'HIT GOOD TRAP' in text,text[-2500:]
    if key:assert 'KEYBOARD PASS down/up' in text
    print('PASS MMIO',arch,'keyboard' if key else 'serial/timer/framebuffer where present')
