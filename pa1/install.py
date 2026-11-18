"""Apply our PA1 files to a pinned upstream checkout, preserving user edits."""
from pathlib import Path
import argparse,subprocess,json,hashlib
BASE='8e7a0fecc95b5b5d2c1f6be0ec1b703da93356c0'
p=argparse.ArgumentParser();p.add_argument('nemu',type=Path);p.add_argument('--rv32im',action='store_true');args=p.parse_args()
dest=args.nemu.resolve();src=Path(__file__).resolve().parent
head=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()
if head!=BASE:raise SystemExit(f'Expected NEMU ics2024 {BASE}, got {head}')
mapping={'nemu-expr.c':'src/monitor/sdb/expr.c','nemu-sdb.c':'src/monitor/sdb/sdb.c',
 'nemu-reg.c':'src/isa/riscv32/reg.c','expr.c':'src/monitor/sdb/course_expr.c','expr.h':'src/monitor/sdb/course_expr.h',
 '@monitor':'src/monitor/monitor.c','nemu-watchpoint.c':'src/monitor/sdb/watchpoint.c',
 '@cpu':'src/cpu/cpu-exec.c'}
if args.rv32im:
    mapping.update({'../pa2/nemu-inst.c':'src/isa/riscv32/inst.c',
      '../pa2/rv32.c':'src/isa/riscv32/course_rv32.c','../pa2/rv32.h':'src/isa/riscv32/course_rv32.h'})
manifest=dest/'.course-pa1-manifest.json'
old=json.loads(manifest.read_text()) if manifest.exists() else {}
pending=[]
for source,target in mapping.items():
    if source=='@cpu':
        content=subprocess.check_output(['git','-C',str(dest),'show',f'{BASE}:{target}'])
        marker=b'  IFDEF(CONFIG_DIFFTEST, difftest_step(_this->pc, dnpc));\n'
        assert content.count(marker)==1
        content=content.replace(marker,marker+b'  extern void course_watch_check(void);\n  course_watch_check();\n')
    elif source=='@monitor':
        content=subprocess.check_output(['git','-C',str(dest),'show',f'{BASE}:{target}'])
        exercise=b'  Log("Exercise: Please remove me in the source code and compile NEMU again.");\n  assert(0);\n'
        assert content.count(exercise)==1
        content=content.replace(exercise,b'  /* PA0 startup exercise completed; enter the debugger. */\n')
    else:
        content=(src/source).read_bytes().replace(b'\r\n',b'\n')
    if source=='expr.c':content=content.replace(b'"expr.h"',b'"course_expr.h"')
    if source=='../pa2/rv32.c':content=content.replace(b'"rv32.h"',b'"course_rv32.h"')
    file=dest/target
    if file.exists() and file.read_bytes()!=content:
        current=file.read_bytes()
        upstream=subprocess.run(['git','-C',str(dest),'show',f'{BASE}:{target}'],capture_output=True)
        if current!=upstream.stdout and hashlib.sha256(current).hexdigest()!=old.get(target):
            raise SystemExit(f'Preserving user changes: {file}')
    pending.append((file,target,content))
for file,target,content in pending:
    file.write_bytes(content);old[target]=hashlib.sha256(content).hexdigest()
manifest.write_text(json.dumps(old,indent=2)+'\n')
config=dest/'configs/course_pa1_defconfig'
config.write_text('CONFIG_ISA_riscv=y\n# CONFIG_RV64 is not set\nCONFIG_TARGET_NATIVE_ELF=y\n# CONFIG_TRACE is not set\n# CONFIG_DEVICE is not set\nCONFIG_CC_DEBUG=y\n')
print('Installed PA1 debugger and evaluator into',dest)
