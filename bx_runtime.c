/* This should be in a file such as: bx_runtime.c */
#include <stdio.h>
#include <stdint.h>
/* Note: TAC int == C int64_t
This is because C int is usually only 32 bits. */
void __bx_print_int(int64_t x) { printf("%ld\n", x); }
void __bx_print_bool(int64_t b) { printf(b == 0 ? "false\n" : "true\n"); }