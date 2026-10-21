/* Original137E0 has eight local bytes then44callee-save bytes.
 * Deep private context448 requires joint/task-stack qualification. */
.equ SPRITE_PRIVATE_RESERVE,448
.text
.globl biwn_native_sprite_create
biwn_native_sprite_create:
lea -8(%sp),%sp
movem.l %d2-%d7/%a2-%a6,-(%sp)
lea -SPRITE_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (52+SPRITE_PRIVATE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_sprite_create_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea SPRITE_PRIVATE_RESERVE(%sp),%sp
movem.l (%sp)+,%d2-%d7/%a2-%a6
lea 8(%sp),%sp
.globl biwn_native_sprite_create_return
biwn_native_sprite_create_return:
rts
.macro sprite_begin
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
move.l %sp,68(%a0)
movea.l 60(%a0),%sp
lea -52(%sp),%sp
.endm
.macro sprite_finish bytes
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (62+\bytes-SPRITE_PRIVATE_RESERVE)(%sp),%a0
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
.globl biwn_native_sprite_create_position_capture
biwn_native_sprite_create_position_capture:
sprite_begin
move.l 44(%a0),%a1
adda.l 20(%a0),%a1
move.l %a1,-(%sp)
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0x105da
sprite_finish 4
.globl biwn_native_sprite_create_allocate_capture
biwn_native_sprite_create_allocate_capture:
sprite_begin
move.l 72(%a0),-(%sp)
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0x152a2
sprite_finish 4
.globl biwn_native_sprite_create_decode_capture
biwn_native_sprite_create_decode_capture:
sprite_begin
move.l 72(%a0),-(%sp)
move.l 28(%a0),-(%sp)
move.l 36(%a0),-(%sp)
move.l #0x6e6a0,-(%sp)
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xe2b8
sprite_finish 16
