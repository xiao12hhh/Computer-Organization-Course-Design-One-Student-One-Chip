#include <Vminirv_top.h>
#include <verilated.h>
#include <verilated_vcd_c.h>
#include <array>
#include <chrono>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <fstream>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
extern "C" {
#include "../../pa2/rv32.h"
}
namespace {
constexpr uint32_t ram_size=128*1024*1024, serial=0x10000000, rtc=0xa0000048;
std::vector<uint8_t> memory(ram_size),reference;
uint32_t base=0x80000000,refregs[32]={},refpc;
uint64_t retired=0,stores=0,serial_bytes=0,rtc_reads=0,latched_time=0;
uint32_t last_io_address=0,last_io_value=0;
bool done=false,quiet=false,diff=false;int exit_code=0;
auto started=std::chrono::steady_clock::now();
struct Store {uint32_t addr,data;int size;};
std::vector<Store> expected,actual;
uint32_t ram_read(const std::vector<uint8_t>&m,uint32_t a,int n){
  if(a<base || uint64_t(a-base)+n>m.size())throw std::runtime_error("RAM read outside mapped range: "+std::to_string(a));
  uint32_t v=0;for(int i=0;i<n;i++)v|=uint32_t(m[a-base+i])<<(8*i);return v;
}
void ram_write(std::vector<uint8_t>&m,uint32_t a,int n,uint32_t v){
  if(a<base || uint64_t(a-base)+n>m.size())throw std::runtime_error("RAM write outside mapped range");
  for(int i=0;i<n;i++)m[a-base+i]=uint8_t(v>>(8*i));
}
uint32_t ref_read(uint32_t a,int n){
  if(a>=base && uint64_t(a-base)+n<=reference.size())return ram_read(reference,a,n);
  if((a&~3u)==last_io_address)return (last_io_value>>(8*(a&3)))&(n==4?~0u:((1u<<(n*8))-1));
  throw std::runtime_error("Reference MMIO read was not observed in RTL");
}
void ref_write(uint32_t a,int n,uint32_t v){
  for(int i=0;i<n;i++)expected.push_back({a+uint32_t(i),uint8_t(v>>(i*8)),1});
  if(a>=base && uint64_t(a-base)+n<=reference.size())ram_write(reference,a,n,v);
}
}
extern "C" int pmem_read(int raw){
  uint32_t a=uint32_t(raw)&~3u;
  if(a==rtc || a==rtc+4){
    if(a==rtc+4)latched_time=std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-started).count();
    ++rtc_reads;last_io_address=a;last_io_value=a==rtc?uint32_t(latched_time):uint32_t(latched_time>>32);return last_io_value;
  }
  return ram_read(memory,a,4);
}
extern "C" void pmem_write(int raw,int data,char rawmask){
  uint32_t a=uint32_t(raw)&~3u,v=uint32_t(data);unsigned mask=uint8_t(rawmask);
  if(mask&~15u)throw std::runtime_error("Invalid byte mask");
  ++stores;
  for(unsigned i=0;i<4;i++)if(mask&(1u<<i)){
    uint32_t at=a+i;uint8_t byte=v>>(8*i);
    if(diff)actual.push_back({at,byte,1});
    if(at==serial){++serial_bytes;if(!quiet){std::putchar(byte);if(byte=='\n')std::fflush(stdout);}}
    else ram_write(memory,at,1,byte);
  }
}
extern "C" void npc_trap(int code,int trap_pc,int invalid){
  done=true;exit_code=code==0?0:1;
  std::fprintf(stderr,"\nNPC %s at pc=0x%08x, a0=%d\n",invalid?"ILLEGAL INSTRUCTION":code==0?"HIT GOOD TRAP":"HIT BAD TRAP",uint32_t(trap_pc),code);
}
int main(int argc,char **argv){try{
  uint64_t limit=1000000000;std::string filename,trace;
  for(int i=1;i<argc;i++){
    std::string arg=argv[i];
    if(arg=="--diff")diff=true;else if(arg=="--quiet")quiet=true;
    else if(arg=="--max" && i+1<argc)limit=std::stoull(argv[++i]);
    else if(arg=="--base" && i+1<argc)base=std::stoul(argv[++i],nullptr,0);
    else if(arg=="--trace" && i+1<argc)trace=argv[++i];
    else if(arg.size() && arg[0]=='-')throw std::runtime_error("Unknown option: "+arg);
    else filename=arg;
  }
  if(filename.empty())throw std::runtime_error("usage: npc [--diff] [--quiet] [--max N] [--base 0x...] [--trace file.vcd] program.bin");
  if(limit==0)limit=UINT64_MAX;
  std::ifstream f(filename,std::ios::binary|std::ios::ate);if(!f)throw std::runtime_error("Cannot open image");
  auto length=f.tellg();if(length<=0 || uint64_t(length)>memory.size())throw std::runtime_error("Invalid image size");
  f.seekg(0);if(!f.read(reinterpret_cast<char*>(memory.data()),length))throw std::runtime_error("Image read failed");
  if(diff)reference=memory;refpc=base;
  Verilated::commandArgs(argc,argv);Verilated::traceEverOn(!trace.empty());
  Vminirv_top top;std::unique_ptr<VerilatedVcdC> wave;
  if(!trace.empty()){wave=std::make_unique<VerilatedVcdC>();top.trace(wave.get(),8);wave->open(trace.c_str());}
  top.reset_pc=base;top.en=1;top.rst=1;top.clk=0;top.eval();top.clk=1;top.eval();top.clk=0;top.rst=0;top.eval();
  while(!done && retired<limit){
    top.clk=0;top.eval();if(wave)wave->dump(retired*2);
    int status=RV_OK;uint32_t next=refpc;
    if(diff){expected.clear();actual.clear();status=rv32_execute(ram_read(reference,refpc,4),refpc,refregs,&next,ref_read,ref_write);}
    top.clk=1;top.eval();if(wave)wave->dump(retired*2+1);++retired;
    if(diff && !top.fault){
      if(status==RV_ILLEGAL || top.pc!=next)throw std::runtime_error("Differential PC/decode mismatch");
      for(int i=0;i<16;i++)if(top.regs[i]!=refregs[i])throw std::runtime_error("Differential register mismatch x"+std::to_string(i));
      if(actual.size()!=expected.size())throw std::runtime_error("Differential store count mismatch");
      for(size_t i=0;i<actual.size();i++)if(actual[i].addr!=expected[i].addr||actual[i].data!=expected[i].data)throw std::runtime_error("Differential store mismatch");
      refpc=next;
    }
  }
  if(!done){std::fprintf(stderr,"NPC instruction limit reached (not a pass)\n");exit_code=2;}
  if(wave)wave->close();top.final();
  std::fprintf(stderr,"retired=%llu stores=%llu serial_bytes=%llu rtc_reads=%llu diff=%s\n",(unsigned long long)retired,(unsigned long long)stores,(unsigned long long)serial_bytes,(unsigned long long)rtc_reads,diff?"on":"off");
  return exit_code;
}catch(const std::exception&e){std::fprintf(stderr,"NPC ERROR: %s\n",e.what());return 1;}}
