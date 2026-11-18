// Course printf subset: %, c, s, d/i, u, x/X, p; width, '-' and '0'.
// Deliberately rejects precision, length modifiers and floating point.
#include <klib.h>
#if !defined(__ISA_NATIVE__) || defined(__NATIVE_USE_KLIB__)
typedef struct {char *out;size_t cap,total;int console;} Sink;
static void emit(Sink *s,char c){if(s->console)putch(c);else if(s->cap && s->total<s->cap-1)s->out[s->total]=c;++s->total;}
static int format(Sink *s,const char *fmt,va_list ap){
  while(*fmt){
    if(*fmt!='%'){emit(s,*fmt++);continue;}
    ++fmt;if(*fmt=='%'){emit(s,*fmt++);continue;}
    int left=0,zero=0,width=0;
    while(*fmt=='-'||*fmt=='0'){if(*fmt=='-')left=1;else zero=1;++fmt;}
    while(*fmt>='0'&&*fmt<='9'){if(width>100000)return -1;width=width*10+*fmt++-'0';}
    char kind=*fmt;if(!kind)return -1;++fmt;
    char rev[3*sizeof(uintptr_t)+1],ch=0;const char *str=NULL;size_t len=0;
    uintptr_t num=0;int neg=0,pointer=0,numeric=0;unsigned base=10;
    switch(kind){
      case 's':str=va_arg(ap,const char *);if(!str)str="(null)";len=strlen(str);break;
      case 'c':ch=(char)va_arg(ap,int);str=&ch;len=1;break;
      case 'd':case 'i':{int v=va_arg(ap,int);neg=v<0;num=neg?0u-(unsigned)v:(unsigned)v;numeric=1;break;}
      case 'u':num=va_arg(ap,unsigned);numeric=1;break;
      case 'x':case 'X':num=va_arg(ap,unsigned);base=16;numeric=1;break;
      case 'p':num=(uintptr_t)va_arg(ap,void *);base=16;numeric=1;pointer=1;break;
      default:return -1;
    }
    if(numeric){const char *digits=kind=='X'?"0123456789ABCDEF":"0123456789abcdef";do{rev[len++]=digits[num%base];num/=base;}while(num);}
    int pad=width>(int)len+neg+2*pointer?width-(int)len-neg-2*pointer:0;
    if(!left && (!zero||!numeric))while(pad-->0)emit(s,' ');
    if(neg)emit(s,'-');
    if(pointer){emit(s,'0');emit(s,'x');}
    if(!left && zero && numeric)while(pad-->0)emit(s,'0');
    if(numeric){while(len)emit(s,rev[--len]);}else{for(size_t i=0;i<len;++i)emit(s,str[i]);}
    if(left)while(pad-->0)emit(s,' ');
  }
  return s->total>INT32_MAX?-1:(int)s->total;
}
int vsnprintf(char *out,size_t n,const char *fmt,va_list ap){Sink s={out,n,0,0};int r=format(&s,fmt,ap);if(n)out[s.total<n?s.total:n-1]=0;return r;}
int vsprintf(char *out,const char *fmt,va_list ap){return vsnprintf(out,(size_t)-1,fmt,ap);}
int vprintf(const char *fmt,va_list ap){Sink s={NULL,0,0,1};return format(&s,fmt,ap);}
int printf(const char *fmt,...){va_list a;va_start(a,fmt);int r=vprintf(fmt,a);va_end(a);return r;}
int sprintf(char *out,const char *fmt,...){va_list a;va_start(a,fmt);int r=vsprintf(out,fmt,a);va_end(a);return r;}
int snprintf(char *out,size_t n,const char *fmt,...){va_list a;va_start(a,fmt);int r=vsnprintf(out,n,fmt,a);va_end(a);return r;}
#endif
