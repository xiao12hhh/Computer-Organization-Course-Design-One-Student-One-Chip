"""Reproducible PA1 source count, reconstructing PA1 from our pinned patches.
Excludes build/ and third-party downloads; does not count PA2 decoder changes.
"""
from pathlib import Path
import subprocess,json,difflib,sys
repo=Path(sys.argv[1] if len(sys.argv)>1 else Path.home()/'course-nemu')
base='8e7a0fecc95b5b5d2c1f6be0ec1b703da93356c0'
def git(*args):return subprocess.check_output(['git','-C',str(repo),*args])
files=git('ls-tree','-r','--name-only',base).decode().splitlines()
files=[f for f in files if f.endswith(('.c','.h'))]
before={f:git('show',f'{base}:{f}').decode().splitlines() for f in files}
after=dict(before)
manifest=json.loads((repo/'.course-pa1-manifest.json').read_text())
for f in manifest:
    if f.endswith(('.c','.h')) and f!='src/isa/riscv32/inst.c' and 'course_rv32' not in f:
        after[f]=(repo/f).read_text().splitlines()
def stats(tree):return {'files':len(tree),'lines':sum(len(v) for v in tree.values()),'nonblank':sum(bool(l.strip()) for v in tree.values() for l in v)}
added=removed=0
for f in after:
    for op,i,j,k,l in difflib.SequenceMatcher(None,before.get(f,[]),after[f],autojunk=False).get_opcodes():
        if op in ('replace','delete'):removed+=j-i
        if op in ('replace','insert'):added+=l-k
print(json.dumps({'scope':'upstream tracked C/H plus PA1 additions, excluding PA2/build/dependencies','base':base,'before':stats(before),'after_pa1':stats(after),'added_lines':added,'removed_lines':removed,'net_lines':added-removed},indent=2))
