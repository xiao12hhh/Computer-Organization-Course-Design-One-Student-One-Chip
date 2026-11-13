"""Build real Logisim datapaths from registers, adders, muxes and ROMs.

The generated schematics are separate from the RTL implementations, so both can
be checked against the same architectural behavior.
"""
from pathlib import Path
import xml.etree.ElementTree as E

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'logisim'

class Netlist:
    def __init__(self,name):
        self.name=name; self.n=0; self.net=0; self.widths={}
        self.root=E.Element('project',source='4.0.0',version='1.0')
        for i,n in enumerate(['Wiring','Gates','Plexers','Arithmetic','Memory','I/O']): E.SubElement(self.root,'lib',name=str(i),desc='#'+n)
        E.SubElement(self.root,'main',name=name)
        self.c=E.SubElement(self.root,'circuit',name=name)
    def new(self,width,label=None):
        self.net+=1; label=label or f'n{self.net}'
        self.widths[label]=width; return label
    def cell(self,lib,name,attrs,ports):
        i=self.n; self.n+=1; x=180+(i%6)*520; y=160+(i//6)*210
        c=E.SubElement(self.c,'comp',lib=str(lib),name=name,loc=f'({x},{y})')
        for k,v in attrs.items():
            a=E.SubElement(c,'a',name=k)
            if k=='contents': a.text=v
            else: a.set('val',str(v))
        for dx,dy,net in ports:
            # Direct connection to a named tunnel. Keep wire stubs short and orthogonal.
            xx,yy=x+dx,y+dy
            shift=-40 if dx<0 else 40
            tx,ty=xx+shift,yy
            if name=='Register' and dy==20:
                tx,ty=xx,yy+(40 if dx==-20 else 80)
            E.SubElement(self.c,'wire',{'from':f'({xx},{yy})','to':f'({tx},{ty})'})
            t=E.SubElement(self.c,'comp',lib='0',name='Tunnel',loc=f'({tx},{ty})')
            for k,v in {'label':net,'width':self.widths[net],'facing':'east' if shift<0 else 'west'}.items(): E.SubElement(t,'a',name=k,val=str(v))
    def const(self,width,value):
        n=self.new(width); self.cell(0,'Constant',{'width':width,'value':hex(value)},[(0,0,n)]); return n
    def pin(self,label,width=1,output=False,net=None):
        n=net or self.new(width,label)
        self.cell(0,'Pin',{'label':label,'width':width,'tristate':'false','output':str(output).lower(),'facing':'west' if output else 'east'},[(0,0,n)])
        return n
    def gate(self,kind,a,b=None):
        n=self.new(self.widths[a]); args={'size':30,'width':self.widths[a]}
        ps=[(0,0,n)]
        if b is None: ps+=[(-30,0,a)]
        else: args['inputs']=2; ps+=[(-30,-10,a),(-30,10,b)]
        self.cell(1,kind+' Gate',args,ps); return n
    def eq(self,a,b):
        n=self.new(1); self.cell(3,'Comparator',{'width':self.widths[a],'mode':'unsigned'},[(-40,-10,a),(-40,10,b),(0,0,n)]); return n
    def add(self,a,b):
        n=self.new(self.widths[a]); self.cell(3,'Adder',{'width':self.widths[a]},[(-40,-10,a),(-40,10,b),(-20,-20,self.const(1,0)),(0,0,n)]); return n
    def mux(self,values,sel):
        width=self.widths[values[0]]; n=self.new(width); count=len(values)
        ps=[(0,0,n)]
        if count==2: ps += [(-30,-10,values[0]),(-30,10,values[1]),(-20,20,sel)]
        else: ps += [(-40,-count*5+i*10,v) for i,v in enumerate(values)]+[(-20,count*5,sel)]
        self.cell(2,'Multiplexer',{'width':width,'select':(count-1).bit_length(),'enable':'false','size':'40'},ps); return n
    def reg(self,label,width,data,clk,rst,en):
        n=self.new(width,label); self.cell(4,'Register',{'width':width,'appearance':'classic','label':label},[(0,0,n),(-30,0,data),(-30,10,en),(-20,20,clk),(-10,20,rst)]); return n
    def extend(self,a,width,sign=False):
        n=self.new(width); self.cell(0,'Bit Extender',{'in_width':self.widths[a],'out_width':width,'type':'sign' if sign else 'zero'},[(-40,0,a),(0,0,n)]); return n
    def split(self,a,widths):
        assert sum(widths)==self.widths[a]
        nets=[self.new(w) for w in widths]; attrs={'incoming':sum(widths),'fanout':len(widths),'appear':'right','facing':'east'}
        bit=0
        for group,w in enumerate(widths):
            for _ in range(w): attrs['bit'+str(bit)]=group; bit+=1
        self.cell(0,'Splitter',attrs,[(0,0,a)]+[(20,10+10*i,n) for i,n in enumerate(nets)])
        return nets
    def rom(self,address,width,words):
        n=self.new(width); aw=self.widths[address]
        contents=f'addr/data: {aw} {width}\n'+' '.join(format(v,'x') for v in words)+'\n'
        self.cell(4,'ROM',{'addrWidth':aw,'dataWidth':width,'appearance':'classic','contents':contents},[(0,10,address),(240,60,n)])
        return n
    def save(self):
        E.indent(self.root); E.ElementTree(self.root).write(OUT/(self.name+'.circ'),encoding='utf-8',xml_declaration=True)

def clock(n):
    clk=n.new(1,'clock'); n.cell(0,'Clock',{},[(0,0,clk)])
    rst=n.pin('Reset'); return clk,rst

def summation():
    n=Netlist('sum10'); clk,rst=clock(n); one=n.const(8,1)
    index=n.new(8,'index'); total=n.new(8,'sum')
    done=n.eq(index,n.const(8,10)); en=n.gate('NOT',done)
    nextindex=n.add(index,one)
    n.reg('index',8,nextindex,clk,rst,en)
    n.reg('sum',8,n.add(total,nextindex),clk,rst,en)
    n.pin('Index',8,True,index); n.pin('Sum',8,True,total); n.pin('halt',1,True,done)
    n.save()

def scpu():
    n=Netlist('scpu'); clk,rst=clock(n); on=n.const(1,1)
    pc=n.new(4,'PC'); regs=[n.new(8,f'R{i}') for i in range(4)]
    words=[0x8b,0x91,0xa0,0xb1,0x29,0x17,0xd1,0xdf]
    inst=n.rom(pc,8,words)
    rs2,rs1,rd,op=n.split(inst,[2,2,2,2])
    imm,_=n.split(inst,[4,4]); _,addr,_=n.split(inst,[2,4,2])
    lhs=n.mux(regs,rs1); rhs=n.mux(regs,rs2)
    li=n.eq(op,n.const(2,2)); add=n.eq(op,n.const(2,0)); branch=n.eq(op,n.const(2,3))
    write=n.gate('OR',li,add); wd=n.mux([n.add(lhs,rhs),n.extend(imm,8)],li)
    taken=n.gate('AND',branch,n.gate('NOT',n.eq(regs[0],rhs)))
    npc=n.mux([n.add(pc,n.const(4,1)),addr],taken)
    n.reg('PC',4,npc,clk,rst,on)
    for i in range(4):
        n.reg(f'R{i}',8,wd,clk,rst,n.gate('AND',write,n.eq(rd,n.const(2,i))))
        n.pin(f'R{i}_out',8,True,regs[i])
    n.pin('PC_out',4,True,pc); n.pin('halt',1,True,n.eq(pc,n.const(4,7)))
    n.save()

def minirv2(edge_test=False):
    n=Netlist('minirv2_edges' if edge_test else 'minirv2'); clk,rst=clock(n); zero=n.const(32,0)
    pc=n.new(32,'PC'); regs=[zero]+[n.new(32,f'x{i}') for i in range(1,16)]
    _,romaddr,_=n.split(pc,[2,6,24])
    # Official call/return example: final a0 = 30, PC = 12.
    words=[0x01400513,0x010000e7,0x00c000e7,0x00c00067,0x00a50513,0x00008067]
    if edge_test:
        words=[0xfff00113,0x00110193,0x80000213,0x7ff00293,0x06300013,0x01d00313,0x00030367,0x01c00067]
    inst=n.rom(romaddr,32,words)
    opcode,rd,funct,rs1,imm=n.split(inst,[7,5,3,5,12])
    rd4,rdhi=n.split(rd,[4,1]); rs4,rshi=n.split(rs1,[4,1])
    funct0=n.eq(funct,n.const(3,0)); addi=n.eq(opcode,n.const(7,0x13)); jalr=n.eq(opcode,n.const(7,0x67))
    valid=n.gate('AND',n.gate('OR',addi,jalr),funct0)
    valid=n.gate('AND',valid,n.gate('NOT',n.gate('OR',rdhi,rshi)))
    value=n.add(n.mux(regs,rs4),n.extend(imm,32,True)); plus4=n.add(pc,n.const(32,4))
    target=n.gate('AND',value,n.const(32,0xfffffffe))
    low,_=n.split(target,[2,30]); aligned=n.eq(low,n.const(2,0))
    valid=n.gate('AND',valid,n.gate('OR',n.gate('NOT',jalr),aligned))
    wd=n.mux([value,plus4],jalr); npc=n.mux([plus4,target],jalr)
    n.reg('PC',32,npc,clk,rst,valid)
    for i in range(1,16): n.reg(f'x{i}',32,wd,clk,rst,n.gate('AND',valid,n.eq(rd4,n.const(4,i))))
    n.pin('PC_out',32,True,pc); n.pin('a0',32,True,regs[10]); n.pin('ra',32,True,regs[1])
    n.pin('illegal',1,True,n.gate('NOT',valid))
    if edge_test:
        for i in [0,2,3,4,5,6]: n.pin(f'x{i}_out',32,True,regs[i])
    n.pin('halt',1,True,n.eq(pc,n.const(32,28 if edge_test else 12)))
    n.save()

summation(); scpu(); minirv2(); minirv2(True)
print('Generated sum10, scpu, and minirv2 Logisim datapaths.')
