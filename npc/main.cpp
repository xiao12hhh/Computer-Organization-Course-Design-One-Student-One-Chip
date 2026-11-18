#include <Vscpu_io.h>
#include <verilated.h>
#include <verilated_vcd_c.h>
#include <array>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
int main(int argc,char**argv){
  Verilated::commandArgs(argc,argv);Verilated::traceEverOn(true);
  Vscpu_io top;VerilatedVcdC wave;top.trace(&wave,8);wave.open("build/scpu-npc/scpu.vcd");
  std::array<uint8_t,4> regs{};uint8_t pc=0,out=0;bool valid=false;
  uint64_t time=0;
  auto step=[&](uint8_t ins,bool reset=false,bool enable=true,bool trace=false){
    top.clk=0;top.instruction=ins;top.rst=reset;top.en=enable;top.eval();
    if(trace)wave.dump(time);++time;
    bool illegal=(ins>>6)==1 && (ins&0x3c)!=0;
    if(bool(top.illegal)!=illegal){std::fprintf(stderr,"illegal decode mismatch\n");std::exit(1);}
    if(reset){pc=0;regs.fill(0);out=0;valid=false;}
    else if(enable && !illegal){
      uint8_t next=(pc+1)&15;unsigned rd=(ins>>4)&3,rs1=(ins>>2)&3,rs2=ins&3;
      switch(ins>>6){
        case 0:regs[rd]=uint8_t(regs[rs1]+regs[rs2]);break;
        case 1:out=regs[rs2];valid=true;break;
        case 2:regs[rd]=ins&15;break;
        case 3:if(regs[0]!=regs[rs2])next=(ins>>2)&15;break;
      }
      pc=next;
    }
    top.clk=1;top.eval();if(trace)wave.dump(time);++time;
    if(top.pc!=pc || top.r0!=regs[0] || top.r1!=regs[1] || top.r2!=regs[2] || top.r3!=regs[3] || top.out_value!=out || bool(top.out_valid)!=valid){
      std::fprintf(stderr,"state mismatch at cycle %llu\n",(unsigned long long)(time/2));std::exit(1);
    }
  };
  const uint8_t rom[]={0x8b,0x91,0xa0,0xb1,0x29,0x17,0xd1,0x42,0xe3};
  step(0,true,true,true);
  for(int cycle=0;cycle<40;cycle++){
    if(pc>=sizeof rom)return 1;
    step(rom[pc],false,true,true);
    std::printf("%2d pc=%x R=[%u,%u,%u,%u] OUT=%u valid=%d\n",cycle+1,pc,regs[0],regs[1],regs[2],regs[3],out,valid);
  }
  if(!valid || out!=55 || pc!=8)return 1;
  wave.close();
  uint32_t seed=0x9512026;
  for(int i=0;i<20000;i++){
    seed=seed*1664525u+1013904223u;
    step(uint8_t(seed>>24),i%251==0,(seed&3)!=0);
  }
  top.final();puts("PASS NPC: sum=55; 20000 differential cycles including reset/stall/out/illegal/overflow");
}
