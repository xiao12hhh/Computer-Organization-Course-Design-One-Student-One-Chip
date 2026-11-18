import os,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent/'demo'
subprocess.run(['make','-s','ARCH=riscv32-nemu','image'],cwd=root,check=True)
exe=Path(os.environ['NEMU_HOME'])/'build/riscv32-nemu-interpreter'
r=subprocess.run([str(exe),'-b',str(root/'build/course-week14-riscv32-nemu.bin')],text=True,capture_output=True,timeout=20)
out=r.stdout+r.stderr
(root/'build/run.log').write_text(out)
assert r.returncode==0 and 'HIT GOOD TRAP' in out and 'sum=5050; strings/format PASS' in out,out
print('PASS real RV32 AM: sum=5050, strings, sprintf/snprintf, serial printf, GOOD TRAP')
