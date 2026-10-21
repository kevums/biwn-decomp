/* Private C frame leaves the original public D2 save at entrySP-4 intact. */
.section .text.biwn_native_format_pad,"ax",@progbits
.globl biwn_native_format_pad
biwn_native_format_pad:
lea -72(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea 72(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_format_pad_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea 72(%sp),%sp
rts
