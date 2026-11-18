"""Download only the official minirv test inputs; never execute archive files."""
from pathlib import Path
import hashlib,tarfile,urllib.request
root=Path(__file__).resolve().parents[1]/'build'/'official-minirv'
root.mkdir(parents=True,exist_ok=True)
archive=root/'logisim-bin.tar.bz2'
if not archive.exists():
    urllib.request.urlretrieve('https://ysyx.oscc.cc/slides/resources/archive/logisim-bin.tar.bz2',archive)
digest=hashlib.sha256(archive.read_bytes()).hexdigest()
expected='b31639d38b8a1b6e866894d40947d928cf626dfd3bd50ec26402819bd0df4938'
if digest!=expected: raise SystemExit('Official archive changed; verify it before updating the pinned SHA256.')
with tarfile.open(archive) as tar:
    for name in ['mem.hex','mem.txt','sum.hex','sum.txt']:
        stream=tar.extractfile('logisim-bin/'+name)
        if stream is None: raise RuntimeError(name)
        (root/name).write_bytes(stream.read())
print('Official archive SHA256:',digest)
print(root)
