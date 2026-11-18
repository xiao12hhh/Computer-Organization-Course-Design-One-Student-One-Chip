#include <am.h>
static uint64_t boot;
static uint64_t now(void){
  // Read high first: the NEMU/NPC device snapshots both halves on that access.
  uint32_t hi=*(volatile uint32_t *)0xa000004c;
  uint32_t lo=*(volatile uint32_t *)0xa0000048;
  return ((uint64_t)hi<<32)|lo;
}
void __am_timer_init(void){boot=now();}
void __am_timer_uptime(AM_TIMER_UPTIME_T *t){t->us=now()-boot;}
void __am_timer_rtc(AM_TIMER_RTC_T *t){*t=(AM_TIMER_RTC_T){.year=1900};}
