/* Coordinator adaptation of the accepted guided local-model ABI shim.
 * Relative call permits the game allocator to move the whole component. */
.section .text.biwn_native_button_digit,"ax",@progbits
.globl biwn_native_button_digit
biwn_native_button_digit:
move.l %d0,-(%sp)
move.l 8(%sp),-(%sp)
bsr.w biwn_button_digit
addq.l #8,%sp
movem.l 4(%sp),%d1
rts
