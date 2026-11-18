#include <am.h>
void __am_input_keybrd(AM_INPUT_KEYBRD_T *k){
  uint32_t value=*(volatile uint32_t *)0xa0000060;
  k->keydown=(value&0x8000)!=0;k->keycode=value&0x7fff;
}
