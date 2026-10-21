/* Numeric C-ABI adapter for RNG's private math_result calls.
 * Arguments: return,a,b,incoming_SR,out. Incoming_SR and out.SR are unused
 * by this numeric backend; RNG C computes its own final original CCR.
 * Public runtime entry contracts are separately source-assembled at their
 * original addresses. This bridge is not their full-flag C-result API. */
.section .text.biwn_rng_fast_math,"ax",@progbits
.macro numeric_entry name,target
.globl \name
\name:
move.l %a2,-(%sp)
movea.l 20(%sp),%a2
move.l 12(%sp),-(%sp)
move.l 12(%sp),-(%sp)
jsr \target
lea 8(%sp),%sp
move.l %d0,(%a2)
move.l %d1,4(%a2)
movea.l (%sp)+,%a2
rts
.endm
numeric_entry biwn_native_fast_multiply_result,biwn_runtime_multiply
numeric_entry biwn_native_fast_division_result,biwn_runtime_division
numeric_entry biwn_native_fast_remainder_result,biwn_runtime_remainder
