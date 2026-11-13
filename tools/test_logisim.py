"""Run real Logisim, assert test summaries and independently check CPU traces."""
import argparse
from pathlib import Path
import re
import subprocess

root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument('--exe',default=r'D:\Logisim\logisim-evolution.exe')
args=p.parse_args()
logdir=root/'build'/'logisim-logs'
logdir.mkdir(parents=True,exist_ok=True)

def run(name,vector=False):
    cmd=[args.exe,'-o','en']
    if vector: cmd+=['-w',name,str(root/'logisim'/f'{name}.txt')]
    else: cmd+=['-t','table']
    cmd+=[str(root/'logisim'/f'{name}.circ')]
    r=subprocess.run(cmd,capture_output=True,timeout=40)
    text=r.stdout.decode('utf-8',errors='replace')
    err=r.stderr.decode('utf-8',errors='replace')
    (logdir/f'{name}.txt').write_text(text+'\n'+err,encoding='utf-8')
    assert r.returncode==0,(name,r.returncode,err,text[-1000:])
    if vector:
        match=re.search(r'Passed:\s*(\d+),\s*Failed:\s*(\d+)',text)
        assert match and int(match[2])==0,(name,text[-1000:])
        print(f'PASS {name}: {match[1]} vectors')
        return
    rows=[]
    for line in text.splitlines():
        fields=line.split('\t')
        if fields and all(re.fullmatch(r'[01 ]+',v) for v in fields):
            rows.append([int(v.replace(' ',''),2) for v in fields])
    assert rows,(name,text,err)
    return rows

for name in ['decoder24','encoder164','full_adder','mux4x3']: run(name,True)
rows=run('sum10')
assert rows==[[i,i*(i+1)//2] for i in range(11)],rows
print('PASS sum10: every state from 0 to 10; final sum 55')

program=[0x8b,0x91,0xa0,0xb1,0x29,0x17,0xd1,0xdf]
regs=[0]*4; pc=0; expected=[regs.copy()+[pc]]
for _ in range(100):
    instruction=program[pc]; opcode=instruction>>6
    dest=(instruction>>4)&3; src1=(instruction>>2)&3; src2=instruction&3
    nextpc=(pc+1)&15
    if opcode==0: regs[dest]=(regs[src1]+regs[src2])&255
    elif opcode==2: regs[dest]=instruction&15
    elif opcode==3 and regs[0]!=regs[src2]: nextpc=(instruction>>2)&15
    pc=nextpc; expected.append(regs.copy()+[pc])
    if pc==7: break
assert run('scpu')==expected
assert regs[2]==55
print(f'PASS scpu: all {len(expected)} architectural states, sum 55')

expected=[[0,0,0,0],[4,20,0,0],[16,20,8,0],[20,30,8,0],[8,30,8,0],[12,30,12,0]]
assert run('minirv2')==expected
print('PASS minirv2: all 6 call/return states, a0=30, ra=12, PC=12')
rows=run('minirv2_edges')
assert rows[-1]==[28,0,0,0,0,0xffffffff,0,0xfffff800,2047,28],rows[-1]
print('PASS minirv2_edges: negative immediates, wraparound, x0, JALR bit zero and rd==rs1')
print('ALL LOGISIM CHECKS PASSED')
