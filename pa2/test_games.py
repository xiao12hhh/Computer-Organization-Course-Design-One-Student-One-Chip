"""Bounded real NES executions. --verify-only rechecks existing captured logs."""
from pathlib import Path
import os,subprocess,re,argparse
p=argparse.ArgumentParser();p.add_argument('--verify-only',action='store_true');args=p.parse_args()
root=Path(__file__).resolve().parents[1]
for mode,frames,arch in [('char',40,'minirv-npc'),('graphics',120,'riscv32-nemu')]:
    build=root/'build'/('litenes-'+mode+'-test')
    if not args.verify_only:
        subprocess.run(['python3',str(root/'pa2/prepare_litenes.py'),'--mode',mode,'--frames',str(frames)],check=True)
        subprocess.run(['make','-s','ARCH='+arch,'image'],cwd=build,check=True)
        image=build/'build'/('litenes-course-'+arch+'.bin')
        command=[str(root/'build/minirv-npc/npc'),'--max','4000000000',str(image)] if mode=='char' else [str(Path(os.environ['NEMU_HOME'])/'build/riscv32-nemu-interpreter'),'-b',str(image)]
        with (build/'run.txt').open('w') as out,(build/'stats.txt').open('w') as err:
            r=subprocess.run(command,stdout=out,stderr=err,env=dict(os.environ,SDL_VIDEODRIVER='dummy'),timeout=900)
            assert r.returncode==0,(mode,r.returncode)
    text=(build/'run.txt').read_text();stats=(build/'stats.txt').read_text() if (build/'stats.txt').exists() else ''
    observed=re.findall(r'NES_FRAME (\d+) HASH ([0-9a-f]+)',text)
    assert [int(f) for f,_ in observed]==list(range(2,frames+1,2)),mode
    assert len(set(h for _,h in observed))>1,mode
    assert 'HIT GOOD TRAP' in text+stats,mode
    print(f'PASS real {mode} LiteNES: {frames} emulated frames, {len(observed)} renders, {len(set(h for _,h in observed))} distinct framebuffer hashes')
