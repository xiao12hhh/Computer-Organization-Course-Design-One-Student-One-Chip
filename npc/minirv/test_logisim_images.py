"""Run the same official mem/sum images as the earlier real Logisim tests."""
from pathlib import Path
import subprocess,struct,sys,re
root=Path(__file__).resolve().parents[2];sys.path.insert(0,str(root/'tools'))
from minirv_model import read_hex
subprocess.run([sys.executable,str(root/'tools/fetch_minirv_programs.py')],check=True)
for name in ['mem','sum']:
    source=root/'build/official-minirv';data=read_hex(source/(name+'.hex'))
    halt=int(re.search(r'^([0-9a-f]+) <halt>:',(source/(name+'.txt')).read_text(),re.M)[1],16)
    data[halt//4]=0x100073
    words=[data.get(i,0) for i in range(max(data)+1)]
    image=root/'build/minirv-npc'/(name+'-logisim.bin');image.write_bytes(struct.pack('<'+'I'*len(words),*words))
    r=subprocess.run([str(root/'build/minirv-npc/npc'),'--diff','--base','0',str(image)],text=True,capture_output=True,timeout=20)
    assert r.returncode==0 and 'HIT GOOD TRAP' in r.stderr,(name,r.stderr)
    print('PASS official Logisim image in RTL:',name,r.stderr.strip(),flush=True)
