"""Independent byte-addressed ISA model and small instruction test program."""
MASK=0xffffffff
def sext(x,bits): return x-(1<<bits) if x>>(bits-1) else x
def i(op,rd,rs,imm,fn=0): return ((imm&4095)<<20)|(rs<<15)|(fn<<12)|(rd<<7)|op
def s(rs,data,imm,fn): return ((imm&0xfe0)<<20)|(data<<20)|(rs<<15)|(fn<<12)|((imm&31)<<7)|0x23
def demo():
    # All eight operations, four byte lanes, sign extension, x0, call/return.
    p=[i(0x13,1,0,256),0x12345137,i(0x13,2,2,0x678),s(1,2,0,2)]
    p += [i(3,3+k,1,k,4) for k in range(4)]
    for k,val in enumerate([0xef,0xcd,0xab,0x90]):
        p += [i(0x13,7,0,val),s(1,7,k,0)]
    p += [i(3,8,1,0,2),i(0x13,9,0,-1),(9<<20)|(7<<15)|(10<<7)|0x33,
          i(0x13,0,0,99),i(0x13,11,0,-2048),i(0x13,12,0,2047)]
    target=(len(p)+2)*4
    p += [i(0x13,13,0,target|1),i(0x67,13,13,0)]
    p += [i(0x67,0,0,len(p)*4)]
    return p
def read_hex(path):
    mem={}
    for line in path.read_text().splitlines()[1:]:
        if ':' not in line: continue
        addr,vals=line.split(':',1)
        for j,value in enumerate(vals.split()): mem[int(addr,16)+j]=int(value,16)
    return mem
class CPU:
    def __init__(self,words):
        self.words=dict(enumerate(words)) if isinstance(words,list) else words
        self.r=[0]*16; self.pc=0; self.mem=bytearray(1<<20)
        for a,w in self.words.items(): self.mem[4*a:4*a+4]=w.to_bytes(4,'little')
    def step(self):
        ins=self.words.get(self.pc//4,0); op=ins&127; rd=(ins>>7)&31
        fn=(ins>>12)&7; r1=(ins>>15)&31; r2=(ins>>20)&31
        nextpc=self.pc+4; val=None
        def reg(j):
            if j>=16: raise ValueError('RV32E register')
            return self.r[j]
        imm=sext(ins>>20,12)
        if op==0x37: val=ins&0xfffff000
        elif op==0x13 and fn==0: val=reg(r1)+imm
        elif op==0x33 and fn==0 and ins>>25==0: val=reg(r1)+reg(r2)
        elif op==0x67 and fn==0:
            nextpc=(reg(r1)+imm)&MASK&~1; val=self.pc+4
            if nextpc&3: raise ValueError('jump alignment')
        elif op==3 and fn in (2,4):
            addr=(reg(r1)+imm)&MASK; size=4 if fn==2 else 1
            if addr+size>len(self.mem) or addr%size: raise ValueError('load address')
            val=int.from_bytes(self.mem[addr:addr+size],'little')
        elif op==0x23 and fn in (0,2):
            imm=sext(((ins>>25)<<5)|rd,12); addr=(reg(r1)+imm)&MASK; size=4 if fn==2 else 1
            if addr+size>len(self.mem) or addr%size: raise ValueError('store address')
            self.mem[addr:addr+size]=(reg(r2)&((1<<(8*size))-1)).to_bytes(size,'little')
        else: raise ValueError(f'illegal instruction {ins:08x} at {self.pc:08x}')
        if val is not None:
            if rd>=16: raise ValueError('RV32E destination')
            if rd: self.r[rd]=val&MASK
        self.pc=nextpc&MASK
