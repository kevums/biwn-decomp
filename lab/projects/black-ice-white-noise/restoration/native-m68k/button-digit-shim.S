.section .text.biwn_native_button_digit,"ax",@progbits
.globl biwn_native_button_digit
biwn_native_button_digit:
move.l %d0,-(%sp)
move.l 8(%sp),-(%sp)
jsr biwn_button_digit
addq.l #8,%sp
rts
