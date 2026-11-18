#include "local-include/reg.h"
#include <cpu/cpu.h>
#include <cpu/ifetch.h>
#include <cpu/decode.h>
#include "course_rv32.h"
static uint32_t read_mem(uint32_t address,int size){return vaddr_read(address,size);}
static void write_mem(uint32_t address,int size,uint32_t value){vaddr_write(address,size,value);}
int isa_exec_once(Decode *s){
  s->isa.inst=inst_fetch(&s->snpc,4);s->dnpc=s->snpc;
  int result=rv32_execute(s->isa.inst,s->pc,cpu.gpr,&s->dnpc,read_mem,write_mem);
  if(result==RV_BREAK)NEMUTRAP(s->pc,gpr(10));
  else if(result==RV_ILLEGAL)INV(s->pc);
  return 0;
}
