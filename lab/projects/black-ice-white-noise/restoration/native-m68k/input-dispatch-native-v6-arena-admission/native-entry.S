/* Prototype original-style no-stack-argument entry, incoming/result D0.
 * Appended after the prior immutable component. It is not installed at191F4.
 * Caller-saved registers/CCR are measured separately,never silently assumed.
 * A logical C error is an explicit ILLEGAL fixture failure,not a success or
 * a restart after partial effects. Production admission remains unqualified.
 */
.section .native_entry,"ax",@progbits
.globl biwn_native_input_entry
biwn_native_input_entry:
move.l %d0,-(%sp)
pea (%sp)
move.l %d0,-(%sp)
jsr biwn_native_input_fixture
addq.l #8,%sp
tst.l %d0
bne.s biwn_native_input_entry_error
move.l (%sp)+,%d0
rts
.globl biwn_native_input_entry_error
biwn_native_input_entry_error:
illegal
