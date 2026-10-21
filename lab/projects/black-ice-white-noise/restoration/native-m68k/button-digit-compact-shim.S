/* Coordinator compact-only ABI. C may clobber CCR and caller-saved A0/A1.
 * Legacy keypad results are1..9,-1,or incomingD0 with lowWORD cleared.
 * TST.W reconstructs originalN/Z/V/C for every result; incomingX is restored.
 * The fixed20byte entry slot keeps startup_finalize at native26's address.
 */
.section .text.biwn_native_button_digit,"ax",@progbits
.globl biwn_native_button_digit
biwn_native_button_digit:
bra.w biwn_native_button_digit_compact
.rept 8
nop
.endr
.if (. - biwn_native_button_digit) != 20
.error "Keypad entry slot must remain20bytes"
.endif
.section .text.biwn_native_button_digit_compact,"ax",@progbits
.globl biwn_native_button_digit_compact
biwn_native_button_digit_compact:
movem.l %a0-%a1,-(%sp)
move.w %sr,-(%sp)
move.l %d0,-(%sp)
move.l 18(%sp),-(%sp)
bsr.w biwn_button_digit
/* The private C argument is the original once-read mask. */
movem.l (%sp),%d1
lea 8(%sp),%sp
move.w (%sp)+,%ccr
movem.l (%sp)+,%a0-%a1
tst.w %d0
rts
