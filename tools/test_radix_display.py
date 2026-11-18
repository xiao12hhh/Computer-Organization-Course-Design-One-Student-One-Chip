from pathlib import Path
import subprocess,re
import generate_processors as g
from generate_radix_display import build
root=Path(__file__).resolve().parents[1];exe=r'D:\Logisim\logisim-evolution.exe'
r=subprocess.run([exe,'-o','en','-w','radix_display',str(root/'logisim/radix_display.txt'),str(root/'logisim/radix_display.circ')],capture_output=True,timeout=60)
out=r.stdout.decode(errors='replace')
assert r.returncode==0 and re.search(r'Passed:\s*1024,\s*Failed:\s*0',out),(out,r.stderr)
print('PASS radix display: all 256 values in 4 bases')
g.OUT=root/'build'/'radix';g.OUT.mkdir(parents=True,exist_ok=True);build(True,True)
r=subprocess.run([exe,'-o','en','-t','table',str(g.OUT/'radix_counter_test.circ')],capture_output=True,timeout=60)
rows=[]
for line in r.stdout.decode(errors='replace').splitlines():
    fs=line.split('\t')
    if len(fs)==2 and all(re.fullmatch('[01 ]+',x) for x in fs):rows.append([int(x.replace(' ',''),2) for x in fs])
assert r.returncode==0 and rows==[[i,int(format(i,'08b'),16)] for i in range(256)],(rows[:3],rows[-3:],r.stderr)
print('PASS radix counter: all 256 binary display states')
