#include <Vboard_top.h>
#include <nvboard.h>
#include <verilated.h>
#include <cstdlib>
void nvboard_bind_all_pins(Vboard_top*);
int main(int argc,char** argv) {
  Verilated::commandArgs(argc,argv);
  Vboard_top top;
  nvboard_bind_all_pins(&top);
  nvboard_init();
  top.rst=1;
  for(int i=0;i<10;i++){top.clk=0;top.eval();top.clk=1;top.eval();}
  top.rst=0;
  // Optional bounded run for environment smoke checks; default stays interactive.
  const long limit=argc>1?std::strtol(argv[1],nullptr,10):0;
  long cycles=0;
  while(!Verilated::gotFinish() && (!limit || cycles<limit)) {
    nvboard_update(); top.clk=0; top.eval(); top.clk=1; top.eval(); ++cycles;
  }
  top.final(); nvboard_quit();
}
