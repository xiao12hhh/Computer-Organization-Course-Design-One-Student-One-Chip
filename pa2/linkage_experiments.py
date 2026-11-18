"""PA2 header/linkage experiments in a disposable copy, never the working NEMU."""
from pathlib import Path
import os,subprocess,shutil,tempfile,json
source=Path.home()/'course-nemu';out=Path(__file__).resolve().parents[1]/'build/linkage';out.mkdir(parents=True,exist_ok=True)
results={}
with tempfile.TemporaryDirectory(prefix='course-linkage-') as temp:
    repo=Path(temp)/'nemu';shutil.copytree(source,repo,ignore=shutil.ignore_patterns('.git','build'))
    env=dict(os.environ,NEMU_HOME=str(repo))
    subprocess.run(['make','-s','-C',str(repo/'tools/fixdep')],env=env,check=True)
    common=repo/'include/common.h';debug=repo/'include/debug.h';fetch=repo/'include/cpu/ifetch.h'
    c0=common.read_text();d0=debug.read_text();f0=fetch.read_text()
    def build(name):
        r=subprocess.run(['make','-s','-j2'],cwd=repo,env=env,text=True,capture_output=True,timeout=120)
        (out/(name+'.log')).write_text(r.stdout+r.stderr)
        result={'build_ok':r.returncode==0}
        if r.returncode==0:
            syms=subprocess.check_output(['nm','-a',str(repo/'build/riscv32-nemu-interpreter')],text=True)
            result['dummy_entities']=sum(line.split()[-1:] == ['dummy'] for line in syms.splitlines())
        else:result['diagnostic']='\n'.join(line for line in r.stderr.splitlines() if 'error:' in line or 'undefined reference' in line or 'multiple definition' in line)[:1000]
        results[name]=result;print(name,result,flush=True);return r.returncode
    common.write_text(c0.replace('#define __COMMON_H__','#define __COMMON_H__\nvolatile static int dummy;'))
    assert build('dummy-common')==0
    debug.write_text(d0.replace('#define __DEBUG_H__','#define __DEBUG_H__\nvolatile static int dummy;'))
    assert build('dummy-both-tentative')==0
    common.write_text(common.read_text().replace('int dummy;','int dummy = 0;'))
    debug.write_text(debug.read_text().replace('int dummy;','int dummy = 0;'))
    assert build('dummy-both-initialized')!=0
    common.write_text(c0);debug.write_text(d0)
    for name,prefix in [('fetch-no-static','inline'),('fetch-no-inline','static'),('fetch-neither','')]:
        fetch.write_text(f0.replace('static inline uint32_t',prefix+' uint32_t'));build(name)
    # Contrast C11 inline linkage at O0 with two translation units, isolated from NEMU.
    a=Path(temp)/'a.c';b=Path(temp)/'b.c';h=Path(temp)/'h.h'
    a.write_text('#include "h.h"\nint main(void){return plus(1);}\n')
    b.write_text('#include "h.h"\nint other(void){return plus(2);}\n')
    for label,prefix in [('static-inline','static inline'),('inline','inline'),('static','static'),('external','')]:
        h.write_text(prefix+' int plus(int x){return x+1;}\n')
        r=subprocess.run(['cc','-std=c11','-O0',str(a),str(b),'-o',str(Path(temp)/'a.out')],text=True,capture_output=True)
        results['two-tu-'+label]={'build_ok':r.returncode==0,'diagnostic':r.stderr[-1200:]}
(out/'results.json').write_text(json.dumps(results,indent=2)+'\n')
print(out/'results.json')
