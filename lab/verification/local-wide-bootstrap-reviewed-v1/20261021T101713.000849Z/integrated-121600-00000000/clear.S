.text
.globl wide_startup_finalize
wide_startup_finalize:
lea 0xe06c0,%a0
move.w #30415,%d0
wide_stage_clear:
clr.l (%a0)+
dbra %d0,wide_stage_clear
movem.l (%sp)+,%d0-%d7/%a0-%a6
move.w #0x2700,%sr
jmp 0x400a
