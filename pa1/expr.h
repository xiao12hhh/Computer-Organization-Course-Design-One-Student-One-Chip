#ifndef COURSE_EXPR_H
#define COURSE_EXPR_H
#include <stdbool.h>
#include <stdint.h>
typedef uint32_t (*expr_register_fn)(const char *,bool *);
typedef uint32_t (*expr_memory_fn)(uint32_t,bool *);
uint32_t course_expr(const char *,bool *,expr_register_fn,expr_memory_fn);
#endif
