.equ FRAME_ACQUIRE_RESERVE,512
.section .text.biwn_frame_acquire,"ax",@progbits
.globl biwn_native_frame_acquire
biwn_native_frame_acquire:
link.w %a6,#-4
movem.l %d2-%d7/%a2-%a4,-(%sp)
lea -FRAME_ACQUIRE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (44+FRAME_ACQUIRE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_frame_acquire_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea FRAME_ACQUIRE_RESERVE(%sp),%sp
movem.l -40(%a6),%d2-%d7/%a2-%a4
unlk %a6
.globl biwn_native_frame_acquire_return
biwn_native_frame_acquire_return:
rts

.macro frame_begin
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
move.l %sp,68(%a0)
movea.l 60(%a0),%sp
lea -44(%sp),%sp
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
.endm
.macro frame_finish nargs
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (62+4*\nargs-FRAME_ACQUIRE_RESERVE)(%sp),%a0
movea.l %sp,%a1
moveq #14,%d0
1:
move.l (%a1)+,(%a0)+
dbra %d0,1b
move.w 60(%sp),6(%a0)
movea.l 8(%a0),%sp
lea 4(%sp),%sp
movem.l (%sp)+,%d2-%d7/%a2-%a6
rts
.endm
.globl biwn_frame_acquire_divs_capture
biwn_frame_acquire_divs_capture:
frame_begin
.globl biwn_frame_acquire_divs_instruction
biwn_frame_acquire_divs_instruction:
divs.w %d3,%d0
frame_finish 0
.globl biwn_frame_acquire_load_capture
biwn_frame_acquire_load_capture:
frame_begin
clr.l -(%sp)
move.l %d5,-(%sp)
pea -4(%a6)
move.l %a4,-(%sp)
pea 0(%a1,%a2.l)
jsr 0x1b044
.globl biwn_frame_acquire_after_load
biwn_frame_acquire_after_load:
frame_finish 5
