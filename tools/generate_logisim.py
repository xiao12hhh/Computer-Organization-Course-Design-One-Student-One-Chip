"""Generate inspectable gate-level Logisim circuits and exhaustive vectors.

Only AND/OR/XOR/NOT gates, pins, tunnels and wires are used. No opaque HDL blocks.
"""
from pathlib import Path
import itertools
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'logisim'
OUT.mkdir(exist_ok=True)

class Circuit:
    def __init__(self, name, inputs, outputs):
        self.name, self.inputs, self.outputs = name, inputs, outputs
        self.root = ET.Element('project', source='4.0.0', version='1.0')
        for n, lib in enumerate(['Wiring','Gates','Plexers','Arithmetic','Memory','I/O']):
            ET.SubElement(self.root,'lib',name=str(n),desc=f'#{lib}')
        ET.SubElement(self.root,'main',name=name)
        self.c = ET.SubElement(self.root,'circuit',name=name)
        self.num=0
        for i,label in enumerate(inputs):
            x,y=80,80+40*i
            self.comp('0','Pin',x,y,{'label':label,'facing':'east','tristate':'false'})
            self.wire(x,y,x+20,y); self.tunnel(label,x+20,y)
        for i,label in enumerate(outputs):
            x,y=1420,80+50*i
            self.comp('0','Pin',x,y,{'label':label,'facing':'west','output':'true'})
            self.wire(x-20,y,x,y); self.tunnel(label,x-20,y)
    def comp(self, lib,name,x,y,attrs):
        e=ET.SubElement(self.c,'comp',lib=lib,name=name,loc=f'({x},{y})')
        for n,v in attrs.items(): ET.SubElement(e,'a',name=n,val=str(v))
    def wire(self,x,y,xx,yy):
        ET.SubElement(self.c,'wire',{'from':f'({x},{y})','to':f'({xx},{yy})'})
    def tunnel(self,label,x,y):
        self.comp('0','Tunnel',x,y,{'label':label,'facing':'west'})
    def gate(self,kind,*args,out=None):
        n=self.num; self.num+=1
        x=360+(n//12)*240; y=80+(n%12)*90
        out=out or f'n{n}'
        self.comp('1',kind+' Gate',x,y,{'size':'30','inputs':str(len(args))} if len(args)>1 else {'size':'30'})
        for i,a in enumerate(args):
            yy=y if len(args)==1 else y+(-10 if i==0 else 10)
            self.wire(x-60,yy,x-30,yy); self.tunnel(a,x-60,yy)
        self.wire(x,y,x+30,y); self.tunnel(out,x+30,y)
        return out
    def reduce(self,kind,args,out):
        value=args[0]
        for i,a in enumerate(args[1:]): value=self.gate(kind,value,a,out=out if i==len(args)-2 else None)
    def save(self,rows):
        ET.indent(self.root)
        ET.ElementTree(self.root).write(OUT/(self.name+'.circ'),encoding='utf-8',xml_declaration=True)
        with (OUT/(self.name+'.txt')).open('w',encoding='ascii') as f:
            f.write(' '.join(self.inputs+self.outputs)+'\n')
            for row in rows: f.write(' '.join(map(str,row))+'\n')

c=Circuit('decoder24',['A0','A1'],['Y0','Y1','Y2','Y3'])
inv=[c.gate('NOT',f'A{i}') for i in range(2)]
for i in range(4): c.gate('AND',('A0' if i&1 else inv[0]),('A1' if i&2 else inv[1]),out=f'Y{i}')
c.save([[a&1,(a>>1)&1]+[int(a==j) for j in range(4)] for a in range(4)])

c=Circuit('encoder164',[f'D{i}' for i in range(16)],[f'Y{i}' for i in range(4)])
for bit in range(4): c.reduce('OR',[f'D{i}' for i in range(16) if i&(1<<bit)],f'Y{bit}')
# The plain encoder contract requires one-hot inputs; test zero plus every legal input.
c.save([[int(i==n) for i in range(16)]+[(max(n,0)>>b)&1 for b in range(4)] for n in range(-1,16)])

c=Circuit('full_adder',['A','B','Cin'],['Sum','Cout'])
t=c.gate('XOR','A','B'); c.gate('XOR',t,'Cin',out='Sum')
c.gate('OR',c.gate('AND','A','B'),c.gate('AND',t,'Cin'),out='Cout')
c.save([[a,b,ci,(a+b+ci)&1,(a+b+ci)>>1] for a,b,ci in itertools.product(range(2),repeat=3)])

inputs=['S0','S1']+[f'D{d}_{b}' for d in range(4) for b in range(3)]
c=Circuit('mux4x3',inputs,[f'Y{b}' for b in range(3)])
n0=c.gate('NOT','S0'); n1=c.gate('NOT','S1')
select=[c.gate('AND','S0' if d&1 else n0,'S1' if d&2 else n1) for d in range(4)]
for b in range(3): c.reduce('OR',[c.gate('AND',select[d],f'D{d}_{b}') for d in range(4)],f'Y{b}')
def muxrows():
    for word in range(16384):
        bits=[(word>>i)&1 for i in range(14)]
        s=bits[0]+2*bits[1]
        yield bits+bits[2+3*s:5+3*s]
c.save(muxrows())
print('Generated 4 gate-level circuits and their test vectors.')
