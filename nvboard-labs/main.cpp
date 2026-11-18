#include <nvboard.h>
#include <verilated.h>
#include <Vlab_top.h>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <SDL.h>
void nvboard_bind_all_pins(Vlab_top*);
int main(int argc,char**argv) {
  Verilated::commandArgs(argc,argv);
  Vlab_top top;
  nvboard_bind_all_pins(&top);nvboard_init();
  top.rst=1;
  for(int i=0;i<10;i++){top.clk=0;top.eval();top.clk=1;top.eval();}
  top.rst=0;
  // Integration test sends real SDL events through NVBoard's switch/keyboard
  // handlers and checks RTL outputs, including all PS/2 serialization stages.
  if(argc>2 && !std::strcmp(argv[1],"--check")) {
    auto advance=[&](){SDL_Delay(25);for(int i=0;i<100000;i++){
      nvboard_update();top.clk=0;top.eval();top.clk=1;top.eval();}};
    auto mouse=[&](int x,int y,bool down){SDL_Event ev{};ev.type=down?SDL_MOUSEBUTTONDOWN:SDL_MOUSEBUTTONUP;
      ev.button.x=x;ev.button.y=y;ev.button.button=SDL_BUTTON_LEFT;SDL_PushEvent(&ev);advance();};
    auto key=[&](bool down){SDL_Event ev{};ev.type=down?SDL_KEYDOWN:SDL_KEYUP;
      ev.key.keysym.scancode=SDL_SCANCODE_A;ev.key.keysym.sym=SDLK_a;SDL_PushEvent(&ev);advance();};
    auto require=[&](bool ok,const char *why){if(!ok){std::fprintf(stderr,"NVBoard check failed: %s\n",why);std::exit(1);}};
    advance();int mode=std::atoi(argv[2]);
    if(mode==11){
      mouse(520,420,true);mouse(520,420,false); // SW0: run
      require((top.ledr&255)==55 && top.seg0==0x49 && top.seg1==0x49,"CPU decimal 55");
    } else if(mode==6){
      require((top.ledr&255)==1,"LFSR reset");
      mouse(535,265,true);mouse(535,265,false);
      require((top.ledr&255)==128,"LFSR button step");
    } else if(mode==7){
      key(true);require(top.seg0==0x63 && top.seg1==0x9f && top.seg2==0x9f && top.seg3==0x41 && top.seg4==0x9f,"A make scan/ASCII/count");
      key(true);require(top.seg4==0x9f,"A repeat count");
      key(false);require(top.seg0==255 && top.seg1==255 && top.seg2==255 && top.seg3==255,"A break blank");
    } else require(false,"unknown mode");
    require(top.seg6==255 && top.seg7==255,"unused digits blank");
    top.final();nvboard_quit();std::puts("PASS NVBoard SDL event integration");return 0;
  }
  unsigned long long limit=argc>1?std::strtoull(argv[1],nullptr,10):0,cycles=0;
  while(!Verilated::gotFinish() && (!limit || cycles<limit)) {
    nvboard_update();top.clk=0;top.eval();top.clk=1;top.eval();++cycles;
  }
  top.final();nvboard_quit();return 0;
}
