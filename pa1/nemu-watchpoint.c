#include "sdb.h"
#include <isa.h>
#include <cpu/cpu.h>
#define NR_WP 32
typedef struct Watchpoint {
  int id;
  struct Watchpoint *next;
  char expression[4097];
  word_t value;
} WP;
static WP pool[NR_WP];
static WP *active,*available;
void init_wp_pool(void) {
  active=NULL;available=pool;
  for(int i=0;i<NR_WP;i++){pool[i].id=i;pool[i].next=i+1<NR_WP?&pool[i+1]:NULL;}
}
void course_watch_add(char *text) {
  bool ok=false;
  word_t value=expr(text,&ok);
  if(!ok){puts("Invalid watch expression");return;}
  if(!available){puts("Watchpoint pool exhausted (32)");return;}
  WP *p=available;available=p->next;
  strcpy(p->expression,text);p->value=value;p->next=active;active=p;
  printf("Watchpoint %d: %s = %u\n",p->id,p->expression,p->value);
}
void course_watch_delete(unsigned long id) {
  WP **link=&active;
  while(*link && (unsigned long)(*link)->id!=id)link=&(*link)->next;
  if(!*link){puts("No such watchpoint");return;}
  WP *p=*link;*link=p->next;p->next=available;available=p;
  printf("Deleted watchpoint %d\n",p->id);
}
void course_watch_list(void) {
  if(!active)puts("No watchpoints");
  for(WP *p=active;p;p=p->next)printf("%d: %s = %u (0x%08x)\n",p->id,p->expression,p->value,p->value);
}
void course_watch_check(void) {
  bool stop=false;
  for(WP *p=active;p;p=p->next){
    bool ok=false;word_t value=expr(p->expression,&ok);
    if(!ok){printf("Watchpoint %d evaluation failed: %s\n",p->id,p->expression);stop=true;}
    else if(value!=p->value){
      printf("Watchpoint %d changed: %s\nold=%u new=%u pc=0x%08x\n",p->id,p->expression,p->value,value,cpu.pc);
      p->value=value;stop=true;
    }
  }
  // Never overwrite END/ABORT from ebreak, an invalid instruction or difftest.
  if(stop && nemu_state.state==NEMU_RUNNING)nemu_state.state=NEMU_STOP;
}
