// Process-local native preview smoke test. Only loaded by test_native.py.
#define _GNU_SOURCE
#include <SDL2/SDL.h>
#include <SDL2/SDL_image.h>
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>

int SDL_WaitEvent(SDL_Event *event) {
  static unsigned next;
  static const struct { Uint32 at; Uint32 type; SDL_Scancode key; } script[] = {
    {1000, SDL_KEYDOWN, SDL_SCANCODE_I}, {1200, SDL_KEYUP, SDL_SCANCODE_I},
    {4500, SDL_KEYDOWN, SDL_SCANCODE_D}, {5000, SDL_KEYDOWN, SDL_SCANCODE_J},
    {5500, SDL_KEYUP, SDL_SCANCODE_J}, {6000, SDL_KEYUP, SDL_SCANCODE_D},
    {7500, SDL_QUIT, SDL_SCANCODE_UNKNOWN}
  };
  for (;;) {
    if (next < sizeof(script)/sizeof(script[0]) && SDL_GetTicks() >= script[next].at) {
      SDL_zero(*event);
      event->type = script[next].type;
      event->key.keysym.scancode = script[next].key;
      event->key.state = event->type == SDL_KEYDOWN ? SDL_PRESSED : SDL_RELEASED;
      ++next;
      return 1;
    }
    if (SDL_WaitEventTimeout(event, 10)) return 1;
  }
}

int SDL_UpdateWindowSurface(SDL_Window *window) {
  static int captured;
  int (*real_update)(SDL_Window *) = dlsym(RTLD_NEXT, "SDL_UpdateWindowSurface");
  const char *prefix = getenv("COURSE_NATIVE_CAPTURE");
  if (prefix && captured < 2 && SDL_GetTicks() >= (captured ? 7000u : 800u)) {
    char path[1024];
    snprintf(path, sizeof(path), "%s-%s.png", prefix, captured ? "playing" : "title");
    if (IMG_SavePNG(SDL_GetWindowSurface(window), path) == 0) ++captured;
  }
  return real_update(window);
}
