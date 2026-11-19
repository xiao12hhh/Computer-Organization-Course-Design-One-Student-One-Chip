"""Build a local derivative of pinned LiteNES; ROM stays in ignored build output.
Only the renderer and a bounded test exit are changed; NES CPU/PPU/ROM are upstream.
"""
from pathlib import Path
import argparse,shutil,subprocess
p=argparse.ArgumentParser();p.add_argument('--mode',choices=['char','graphics'],default='char');p.add_argument('--frames',type=int,default=0);p.add_argument('--no-frame-hashes',action='store_true');a=p.parse_args()
repo=Path.home()/'course-am-kernels';base='9c433f7cf4b4e05d09543bf7e269b23502d1b2b6'
assert subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()==base
root=Path(__file__).resolve().parents[1];out=root/'build'/('litenes-'+a.mode+('-test' if a.frames else '')+('-quiet' if a.no_frame_hashes else ''))
out.mkdir(parents=True,exist_ok=True)
shutil.copytree(repo/'kernels/litenes/src',out/'src',dirs_exist_ok=True)
f=out/'src/fce.c';code=f.read_text()
marker='  AM_GPU_CONFIG_T cfg = io_read(AM_GPU_CONFIG);'
assert code.count(marker)==1
replacement='''#ifdef COURSE_FRAME_HASHES
  uint32_t digest=2166136261u;
  for (int k=0;k<SCR_W*SCR_H;k++) digest=(digest^canvas[k])*16777619u;
#endif
#ifdef COURSE_CHARACTER
  // Downsample the actual PPU framebuffer to 64x30 terminal characters.
  static const char shades[]=" .:-=+*#%@";
  printf("\\033[H");
  for(int y=0;y<SCR_H;y+=8) {
    for(int x=0;x<SCR_W;x+=4) {
      uint32_t c=canvas[y*SCR_W+x];
      unsigned l=(((c>>16)&255)*3+((c>>8)&255)*6+(c&255))/10;
      putch(shades[l*9/255]);
    }
    putch('\\n');
  }
#else
'''+marker
code=code.replace(marker,replacement)
end='  io_write(AM_GPU_FBDRAW, xpad, ypad, canvas, SCR_W, SCR_H, true);'
code=code.replace(end,end+'''\n#endif
#ifdef COURSE_FRAME_HASHES
  printf("NES_FRAME %d HASH %08x\\n",frame_cnt,digest);
#endif
  if(COURSE_FRAME_LIMIT && frame_cnt>=COURSE_FRAME_LIMIT) {
    printf("NES_DONE %d\\n",frame_cnt);
    halt(0);
  }''')
f.write_text(code)
(out/'Makefile').write_text(f'NAME = litenes-course\nSRCS = $(shell find src -name "*.c")\nCFLAGS += -DCOURSE_FRAME_LIMIT={a.frames} '+('-DCOURSE_CHARACTER ' if a.mode=='char' else '')+('-DCOURSE_FRAME_HASHES' if a.frames and not a.no_frame_hashes else '')+'\ninclude $(AM_HOME)/Makefile\n')
print(out)
