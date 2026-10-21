/* Coordinator frame and original single-instruction CLR.L bus boundary. */
.section .text.biwn_native_free,"ax",@progbits
.globl biwn_native_free
biwn_native_free:
lea -96(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea 96(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_free_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea 96(%sp),%sp
rts
.globl biwn_native_free_clear32
biwn_native_free_clear32:
movea.l 4(%sp),%a0
clr.l (%a0)
rts
