/* Coordinator native target frame, exact public-stack save slots in C body. */
.section .text.biwn_native_copy,"ax",@progbits
.macro copy_entry name, order
.globl \name
\name:
lea -96(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea 96(%sp),%a0
move.l %a0,60(%sp)
move.l #\order,68(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_copy_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea 96(%sp),%sp
rts
.endm
copy_entry biwn_native_copy_source_first,0
copy_entry biwn_native_copy_destination_first,1
