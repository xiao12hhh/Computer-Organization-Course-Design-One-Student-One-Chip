// Process-local test hook: inject A down/up and capture real SDL framebuffer.
// Enabled only via explicit LD_PRELOAD plus COURSE_KEYS / COURSE_SCREENSHOT.
#define _GNU_SOURCE
#include <SDL2/SDL.h>
#include <SDL2/SDL_image.h>
#include <dlfcn.h>
#include <stdlib.h>
int SDL_PollEvent(SDL_Event *event){
  static int sent;
  int (*real_poll)(SDL_Event *)=dlsym(RTLD_NEXT,"SDL_PollEvent");
  if(getenv("COURSE_KEYS") && sent<2 && event){
    SDL_zero(*event);event->type=sent?SDL_KEYUP:SDL_KEYDOWN;
    event->key.keysym.scancode=SDL_SCANCODE_A;event->key.state=sent?SDL_RELEASED:SDL_PRESSED;
    ++sent;return 1;
  }
  return real_poll(event);
}
void SDL_RenderPresent(SDL_Renderer *renderer){
  void (*real_present)(SDL_Renderer *)=dlsym(RTLD_NEXT,"SDL_RenderPresent");
  const char *path=getenv("COURSE_SCREENSHOT");
  if(path){
    int w,h;SDL_GetRendererOutputSize(renderer,&w,&h);
    SDL_Surface *surface=SDL_CreateRGBSurfaceWithFormat(0,w,h,32,SDL_PIXELFORMAT_ARGB8888);
    if(surface){if(SDL_RenderReadPixels(renderer,NULL,SDL_PIXELFORMAT_ARGB8888,surface->pixels,surface->pitch)==0)IMG_SavePNG(surface,path);SDL_FreeSurface(surface);}
  }
  real_present(renderer);
}
