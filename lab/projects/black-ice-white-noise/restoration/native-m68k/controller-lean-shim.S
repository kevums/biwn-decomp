/* Coordinator lean ABI boundary. Accepted compiler body is statically
 * restricted to X-preserving moves/bitwise/ROR/ROL/return instructions.
 * GCC preserves D2-D7/A2-A6; MOVEM preserves CCR. TST returns edge N/Z,
 * clears V/C and preserves X. Full native SR gates remain required. */
.section .text.biwn_native_controller_poll,"ax",@progbits
.globl biwn_native_controller_poll
biwn_native_controller_poll:
movem.l %d0-%d1/%a0-%a1,-(%sp)
bsr.w biwn_native_controller_poll_body
tst.l %d0
movem.l (%sp)+,%d0-%d1/%a0-%a1
rts
