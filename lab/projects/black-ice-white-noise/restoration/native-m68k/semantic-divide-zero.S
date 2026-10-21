/* Bridge only the declared DIVU-zero semantic state to a real new CPU fault.
 * Bookkeeping is below virtualSP-496, outside original public frames and
 * below the bounded compiled C call frames. C ABI callee-saves are restored.
 * IRQ disabled/inert RTE fixtures; arbitrary handlers/concurrency unproved. */
.section .text.biwn_native_semantic_zero,"ax",@progbits
.globl biwn_native_semantic_divide_zero
biwn_native_semantic_divide_zero:
movem.l %d2-%d7/%a2-%a6,-(%sp)
movea.l 48(%sp),%a0
movea.l 60(%a0),%a1
move.l %sp,-512(%a1)
move.l %a0,-508(%a1)
move.w 66(%a0),%ccr
movea.l 60(%a0),%sp
movem.l (%a0),%d0-%d7/%a0-%a6
.globl biwn_native_semantic_divide_fault
biwn_native_semantic_divide_fault:
divu.w %d2,%d1
/* Capture semantic flags BEFORE any ordinary MOVE changes them. */
move.w %sr,-496(%sp)
move.l %a0,-504(%sp)
movea.l -508(%sp),%a0
movem.l %d0-%d7/%a0-%a6,(%a0)
move.l -504(%sp),32(%a0)
move.l %sp,60(%a0)
moveq #0,%d0
move.w -496(%sp),%d0
move.l %d0,64(%a0)
movea.l -512(%sp),%sp
movem.l (%sp)+,%d2-%d7/%a2-%a6
rts
