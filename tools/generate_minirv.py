"""Generate a complete eight-instruction Logisim minirv datapath.

ROM/RAM are 1 MiB each, byte addressed by the ISA, little endian. Only aligned
word accesses are supported; bad instructions/addresses halt without a write.
"""
import argparse
from pathlib import Path
import generate_processors as g
from minirv_model import demo,read_hex

def join(n,parts):
    widths=[n.widths[x] for x in parts]; out=n.new(sum(widths)); attrs={'incoming':sum(widths),'fanout':len(parts),'appear':'right','facing':'east'}
    bit=0
    for group,w in enumerate(widths):
        for _ in range(w): attrs['bit'+str(bit)]=group; bit+=1
    n.cell(0,'Splitter',attrs,[(0,0,out)]+[(20,10+10*i,p) for i,p in enumerate(parts)])
    return out

def build(name,words,cycles=6000):
    n=g.Netlist(name); clk,rst=g.clock(n); zero=n.const(32,0); on=n.const(1,1)
    pc=n.new(32,'PC'); regs=[zero]+[n.new(32,f'x{i}') for i in range(1,16)]
    low,addr,high=n.split(pc,[2,18,12])
    inst=n.rom(addr,32,words)
    op,rd,fn,r1,r2,f7=n.split(inst,[7,5,3,5,5,7])
    rd4,rdhi=n.split(rd,[4,1]); r14,r1hi=n.split(r1,[4,1]); r24,r2hi=n.split(r2,[4,1])
    eq=lambda a,v:n.eq(a,n.const(n.widths[a],v))
    AND=lambda a,b:n.gate('AND',a,b)
    OR=lambda a,b:n.gate('OR',a,b)
    NOT=lambda a:n.gate('NOT',a)
    add=AND(AND(eq(op,0x33),eq(fn,0)),eq(f7,0))
    addi=AND(eq(op,0x13),eq(fn,0)); lui=eq(op,0x37); jalr=AND(eq(op,0x67),eq(fn,0))
    lw=AND(eq(op,3),eq(fn,2)); lbu=AND(eq(op,3),eq(fn,4))
    sw=AND(eq(op,0x23),eq(fn,2)); sb=AND(eq(op,0x23),eq(fn,0))
    load=OR(lw,lbu); store=OR(sw,sb); memory=OR(load,store)
    writes=OR(OR(add,addi),OR(lui,OR(jalr,load)))
    valid=OR(writes,store)
    valid=AND(valid,NOT(OR(AND(writes,rdhi),OR(AND(NOT(lui),r1hi),AND(OR(add,store),r2hi)))))
    a=n.mux(regs,r14); b=n.mux(regs,r24)
    _,imm_i=n.split(inst,[20,12]); imm_s=join(n,[rd,f7]); _,imm_u=n.split(inst,[12,20])
    imm=n.extend(n.mux([imm_i,imm_s],store),32,True)
    effective=n.add(a,imm); lane,ma,mhi=n.split(effective,[2,18,12])
    aligned=OR(NOT(OR(lw,sw)),eq(lane,0))
    valid=AND(valid,OR(NOT(memory),AND(eq(mhi,0),aligned)))
    target=AND(effective,n.const(32,0xfffffffe)); tlo,_,thi=n.split(target,[2,18,12])
    valid=AND(valid,OR(NOT(jalr),AND(eq(tlo,0),eq(thi,0))))
    valid=AND(valid,AND(eq(low,0),eq(high,0)))
    # A 32-bit RAM with byte enables. SB repeats its low byte onto each lane;
    # only the addressed lane is enabled, preserving the other three bytes.
    byte=n.split(b,[8,24])[0]; wd=n.mux([b,join(n,[byte]*4)],sb)
    ram=n.new(32,'RAM_read'); we=AND(AND(store,valid),NOT(rst))
    bes=[OR(sw,AND(sb,eq(lane,k))) for k in range(4)]
    n.cell(4,'RAM',{'addrWidth':18,'dataWidth':32,'enables':'byte','type':'nonvolatile',
      'clearpin':'false','trigger':'rising','asyncread':'true','byteenables':'byteEnables',
      'databus':'bibus','appearance':'classic','label':'Data_RAM'},
      [(0,10,ma),(0,50,we),(0,60,on),(0,110,clk),(0,130,wd),(240,130,ram)]+
      [(0,100-10*k,bes[k]) for k in range(4)])
    readbyte=n.mux(n.split(ram,[8]*4),lane)
    loaded=n.mux([ram,n.extend(readbyte,32)],lbu)
    plus4=n.add(pc,n.const(32,4)); value=n.add(a,n.mux([imm,b],add))
    value=n.mux([value,join(n,[n.const(12,0),imm_u])],lui)
    value=n.mux([value,loaded],load); value=n.mux([value,plus4],jalr)
    n.reg('PC',32,n.mux([plus4,target],jalr),clk,rst,valid)
    for k in range(1,16): n.reg(f'x{k}',32,value,clk,rst,AND(AND(valid,writes),eq(rd,k)))
    count=n.new(32,'Cycles'); n.reg('Cycles',32,n.add(count,n.const(32,1)),clk,rst,on)
    n.pin('PC_out',32,True,pc)
    for k in range(16): n.pin(f'x{k}_out',32,True,regs[k])
    n.pin('fault',1,True,NOT(valid)); n.pin('Cycles_out',32,True,count)
    n.pin('halt',1,True,OR(eq(count,cycles),NOT(valid)))
    n.save()

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--hex',type=Path);p.add_argument('--name',default='minirv_full')
    p.add_argument('--out',type=Path);p.add_argument('--cycles',type=int,default=64);args=p.parse_args()
    if args.out: g.OUT=args.out; g.OUT.mkdir(parents=True,exist_ok=True)
    data=read_hex(args.hex) if args.hex else dict(enumerate(demo()))
    words=[data.get(k,0) for k in range(max(data)+1)]
    build(args.name,words,args.cycles)
    print(f'Generated {g.OUT / (args.name+".circ")}')
