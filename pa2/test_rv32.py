"""Independent Python integer oracle for register ALU/M and immediate operations."""
import ctypes as C,random,subprocess
from pathlib import Path
root=Path(__file__).resolve().parent;b=root/'build';b.mkdir(exist_ok=True)
subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-shared','-fPIC','-fsanitize=undefined','-fno-sanitize-recover=all',str(root/'rv32.c'),'-o',str(b/'rv32.so')],check=True)
lib=C.CDLL(str(b/'rv32.so'));fn=lib.rv32_execute
readtype=C.CFUNCTYPE(C.c_uint32,C.c_uint32,C.c_int);writetype=C.CFUNCTYPE(None,C.c_uint32,C.c_int,C.c_uint32)
fn.argtypes=[C.c_uint32,C.c_uint32,C.POINTER(C.c_uint32),C.POINTER(C.c_uint32),readtype,writetype]
memory=bytearray(256)
@readtype
def read(a,n):return int.from_bytes(memory[a:a+n],'little')
@writetype
def write(a,n,v):memory[a:a+n]=(v&((1<<(n*8))-1)).to_bytes(n,'little')
mask=2**32-1
def signed(a):return a if a<2**31 else a-2**32
count=0
def check(i,a,b,expected,rd=3,pc=0x80000000):
    global count
    regs=(C.c_uint32*32)();regs[1]=a;regs[2]=b;nextpc=C.c_uint32()
    assert fn(i,pc,regs,C.byref(nextpc),read,write)==0,hex(i)
    assert regs[rd]==(expected&mask),(hex(i),hex(a),hex(b),hex(regs[rd]),hex(expected&mask))
    assert regs[0]==0;count+=1
    return nextpc.value,regs
edge=[0,1,2,31,32,0x7fffffff,0x80000000,0xfffffffe,0xffffffff]
rng=random.Random(1314)
pairs=[(a,b) for a in edge for b in edge]+[(rng.getrandbits(32),rng.getrandbits(32)) for _ in range(2000)]
for a,b in pairs:
    sa,sb=signed(a),signed(b);q=abs(sa)//abs(sb) if b else 0
    if (sa<0)!=(sb<0):q=-q
    values=[a*b,(sa*sb)>>32,(sa*b)>>32,(a*b)>>32,q if b else -1,a//b if b else mask,sa-q*sb if b else a,a%b if b else a]
    for f,v in enumerate(values):check((1<<25)|(2<<20)|(1<<15)|(f<<12)|(3<<7)|0x33,a,b,v)
    vals=[a+b,a<<(b&31),int(sa<sb),int(a<b),a^b,a>>(b&31),a|b,a&b]
    for f,v in enumerate(vals):check((2<<20)|(1<<15)|(f<<12)|(3<<7)|0x33,a,b,v)
    check((32<<25)|(2<<20)|(1<<15)|(3<<7)|0x33,a,b,a-b)
    check((32<<25)|(2<<20)|(1<<15)|(5<<12)|(3<<7)|0x33,a,b,sa>>(b&31))
for imm in [-2048,-1,0,1,2047]:
    for a in edge:
        for f,v in [(0,a+imm),(2,int(signed(a)<imm)),(3,int(a<(imm&mask))),(4,a^(imm&mask)),(6,a|(imm&mask)),(7,a&(imm&mask))]:
            check(((imm&4095)<<20)|(1<<15)|(f<<12)|(3<<7)|0x13,a,0,v)
for a in edge:
    for sh in range(32):
        for f,hi,v in [(1,0,a<<sh),(5,0,a>>sh),(5,32,signed(a)>>sh)]:
            check((hi<<25)|(sh<<20)|(1<<15)|(f<<12)|(3<<7)|0x13,a,0,v)
# Signed/unsigned loads, stores, x0, JALR rd==rs1 and bit-zero clearing.
memory[64:68]=bytes([0x80,0xff,0xff,0x80])
for f,v in [(0,-128),(1,-128),(2,0x80ffff80),(4,128),(5,65408)]:check((1<<15)|(f<<12)|(3<<7)|3,64,0,v)
for f,n in [(0,1),(1,2),(2,4)]:
    check((2<<20)|(1<<15)|(f<<12)|0x23,80,0x89abcdef,0)
    assert int.from_bytes(memory[80:80+n],'little')==0x89abcdef&((1<<(8*n))-1)
check((1<<20)|(1<<15)|0x13,8,0,0,rd=0)
nextpc,regs=check((1<<15)|(1<<7)|0x67,0x1001,0,0x80000004,rd=1)
assert nextpc==0x1000
print('PASS RV32 oracle:',count,'cases, including M arithmetic edges; UBSan enabled')
