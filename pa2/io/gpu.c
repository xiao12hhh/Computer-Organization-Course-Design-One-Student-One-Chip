#include <am.h>
static int width,height;
void __am_gpu_init(void){uint32_t v=*(volatile uint32_t *)0xa0000100;width=v>>16;height=v&65535;}
void __am_gpu_config(AM_GPU_CONFIG_T *c){*c=(AM_GPU_CONFIG_T){.present=true,.has_accel=false,.width=width,.height=height,.vmemsz=width*height*4};}
void __am_gpu_status(AM_GPU_STATUS_T *s){s->ready=true;}
void __am_gpu_fbdraw(AM_GPU_FBDRAW_T *c){
  volatile uint32_t *fb=(volatile uint32_t *)0xa1000000;
  const uint32_t *pixels=c->pixels;
  for(int y=0;y<c->h;y++)for(int x=0;x<c->w;x++){
    int64_t dx=(int64_t)c->x+x,dy=(int64_t)c->y+y;
    if(dx>=0 && dx<width && dy>=0 && dy<height)fb[dy*width+dx]=pixels[(size_t)y*c->w+x];
  }
  if(c->sync)*(volatile uint32_t *)0xa0000104=1;
}
