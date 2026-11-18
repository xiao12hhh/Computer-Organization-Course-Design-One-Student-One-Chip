"""Install the course klib implementations; preserve upstream scanning code and user edits."""
from pathlib import Path
import subprocess,hashlib,json,sys
BASE='9bc0a93c52c928a6de970f39a507be94cfb63a9f'
dest=Path(sys.argv[1]).resolve();src=Path(__file__).resolve().parent/'klib'
assert subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()==BASE
manifest=dest/'.course-klib-manifest.json'
old=json.loads(manifest.read_text()) if manifest.exists() else {};pending=[]
for name in ['string.c','stdio.c']:
    target='klib/src/'+name
    upstream=subprocess.check_output(['git','-C',str(dest),'show',f'{BASE}:{target}'])
    if name=='string.c':content=(src/name).read_bytes().replace(b'\r\n',b'\n')
    else:
        tail=upstream[upstream.index(b'int __am_vsscanf_internal'):]
        content=(src/'format.c').read_bytes().replace(b'\r\n',b'\n')+b'\n#if !defined(__ISA_NATIVE__) || defined(__NATIVE_USE_KLIB__)\n'+tail
    file=dest/target;current=file.read_bytes()
    if current not in [upstream,content] and hashlib.sha256(current).hexdigest()!=old.get(target):raise SystemExit('Preserving user changes: '+str(file))
    pending.append((file,target,content))
for file,target,content in pending:file.write_bytes(content);old[target]=hashlib.sha256(content).hexdigest()
manifest.write_text(json.dumps(old,indent=2)+'\n')
print('Installed course klib in',dest)
