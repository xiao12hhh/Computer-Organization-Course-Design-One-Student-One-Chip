// Unsigned RV32 expression evaluator. Recursive descent by precedence level.
#include "expr.h"
#include <ctype.h>
#include <errno.h>
#include <stdlib.h>
#include <string.h>
enum {END=256,NUMBER,REG,EQ,NE,AND,BAD};
typedef struct {
  const char *p; int token,depth; uint32_t value; char reg[64]; bool ok;
  expr_register_fn read_reg; expr_memory_fn read_mem;
} Parser;
static void next(Parser *p) {
  while(isspace((unsigned char)*p->p)) ++p->p;
  unsigned char c=*p->p;
  if(!c) {p->token=END;return;}
  if(isdigit(c)) {
    char *end;errno=0;
    int base=(c=='0' && (p->p[1]=='x'||p->p[1]=='X'))?16:10;
    unsigned long long v=strtoull(p->p,&end,base);
    if(errno || end==p->p || v>UINT32_MAX) {p->ok=false;p->token=BAD;return;}
    p->p=end;p->value=(uint32_t)v;p->token=NUMBER;return;
  }
  if(c=='$') {
    ++p->p;size_t n=0;
    while(isalnum((unsigned char)*p->p)||*p->p=='_') {
      if(n+1>=sizeof p->reg){p->ok=false;p->token=BAD;return;}
      p->reg[n++]=*p->p++;
    }
    p->reg[n]=0;p->token=REG;if(!n)p->ok=false;return;
  }
  if((c=='='||c=='!') && p->p[1]=='=') {p->p+=2;p->token=c=='='?EQ:NE;return;}
  if(c=='&' && p->p[1]=='&') {p->p+=2;p->token=AND;return;}
  ++p->p;p->token=c;
  if(!strchr("+-*/()",c)){p->ok=false;p->token=BAD;}
}
static uint32_t logical_and(Parser *,bool);
static uint32_t unary(Parser *p,bool run) {
  if(!p->ok)return 0;
  if(++p->depth>128){p->ok=false;--p->depth;return 0;}
  uint32_t v=0;int token=p->token;
  if(token==NUMBER){v=p->value;next(p);}
  else if(token==REG){if(run){bool ok=false;v=p->read_reg?p->read_reg(p->reg,&ok):0;p->ok &= ok;}next(p);}
  else if(token=='('){next(p);v=logical_and(p,run);if(p->token!=')')p->ok=false;else next(p);}
  else if(token=='-'||token=='+'||token=='*') {
    next(p);v=unary(p,run);
    if(run && p->ok) {
      if(token=='-')v=0u-v;
      else if(token=='*'){bool ok=false;v=p->read_mem?p->read_mem(v,&ok):0;p->ok &= ok;}
    }
  } else p->ok=false;
  --p->depth;return v;
}
static uint32_t multiply(Parser *p,bool run) {
  uint32_t v=unary(p,run);
  while(p->ok && (p->token=='*'||p->token=='/')) {
    int op=p->token;next(p);uint32_t rhs=unary(p,run);
    if(run && p->ok){if(op=='*')v*=rhs;else if(!rhs)p->ok=false;else v/=rhs;}
  }
  return v;
}
static uint32_t add(Parser *p,bool run) {
  uint32_t v=multiply(p,run);
  while(p->ok && (p->token=='+'||p->token=='-')) {
    int op=p->token;next(p);uint32_t rhs=multiply(p,run);
    if(run)v=op=='+'?v+rhs:v-rhs;
  }
  return v;
}
static uint32_t equal(Parser *p,bool run) {
  uint32_t v=add(p,run);
  while(p->ok && (p->token==EQ||p->token==NE)) {
    int op=p->token;next(p);uint32_t rhs=add(p,run);
    if(run)v=op==EQ?v==rhs:v!=rhs;
  }
  return v;
}
static uint32_t logical_and(Parser *p,bool run) {
  uint32_t v=equal(p,run);
  while(p->ok && p->token==AND) {
    next(p);uint32_t rhs=equal(p,run && v!=0);
    if(run)v=(v!=0 && rhs!=0);
  }
  return v;
}
uint32_t course_expr(const char *text,bool *success,expr_register_fn regs,expr_memory_fn mem) {
  if(!success)return 0;
  *success=false;
  if(!text || strlen(text)>4096)return 0;
  Parser p={.p=text,.ok=true,.read_reg=regs,.read_mem=mem};
  next(&p);uint32_t result=logical_and(&p,true);
  *success=p.ok && p.token==END;
  return *success?result:0;
}
