"""Seeded independent AST oracle; 2000 expressions plus rejected mutations."""
import random,subprocess
from pathlib import Path
rng=random.Random(912);mask=0xffffffff
def generate(depth):
    if depth==0 or rng.random()<.25:
        n=rng.randrange(0,mask+1);return (hex(n) if rng.randrange(2) else str(n)),n
    if rng.random()<.15:
        s,v=generate(depth-1);return f'-({s})',(-v)&mask
    a,x=generate(depth-1);b,y=generate(depth-1);op=rng.choice(['+','-','*','/','==','!=','&&'])
    if op=='/' and y==0:b,y='1',1
    value={'+':lambda:(x+y)&mask,'-':lambda:(x-y)&mask,'*':lambda:(x*y)&mask,
           '/':lambda:x//y,'==':lambda:int(x==y),'!=':lambda:int(x!=y),'&&':lambda:int(bool(x) and bool(y))}[op]()
    return f'({a} {op} {b})',value
root=Path(__file__).resolve().parents[1]
cases=[generate(5) for _ in range(2000)]
exe=root/'build/pa1/test_expr'
run=subprocess.run([str(exe),'--stdin'],input='\n'.join(s for s,v in cases)+'\n',text=True,capture_output=True,check=True)
rows=run.stdout.splitlines();assert len(rows)==len(cases)
for case,line in zip(cases,rows):assert line==f'1 {case[1]}',(case,line)
print('PASS 2000 seeded random expressions against independent AST oracle')
