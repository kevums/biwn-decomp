/* Original stack ABI, exact return registers/CCR, compiled arithmetic body.
 * Zero divisors execute a new native DIVU exception path, not original code. */
.section .text.biwn_native_math,"ax",@progbits
.globl biwn_native_multiply,biwn_native_division,biwn_native_remainder
.macro frame_and_call target
move.w %sr,-(%sp)
lea -18(%sp),%sp
move.l %d2,10(%sp)
move.l %d3,14(%sp)
lea (%sp),%a0
move.l %a0,-(%sp)
moveq #0,%d0
move.w 22(%sp),%d0
move.l %d0,-(%sp)
move.l 36(%sp),-(%sp)
move.l 36(%sp),-(%sp)
bsr.w \target
lea 16(%sp),%sp
movea.l 10(%sp),%a0
movea.l 14(%sp),%a1
move.l (%sp),%d0
move.l 4(%sp),%d1
move.w 8(%sp),%ccr
lea 20(%sp),%sp
rts
.endm
biwn_native_multiply:
frame_and_call biwn_native_multiply_result
biwn_native_division:
tst.l 8(%sp)
beq.w biwn_native_division_zero
frame_and_call biwn_native_division_result
biwn_native_remainder:
tst.l 8(%sp)
beq.w biwn_native_remainder_zero
frame_and_call biwn_native_remainder_result
biwn_native_remainder_zero:
move.l 8(%sp),-(%sp)
move.l 8(%sp),-(%sp)
bsr.w biwn_native_division_zero
addq.l #8,%sp
move.l %d1,%d0
rts
biwn_native_division_zero:
movea.l %d2,%a0
movea.l %d3,%a1
clr.w -(%sp)
clr.l %d0
move.l 10(%sp),%d2
.globl biwn_native_division_fault,biwn_native_division_fault_return
biwn_native_division_fault:
divu.w %d2,%d1
biwn_native_division_fault_return:
tst.w 6(%sp)
bpl.s 1f
neg.l %d1
1: tst.w (%sp)+
bpl.s 2f
neg.l %d0
2: move.l %a1,%d3
move.l %a0,%d2
rts
