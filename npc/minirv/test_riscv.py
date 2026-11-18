from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[2];repo=Path.home()/'course-riscv-tests'
assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()=='676cbc7a4e520fca1c3d4dd1b586b2550769e02e'
build=root/'build/minirv-riscv-tests';build.mkdir(parents=True,exist_ok=True)
# Same exclusions as upstream: fence_i needs Zifencei, ma_data deliberately misaligns words.
tests=sorted(t for t in (repo/'isa/rv32ui').glob('*.S') if t.stem not in ['fence_i','ma_data'])
for t in tests:
    mf=build/('Makefile.'+t.stem)
    mf.write_text(f'NAME = {t.stem}\nSRCS = {t}\nINC_PATH += {repo}/env/p {repo}/isa/macros/scalar\ninclude $(AM_HOME)/Makefile\n')
    r=subprocess.run(['make','-s','-f',str(mf),'ARCH=minirv-npc','image'],cwd=build,text=True,capture_output=True,timeout=180)
    (build/(t.stem+'-build.log')).write_text(r.stdout+r.stderr)
    assert r.returncode==0,(t.stem,r.stderr[-2500:])
    r=subprocess.run([str(root/'build/minirv-npc/npc'),'--diff',str(build/'build'/(t.stem+'-minirv-npc.bin'))],text=True,capture_output=True,timeout=90)
    out=r.stdout+r.stderr;(build/(t.stem+'-run.log')).write_text(out)
    assert r.returncode==0 and 'HIT GOOD TRAP' in out,(t.stem,out)
    print('PASS riscv-tests -> minirv',t.stem,flush=True)
print('PASS',len(tests),'upstream RV32 I tests compiled down to eight instructions; M assembly is outside minirv translator support')
