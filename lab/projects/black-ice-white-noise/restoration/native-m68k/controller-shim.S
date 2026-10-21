/* Coordinator C ABI boundary. Original E4C0 preserves every register and X;
 * N/Z follow the final press-edge long store, V/C clear. C returns edge.
 * GCC preserves D2-D7/A2-A6; save volatile D0/D1/A0/A1 explicitly. */
.section .text.biwn_native_controller_poll,"ax",@progbits
.globl biwn_native_controller_poll
biwn_native_controller_poll:
move.w %sr,-(%sp)
movem.l %d0-%d1/%a0-%a1,-(%sp)
bsr.w biwn_native_controller_poll_body
tst.l %d0
move.w %sr,%d1
andi.w #15,%d1
move.w 16(%sp),%d0
andi.w #16,%d0
or.w %d0,%d1
move.w %d1,16(%sp)
movem.l (%sp)+,%d0-%d1/%a0-%a1
move.w (%sp)+,%ccr
rts
