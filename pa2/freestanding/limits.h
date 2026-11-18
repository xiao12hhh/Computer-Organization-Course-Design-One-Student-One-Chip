/* Integer limits for the freestanding course toolchain, from GCC target macros. */
#ifndef COURSE_LIMITS_H
#define COURSE_LIMITS_H
#define CHAR_BIT __CHAR_BIT__
#define SCHAR_MAX __SCHAR_MAX__
#define SCHAR_MIN (-SCHAR_MAX-1)
#define UCHAR_MAX (2U*SCHAR_MAX+1U)
#ifdef __CHAR_UNSIGNED__
#define CHAR_MIN 0
#define CHAR_MAX UCHAR_MAX
#else
#define CHAR_MIN SCHAR_MIN
#define CHAR_MAX SCHAR_MAX
#endif
#define SHRT_MAX __SHRT_MAX__
#define SHRT_MIN (-SHRT_MAX-1)
#define USHRT_MAX (2U*SHRT_MAX+1U)
#define INT_MAX __INT_MAX__
#define INT_MIN (-INT_MAX-1)
#define UINT_MAX (2U*INT_MAX+1U)
#define LONG_MAX __LONG_MAX__
#define LONG_MIN (-LONG_MAX-1L)
#define ULONG_MAX (2UL*LONG_MAX+1UL)
#define LLONG_MAX __LONG_LONG_MAX__
#define LLONG_MIN (-LLONG_MAX-1LL)
#define ULLONG_MAX (2ULL*LLONG_MAX+1ULL)
#endif
