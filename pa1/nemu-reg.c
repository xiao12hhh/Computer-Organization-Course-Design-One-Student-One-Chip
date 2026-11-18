// RV32 register display and name lookup for NEMU ics2024.
#include <isa.h>
#include "local-include/reg.h"
#include <errno.h>
const char *regs[]={"$0","ra","sp","gp","tp","t0","t1","t2","s0","s1","a0","a1","a2","a3","a4","a5",
  "a6","a7","s2","s3","s4","s5","s6","s7","s8","s9","s10","s11","t3","t4","t5","t6"};
void isa_reg_display(void) {
  printf("pc  0x%08x\n",cpu.pc);
  for(int i=0;i<32;i++)printf("x%-2d %-3s 0x%08x  %u\n",i,regs[i],gpr(i),gpr(i));
}
word_t isa_reg_str2val(const char *s,bool *success) {
  *success=true;
  if(*s=='$')++s;
  if(!strcmp(s,"pc"))return cpu.pc;
  if(!strcmp(s,"0")||!strcmp(s,"zero"))return 0;
  if(!strcmp(s,"fp"))return gpr(8);
  for(int i=1;i<32;i++)if(!strcmp(s,regs[i]))return gpr(i);
  if(*s=='x' && s[1]>='0' && s[1]<='9') {
    char *end;errno=0;unsigned long n=strtoul(s+1,&end,10);
    if(!errno && !*end && n<32)return gpr(n);
  }
  *success=false;return 0;
}
