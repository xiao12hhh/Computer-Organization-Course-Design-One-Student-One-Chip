// PA1 week 12 commands; watchpoints intentionally belong to week 13.
#include <isa.h>
#include <cpu/cpu.h>
#include <memory/paddr.h>
#include <readline/readline.h>
#include <readline/history.h>
#include <ctype.h>
#include <errno.h>
#include "sdb.h"
static bool batch=false;
void init_regex(void);
void init_wp_pool(void);
void sdb_set_batch_mode(void){batch=true;}
void init_sdb(void){init_regex();init_wp_pool();}
static char *skip(char *p){while(p && isspace((unsigned char)*p))++p;return p;}
static bool number(char **text,unsigned long *value) {
  char *p=skip(*text),*end;
  if(!p || !isdigit((unsigned char)*p))return false;
  errno=0;*value=strtoul(p,&end,10);
  if(errno || (*end && !isspace((unsigned char)*end)) || !*value)return false;
  *text=skip(end);return true;
}
static void help(void){puts("help      Show commands\nc         Continue\nq         Quit\nsi [N]    Step N instructions (default 1)\ninfo r    Registers\nx N EXPR  Read N 32-bit memory words\np EXPR    Evaluate unsigned RV32 expression");}
void sdb_mainloop(void) {
  if(batch){cpu_exec((uint64_t)-1);return;}
  for(;;) {
    char *line=readline("(nemu) ");if(!line)break;if(*line)add_history(line);
    char *cmd=skip(line),*args=cmd;
    while(*args && !isspace((unsigned char)*args))++args;
    if(*args)*args++=0;
    args=skip(args);
    if(!*cmd){free(line);continue;}
    if(!strcmp(cmd,"q")){free(line);break;}
    if(!strcmp(cmd,"help"))help();
    else if(!strcmp(cmd,"c")){if(*args)puts("usage: c");else cpu_exec((uint64_t)-1);}
    else if(!strcmp(cmd,"si")) {
      unsigned long n=1;
      if(*args && (!number(&args,&n)||*args))puts("usage: si [positive decimal N]");
      else cpu_exec(n);
    } else if(!strcmp(cmd,"info")) {
      char *end=args+strlen(args);while(end>args && isspace((unsigned char)end[-1]))*--end=0;
      if(!strcmp(args,"r"))isa_reg_display();else puts("usage: info r (watchpoints are week 13)");
    } else if(!strcmp(cmd,"p")) {
      bool ok;word_t value=expr(args,&ok);
      if(ok)printf("= %u (0x%08x)\n",value,value);else puts("Invalid expression");
    } else if(!strcmp(cmd,"x")) {
      unsigned long n;bool ok=false;
      if(!number(&args,&n)||n>1024||!*args)puts("usage: x N EXPR (1 <= N <= 1024)");
      else {
        word_t addr=expr(args,&ok);
        uint64_t last=(uint64_t)addr+4*n-1;
        if(!ok||last>UINT32_MAX||!in_pmem(addr)||!in_pmem((paddr_t)last))puts("Invalid expression or memory range");
        else for(unsigned long i=0;i<n;i++)printf("0x%08x: 0x%08x\n",addr+4*(uint32_t)i,paddr_read(addr+4*(uint32_t)i,4));
      }
    } else printf("Unknown command '%s'\n",cmd);
    free(line);
  }
}
