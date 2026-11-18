from pathlib import Path
import random,struct,subprocess
root=Path(__file__).resolve().parents[2];build=root/'build/minirv-npc';exe=build/'npc'
def imm(rd,rs,v):return ((v&4095)<<20)|(rs<<15)|(rd<<7)|0x13
def load(rd,rs,offset,byte=False):return ((offset&4095)<<20)|(rs<<15)|((4 if byte else 2)<<12)|(rd<<7)|3
def store(rs,offset,byte=False):return (((offset&4095)>>5)<<25)|(rs<<20)|(1<<15)|((0 if byte else 2)<<12)|((offset&31)<<7)|0x23
def run(name,words,expected=0,args=()):
    path=build/(name+'.bin');path.write_bytes(struct.pack('<'+'I'*len(words),*words))
    r=subprocess.run([str(exe),'--diff','--max','10000',*args,str(path)],text=True,capture_output=True,timeout=20)
    (build/(name+'.log')).write_text(r.stdout+r.stderr)
    assert r.returncode==expected,(name,r.stdout,r.stderr)
    if name=='negative-bad-trap':assert 'HIT BAD TRAP' in r.stderr and 'ILLEGAL' not in r.stderr
    print('PASS',name)
rng=random.Random(1516)
words=[0x800100b7] # x1 = data base, outside the image
for rd in range(2,16):words.append(imm(rd,0,rng.randrange(-2048,2048)))
for _ in range(2500):
    rd=rng.randrange(2,16);rs=rng.randrange(2,16);kind=rng.randrange(7)
    if kind==0:words.append(imm(rd,rs,rng.randrange(-2048,2048)))
    elif kind==1:words.append((rng.randrange(2,16)<<20)|(rs<<15)|(rd<<7)|0x33)
    elif kind==2:words.append((rng.getrandbits(20)<<12)|(rd<<7)|0x37)
    elif kind==3:words.append(store(rs,rng.randrange(64)*4))
    elif kind==4:words.append(store(rs,rng.randrange(256),True))
    elif kind==5:words.append(load(rd,1,rng.randrange(64)*4))
    else:words.append(load(rd,1,rng.randrange(256),True))
words += [imm(0,2,42),imm(10,0,0),0x100073]
run('random-register-memory',words)
# JALR writes its link register after reading the old source, clears target bit 0.
run('jalr-alias',[0x800000b7,imm(1,1,17),(1<<15)|(1<<7)|0x67,0xffffffff,imm(10,0,0),0x100073])
run('bad-trap',[imm(10,0,7),0x100073],1)
run('negative-bad-trap',[imm(10,0,-1),0x100073],1)
run('invalid-high-register',[imm(17,0,1),0x100073],1)
run('invalid-multiply',[(1<<25)|(2<<20)|(1<<15)|(3<<7)|0x33],1)
run('misaligned-word',[0x800100b7,load(2,1,1)],1)
run('misaligned-jump',[0x800000b7,imm(1,1,2),(1<<15)|0x67],1)
run('out-of-range',[load(2,0,0)],1)
run('limit-is-not-pass',[(0<<15)|0x67],2,args=('--base','0'))
print('PASS strict 8-instruction/16-register RTL; register/PC/store comparison with independent C model')
