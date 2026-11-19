#include <am.h>
static int width,height;
void __am_gpu_init(void){uint32_t v=*(volatile uint32_t *)0xa0000100;width=v>>16;height=v&65535;}
void __am_gpu_config(AM_GPU_CONFIG_T *c){*c=(AM_GPU_CONFIG_T){.present=true,.has_accel=false,.width=width,.height=height,.vmemsz=width*height*4};}
void __am_gpu_status(AM_GPU_STATUS_T *s){s->ready=true;}
void __am_gpu_fbdraw(AM_GPU_FBDRAW_T *c){
  volatile uint32_t *fb=(volatile uint32_t *)0xa1000000;
  const uint32_t *pixels=c->pixels;
  // Clip once with wide arithmetic (including extreme signed coordinates).
  // The inner copy then uses only pointers and 32-bit loads/stores on RV32.
  int64_t left=c->x,top=c->y,right=left+c->w,bottom=top+c->h;
  if(left<0)left=0;
  if(top<0)top=0;
  if(right>width)right=width;
  if(bottom>height)bottom=height;
  if(c->w>0 && c->h>0 && right>left && bottom>top){
    int count=(int)(right-left);
    const uint32_t *src=pixels+(size_t)(top-c->y)*(size_t)c->w+(size_t)(left-c->x);
    volatile uint32_t *dst=fb+(size_t)top*width+(size_t)left;
    for(int y=(int)top;y<(int)bottom;y++){
      for(int x=0;x<count;x++)dst[x]=src[x];
      if(y+1<(int)bottom){src+=c->w;dst+=width;}
    }
  }
  if(c->sync)*(volatile uint32_t *)0xa0000104=1;
}
