"""8-bit value/counter displayed in binary, octal, decimal or hexadecimal."""
import generate_processors as g
from generate_minirv import join
from pathlib import Path

def build(counter=False,test=False):
    name='radix_counter_test' if test else ('radix_counter' if counter else 'radix_display')
    n=g.Netlist(name)
    value=n.pin('Value',8);base=n.pin('Base',2)
    if counter:
        clk,rst=g.clock(n);q=n.new(8,'Count');load=n.pin('Load')
        run=n.const(1,1) if test else n.pin('Run')
        n.reg('Count',8,n.mux([n.add(q,n.const(8,1)),value],load),clk,rst,n.gate('OR',load,run))
        value=q;n.pin('Count_out',8,True,q)
    address=join(n,[value,base]);words=[]
    for b in [2,8,10,16]:
        for v in range(256):
            packed=0
            for j in range(8): packed|=(v%b)<<(4*j);v//=b
            words.append(packed)
    digits=n.rom(address,32,words);n.pin('Packed',32,True,digits)
    for j,digit in enumerate(n.split(digits,[4]*8)):
        n.cell(5,'Hex Digit Display',{'label':f'Digit{j}'},[(0,0,digit)])
    if test:n.pin('halt',1,True,n.eq(value,n.const(8,255)))
    n.save()
    return name

if __name__=='__main__':
    build();build(True)
    path=g.OUT/'radix_display.txt'
    with path.open('w') as f:
        f.write('Value[8] Base[2] Packed[32]\n')
        for mode,base in enumerate([2,8,10,16]):
            for value in range(256):
                digits=[];v=value
                for _ in range(8):digits.append(v%base);v//=base
                packed=sum(d<<(4*j) for j,d in enumerate(digits))
                f.write(f'{value} {mode} {packed}\n')
    print('Generated radix display/counter and 1024 vectors')
