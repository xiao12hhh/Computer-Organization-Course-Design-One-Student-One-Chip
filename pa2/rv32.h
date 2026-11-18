#ifndef COURSE_RV32_H
#define COURSE_RV32_H
#include <stdint.h>
typedef uint32_t (*rv_read)(uint32_t,int);
typedef void (*rv_write)(uint32_t,int,uint32_t);
enum {RV_OK,RV_BREAK,RV_ILLEGAL};
int rv32_execute(uint32_t,uint32_t,uint32_t[32],uint32_t *,rv_read,rv_write);
#endif
