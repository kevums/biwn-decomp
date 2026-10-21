/* Original13C9Aroot has40saved bytes; r15tracks original workingSP.
 * Captures use real guest JSR/RTS and copy actual helper outputs. */
.equ MOVE_PRIVATE_RESERVE,448
.text
.globl biwn_native_actor_move
biwn_native_actor_move:
movem.l %d2-%d7/%a2-%a5,-(%sp)
lea -MOVE_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (40+MOVE_PRIVATE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_actor_move_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea MOVE_PRIVATE_RESERVE(%sp),%sp
movem.l (%sp)+,%d2-%d7/%a2-%a5
.globl biwn_native_actor_move_return
biwn_native_actor_move_return:
rts
.macro move_begin
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
move.l %sp,68(%a0)
movea.l 60(%a0),%sp
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
.endm
.macro move_finish bytes
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (62+\bytes-MOVE_PRIVATE_RESERVE)(%sp),%a0
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
.globl biwn_native_actor_move_direction_capture
biwn_native_actor_move_direction_capture:
move_begin
jsr 0x13440
move_finish 4
.globl biwn_native_actor_move_submit_capture
biwn_native_actor_move_submit_capture:
move_begin
jsr 0xe220
move_finish 20
.globl biwn_native_actor_move_outdoor_capture
biwn_native_actor_move_outdoor_capture:
move_begin
jsr 0x13b5a
move_finish 10
.globl biwn_native_actor_move_indoor_capture
biwn_native_actor_move_indoor_capture:
move_begin
jsr 0x13bb0
move_finish 10
