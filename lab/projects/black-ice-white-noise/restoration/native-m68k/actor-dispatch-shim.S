/* Coordinator original-ABI adapter. Helpers use the original guest SP.
 * The fixed private gap is experimental until real nested stack tests pass. */
.equ ACTOR_PRIVATE_RESERVE,256
.text
.globl biwn_native_actor_dispatch
biwn_native_actor_dispatch:
movem.l %d2-%d5,-(%sp)
lea -ACTOR_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (16+ACTOR_PRIVATE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_actor_dispatch_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea ACTOR_PRIVATE_RESERVE(%sp),%sp
movem.l (%sp)+,%d2-%d5
.globl biwn_native_actor_dispatch_return
biwn_native_actor_dispatch_return:
rts
.macro actor_begin
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
move.l %sp,68(%a0)
movea.l 60(%a0),%sp
lea -16(%sp),%sp
.endm
.macro actor_finish bytes
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (62+\bytes-ACTOR_PRIVATE_RESERVE)(%sp),%a0
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
.globl biwn_native_actor_dispatch_actor_capture
biwn_native_actor_dispatch_actor_capture:
actor_begin
move.w 10(%a0),-(%sp)
move.l 12(%a0),-(%sp)
move.w 18(%a0),-(%sp)
move.l 20(%a0),-(%sp)
move.w 6(%a0),-(%sp)
move.w 38(%a0),-(%sp)
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0x134dc
actor_finish 16
.globl biwn_native_actor_dispatch_sprite_capture
biwn_native_actor_dispatch_sprite_capture:
actor_begin
move.w 10(%a0),-(%sp)
move.l 12(%a0),-(%sp)
move.w 18(%a0),-(%sp)
move.l 20(%a0),-(%sp)
move.w 38(%a0),-(%sp)
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0x137e0
actor_finish 14
