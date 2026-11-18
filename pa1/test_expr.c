#include "expr.h"
#include <assert.h>
#include <stdio.h>
#include <string.h>
static uint32_t reg(const char *n,bool *ok){*ok=!strcmp(n,"a0")||!strcmp(n,"pc");return !strcmp(n,"a0")?7:0x80000000;}
static uint32_t mem(uint32_t a,bool *ok){*ok=a==0x80000000;return 0x12345678;}
static void check(const char *s,bool valid,uint32_t expected){bool ok;uint32_t v=course_expr(s,&ok,reg,mem);assert(ok==valid);if(ok)assert(v==expected);}
int main(int argc,char **argv){
  if(argc==2 && !strcmp(argv[1],"--stdin")){
    char line[8192];while(fgets(line,sizeof line,stdin)){bool ok;uint32_t v=course_expr(line,&ok,reg,mem);printf("%d %u\n",ok,v);}return 0;
  }
  check("1 + 2 * 3",true,7);check("(1+2)*3",true,9);check("10-3-2",true,5);
  check("20/2/2",true,5);check("-1",true,UINT32_MAX);check("0xffffffff+1",true,0);
  check("-2 / 2",true,2147483647);check("$a0 * 2",true,14);check("*$pc",true,0x12345678);
  check("1 == 1 != 0 && 5",true,1);check("0 && 1/0",true,0);check("0 && *0",true,0);
  check("1 && 0 && *0",true,0);check("--2",true,2);check("08+1",true,9);
  const char *bad[]={"","()","(1+2","1+2)","1 2","1/0","*0","$nope","0x","4294967296","1=1","1||2","1+","0 && (1+)","$","1 & 1"};
  for(unsigned i=0;i<sizeof bad/sizeof *bad;i++)check(bad[i],false,0);
  char deep[1024];memset(deep,'(',300);deep[300]='1';memset(deep+301,')',300);deep[601]=0;check(deep,false,0);
  puts("PASS expression regression: precedence, unsigned arithmetic, registers, dereference, short circuit, malformed and depth limit");
}
