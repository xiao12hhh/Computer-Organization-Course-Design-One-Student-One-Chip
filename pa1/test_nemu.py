"""Integration checks against the real pinned riscv32 NEMU executable."""
from pathlib import Path
import re,subprocess,argparse
p=argparse.ArgumentParser();p.add_argument('--nemu',type=Path,default=Path.home()/'course-nemu/build/riscv32-nemu-interpreter');args=p.parse_args()
commands=['p $pc','p $0 + $zero + $x0','p 1+2*3','p *0x80000000',
 'x 2 $pc','si','p $pc','p $t0','p $x5','info r','si 0','si -1','si 1 junk',
 'p $pc','p 0 && *0','p 1 / 0','p $no_such_register','p *0xffffffff',
 'x 2 0xfffffffc','x 0 $pc','x 1025 $pc','si 2','p $pc','p $a0',
 'x 1 0x80000010','p *0x80000010','  p   (8 - 3) * 2','c','q']
r=subprocess.run([str(args.nemu)],input='\n'.join(commands)+'\n',text=True,capture_output=True,timeout=30)
out=re.sub(r'\x1b\[[0-9;]*m','',r.stdout+r.stderr)
log=Path(__file__).resolve().parents[1]/'build/pa1/nemu-integration.log';log.parent.mkdir(parents=True,exist_ok=True);log.write_text(out)
assert r.returncode==0,(r.returncode,out[-3000:])
values=[int(x) for x in re.findall(r'^= (\d+) \(0x[0-9a-f]+\)$',out,re.M)]
expected=[0x80000000,0,7,0x297,0x80000004,0x80000000,0x80000000,0x80000004,0,0x8000000c,0,0xdeadbe00,10]
assert values==expected,(values,expected,out)
assert '0x80000000: 0x00000297' in out and '0x80000004: 0x00028823' in out
assert '0x80000010: 0xdeadbe00' in out
assert out.count('Invalid expression\n')==3
assert 'Invalid expression or memory range' in out
assert 'HIT GOOD TRAP' in out
assert len(re.findall(r'^x\d+\s+\S+\s+0x',out,re.M))==32
print('PASS real NEMU: si/info r/x/p/c/q, aliases, memory updates, malformed args, bad ranges; built-in GOOD TRAP')
