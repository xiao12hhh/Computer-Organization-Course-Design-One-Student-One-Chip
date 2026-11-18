#include <am.h>
#include <klib-macros.h>
extern char _heap_start,_pmem_start;
int main(const char *args);
Area heap=RANGE(&_heap_start,(uintptr_t)&_pmem_start+128*1024*1024);
static const char mainargs[MAINARGS_MAX_LEN]=TOSTRING(MAINARGS_PLACEHOLDER);
void putch(char c){*(volatile unsigned char *)0x10000000=(unsigned char)c;}
void halt(int code){asm volatile("mv a0, %0; ebreak"::"r"(code):"a0");for(;;);}
void _trm_init(void){halt(main(mainargs));}
