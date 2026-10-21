/* Newly assembled source kernel for the existing word-stride marker repair.
 * C ABI: r frame pointer at4(SP); return1=valid16word marker,0=retry.
 * Updates semantic D0,D1,A2,CCR in frame. No helper calls or host services.
 * Source controls all busy/read/copy/completion behavior in C.
 */
.section .text.biwn_native_resource_load_scan,"ax",@progbits
.globl biwn_native_load_scan
biwn_native_load_scan:
movem.l %d2/%a2-%a3,-(%sp)
movea.l 16(%sp),%a3
movem.l (%a3),%d0-%d2
movea.l 40(%a3),%a2
move.w 66(%a3),%ccr
.Lscan:
cmp.l (%a2)+,%d2
beq.s .Lmarker
subq.l #2,%a2
cmpa.l #0x1c7fff,%a2
bcs.s .Lscan
clr.l 0xbd848
bra.s .Lretry
.Lmarker:
moveq #1,%d0
.Lrun:
cmp.l (%a2)+,%d2
bne.s .Lscan
addq.l #1,%d0
moveq #15,%d1
cmp.l %d0,%d1
bge.s .Lrun
cmpa.l #0x1c8000,%a2
bgt.s .Lretry
bsr.s .Lcapture
moveq #1,%d0
bra.s .Lreturn
.Lretry:
bsr.s .Lcapture
moveq #0,%d0
.Lreturn:
movem.l (%sp)+,%d2/%a2-%a3
rts
.Lcapture:
move.w %sr,66(%a3)
movem.l %d0-%d1,(%a3)
move.l %a2,40(%a3)
rts
