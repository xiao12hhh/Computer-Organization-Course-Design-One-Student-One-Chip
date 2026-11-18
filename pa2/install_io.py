"""Install week 15/16 platform drivers without overwriting unknown edits."""
from pathlib import Path
import subprocess,json,hashlib
here=Path(__file__).resolve().parent
def install(repo,base,patches):
    assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==base
    mf=repo/'.course-io-manifest.json';old=json.loads(mf.read_text()) if mf.exists() else {};pending=[]
    for target,source in patches.items():
        upstream=subprocess.check_output(['git','-C',str(repo),'show',base+':'+target])
        if source=='@npc-make':content=upstream.replace(b'\techo "TODO: add command here to run simulation"',b'\t$(NPC_BIN) $(NPC_ARGS) $(IMAGE).bin').replace(b'@python ',b'@python3 ')
        elif source=='@python3':content=upstream.replace(b'@python ',b'@python3 ')
        elif source=='@vga':
            marker=b'  // TODO: call `update_screen()` when the sync register is non-zero,\n  // then zero out the sync register'
            assert upstream.count(marker)==1
            content=upstream.replace(marker,b'  if (vgactl_port_base[1]) {\n    IFDEF(CONFIG_VGA_SHOW_SCREEN, update_screen());\n    vgactl_port_base[1] = 0;\n  }')
        else:content=(here/source).read_bytes().replace(b'\r\n',b'\n')
        path=repo/target;current=path.read_bytes()
        if current not in (upstream,content) and hashlib.sha256(current).hexdigest()!=old.get(target):raise SystemExit('Preserving user changes: '+str(path))
        pending.append((path,target,content))
    for path,target,content in pending:path.write_bytes(content);old[target]=hashlib.sha256(content).hexdigest()
    mf.write_text(json.dumps(old,indent=2)+'\n')
install(Path.home()/'course-am','9bc0a93c52c928a6de970f39a507be94cfb63a9f',{
 'am/src/platform/nemu/ioe/timer.c':'io/timer.c','am/src/platform/nemu/ioe/input.c':'io/input.c',
 'am/src/platform/nemu/ioe/gpu.c':'io/gpu.c','am/src/riscv/npc/timer.c':'io/timer.c',
 'am/src/riscv/npc/trm.c':'io/npc-trm.c','scripts/platform/npc.mk':'@npc-make',
 'scripts/platform/nemu.mk':'@python3'})
install(Path.home()/'course-nemu','8e7a0fecc95b5b5d2c1f6be0ec1b703da93356c0',{'src/device/vga.c':'@vga'})
print('Installed AM/NEMU I/O and NPC runtime')
