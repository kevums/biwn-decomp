.section .text.biwn_frame_single_lean,"ax",@progbits
.globl biwn_frame_single_lean
biwn_frame_single_lean:
move.l %d2,-(%sp)
move.l %d1,-(%sp)
move.l %a1,-(%sp)
moveq #0,%d0
move.w 16(%sp),%d0
move.l %d0,-(%sp)
bsr.w biwn_frame_single_lean_body
lea 4(%sp),%sp
move.l %d0,%d2
lsr.l #8,%d0
movea.l (%sp)+,%a1
move.l (%sp)+,%d1
move.w %d0,%d1
cmpi.w #36,%d0
bne.s 1f
moveq #35,%d0
1:
lsl.l #2,%d0
lea 0x15b4a0,%a0
move.w %d2,%ccr
move.l (%sp)+,%d2
rts
