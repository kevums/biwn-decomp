/* Coordinator exact original public prologue and target dependency capture. */
.section .text.biwn_native_resource_release,"ax",@progbits
.globl biwn_native_resource_release
biwn_native_resource_release:
movem.l %d2-%d3/%a2,-(%sp)
lea -72(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea 84(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_resource_release_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea 72(%sp),%sp
movem.l (%sp)+,%d2-%d3/%a2
rts
.globl biwn_native_release_free_capture
biwn_native_release_free_capture:
movem.l %a2-%a4,-(%sp)
movea.l 16(%sp),%a4
movem.l (%a4),%d0-%d1
movea.l 32(%a4),%a0
movea.l 36(%a4),%a1
movea.l #0x15b534,%a2
movea.l 44(%a4),%a3
move.w #0,%ccr
move.l 20(%sp),-(%sp)
jsr 0x1545c
move.w %sr,-(%sp)
movem.l %d0-%d1,(%a4)
move.l %a0,32(%a4)
move.l %a1,36(%a4)
move.w (%sp)+,66(%a4)
lea 4(%sp),%sp
movem.l (%sp)+,%a2-%a4
rts
