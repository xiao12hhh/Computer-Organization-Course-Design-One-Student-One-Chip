#include <am.h>
#include <klib.h>
int main(void){
  ioe_init();printf("MMIO hello\n");
  uint64_t begin=io_read(AM_TIMER_UPTIME).us,previous=begin,now=begin;
  while(now-begin<20000){now=io_read(AM_TIMER_UPTIME).us;assert(now>=previous);previous=now;}
#ifndef COURSE_NPC
  AM_GPU_CONFIG_T cfg=io_read(AM_GPU_CONFIG);assert(cfg.width==400 && cfg.height==300);
  uint32_t pixels[4]={0x112233,0x445566,0x778899,0xaabbcc};
  io_write(AM_GPU_FBDRAW,-1,-1,pixels,2,2,true);
  assert(*(volatile uint32_t *)0xa1000000==pixels[3]);
  io_write(AM_GPU_FBDRAW,399,299,pixels,2,2,true);
  assert(*(volatile uint32_t *)(0xa1000000+4*(400*300-1))==pixels[0]);
  // Both sides clipped: retain the source stride when advancing a row.
  static uint32_t wide[804];
  for(int i=0;i<804;i++)wide[i]=i+1;
  io_write(AM_GPU_FBDRAW,-1,10,wide,402,2,false);
  volatile uint32_t *fb=(volatile uint32_t *)0xa1000000;
  assert(fb[10*400]==2 && fb[10*400+399]==401);
  assert(fb[11*400]==404 && fb[11*400+399]==803);
  io_write(AM_GPU_FBDRAW,(-2147483647-1),0,pixels,2,2,false);
  io_write(AM_GPU_FBDRAW,2147483647,0,pixels,2,2,false);
  io_write(AM_GPU_FBDRAW,0,(-2147483647-1),pixels,2,2,false);
  io_write(AM_GPU_FBDRAW,0,2147483647,pixels,2,2,false);
  io_write(AM_GPU_FBDRAW,0,0,pixels,0,2,false);
  io_write(AM_GPU_FBDRAW,0,0,pixels,2,-1,false);
  assert(fb[0]==pixels[3] && fb[400*300-1]==pixels[0]);
  AM_INPUT_KEYBRD_T k=io_read(AM_INPUT_KEYBRD);
#ifdef COURSE_KEY_TEST
  while(k.keycode==AM_KEY_NONE)k=io_read(AM_INPUT_KEYBRD);
  assert(k.keycode==AM_KEY_A && k.keydown);
  do{k=io_read(AM_INPUT_KEYBRD);}while(k.keycode==AM_KEY_NONE);
  assert(k.keycode==AM_KEY_A && !k.keydown);
  printf("KEYBOARD PASS down/up\n");
#else
  assert(k.keycode==AM_KEY_NONE);
#endif
#endif
  printf("MMIO PASS timer=%u us\n",(unsigned)(now-begin));return 0;
}
