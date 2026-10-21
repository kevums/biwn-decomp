/* Coordinator ABI/exception wrapper, separate from local Author C.
 * The original successful entry changes only D0/A0/A1 and N/Z/V/C.
 * Empty pool restores the original register/CCR prefix then executes the
 * retained ILLEGAL at DEB4, so its exception PC and frame remain original.
 * No IRQ/cycle equivalence is implied by this synchronous wrapper. */
.section .text.biwn_native_task_create,"ax",@progbits
.globl biwn_native_task_create
.globl biwn_native_task_create_stack
biwn_native_task_create_stack:
move.l 4(%sp),%d0
move.l 8(%sp),%d1
bra.w biwn_native_task_create
biwn_native_task_create:
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
subq.l #4,%sp
lea (%sp),%a0
move.l %a0,-(%sp)
move.l 12(%sp),-(%sp)
move.l 12(%sp),-(%sp)
bsr.w biwn_native_task_create_body
lea 12(%sp),%sp
tst.l %d0
beq.s .Lempty
move.l %d0,4(%sp)
move.l %d0,40(%sp)
movea.l %d0,%a0
lea 0x400(%a0),%a0
move.l %a0,36(%sp)
addq.l #4,%sp
movem.l (%sp)+,%d0-%d7/%a0-%a6
move.w (%sp)+,%ccr
tst.l %d0
rts
.Lempty:
move.l (%sp),36(%sp)
clr.l 40(%sp)
addq.l #4,%sp
movem.l (%sp)+,%d0-%d7/%a0-%a6
move.w (%sp)+,%ccr
cmpa.w #0,%a1
jmp 0xdeb4
