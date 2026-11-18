from pathlib import Path
import subprocess,re
exe=Path.home()/'course-nemu/build/riscv32-nemu-interpreter'
def run(commands):
    r=subprocess.run([str(exe)],input='\n'.join(commands)+'\n',text=True,capture_output=True,timeout=15)
    assert r.returncode==0,(r.returncode,r.stdout,r.stderr)
    return re.sub(r'\x1b\[[0-9;]*m','',r.stdout+r.stderr)
out=run(['w $t0','w *0x80000010','w $pc == 0x80000008','c','p $pc','c','p $pc','info w','d 0','d 1','d 2','c','q'])
assert 'Watchpoint 0 changed' in out and 'Watchpoint 1 changed' in out and 'Watchpoint 2 changed' in out
assert '= 2147483652 (0x80000004)' in out and '= 2147483656 (0x80000008)' in out
assert 'HIT GOOD TRAP' in out
out=run(['w 1']*32+['w 2','info w','d 0','d 0','d 31','w $pc','info w','q'])
assert 'pool exhausted' in out and 'No such watchpoint' in out and 'Watchpoint 31: $pc' in out
out=run(['w 1/0','w *0','w $pc','si 3','c','c','c','c','q'])
assert out.count('Invalid watch expression')==2
assert 'HIT GOOD TRAP' in out and 'Program execution has ended' in out
# Valid at creation, invalid after AUIPC changes t0 to 0x80000000.
out=run(['w *(0x80000000 + $t0)','c','p $pc','d 0','c','q'])
assert 'evaluation failed' in out and '= 2147483652 (0x80000004)' in out and 'HIT GOOD TRAP' in out
print('PASS watchpoints: register/memory/PC, simultaneous triggers, 32-slot exhaustion, deletion/reuse, evaluation errors, terminal state preserved')
