"""Compare every architectural state of actual Logisim against an ISA model."""
from pathlib import Path
import argparse,subprocess,re,sys
import generate_processors as g
from generate_minirv import build
from minirv_model import CPU,demo,read_hex
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--exe',default=r'D:\Logisim\logisim-evolution.exe');args=p.parse_args()
g.OUT=root/'build'/'minirv-logisim';g.OUT.mkdir(parents=True,exist_ok=True)
official=root/'build'/'official-minirv'
for name in ['demo','mem','sum']:
    cycles=64 if name=='demo' else 6000
    data=dict(enumerate(demo())) if name=='demo' else read_hex(official/(name+'.hex'))
    words=[data.get(k,0) for k in range(max(data)+1)]
    build('minirv_'+name,words,cycles)
    cmd=[args.exe,'-o','en','-t','table']
    if name!='demo': cmd+=['-l',str(official/(name+'.hex'))]
    cmd+=[str(g.OUT/('minirv_'+name+'.circ'))]
    r=subprocess.run(cmd,capture_output=True,timeout=180)
    output=r.stdout.decode(errors='replace');err=r.stderr.decode(errors='replace')
    (g.OUT/(name+'.log')).write_text(output+'\n'+err,encoding='utf-8')
    assert r.returncode==0,(name,r.returncode,err)
    rows=[]
    for line in output.splitlines():
        fields=line.split('\t')
        if len(fields)==19 and all(re.fullmatch('[01 ]+',v) for v in fields):
            rows.append([int(v.replace(' ',''),2) for v in fields])
    assert len(rows)==cycles+1,(name,len(rows),output[:1000],err)
    model=CPU(words)
    for step,row in enumerate(rows):
        expected=[model.pc]+model.r+[0,step]
        assert row==expected,(name,step,row,expected)
        if step<cycles:model.step()
    if name=='demo': assert model.r[8]==0x90abcdef and model.r[10]==143
    else:
        text=(official/(name+'.txt')).read_text()
        halt=int(re.search(r'^([0-9a-f]+) <halt>:',text,re.M)[1],16)
        assert model.r[10]==0 and model.pc in (halt,halt+4),(name,model.pc,halt,model.r[10])
    print(f'PASS Logisim {name}: {len(rows)} states match; PC=0x{model.pc:x}, a0={model.r[10]}',flush=True)
