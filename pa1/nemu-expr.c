// Integration of the course evaluator into NEMU ics2024 (RV32).
#include <isa.h>
#include <memory/paddr.h>
#include "course_expr.h"
void init_regex(void) {} // A handwritten lexer is used instead of POSIX regex.
static uint32_t read_register(const char *name,bool *ok) {
  return isa_reg_str2val(name,ok);
}
static uint32_t read_memory(uint32_t address,bool *ok) {
  *ok=address<=UINT32_MAX-3 && in_pmem(address) && in_pmem(address+3);
  return *ok?paddr_read(address,4):0;
}
word_t expr(char *text,bool *success) {
  return course_expr(text,success,read_register,read_memory);
}
