/* Original-facing public roots; movement->collision is an internal C call.
 * Context r0..14=D/A,r15=logical workingSP,r16=SR,r17=Ccontinuation,
 * r18=collision entry,r19=owning public root. Provisional320private gap. */
.equ CHAIN_PRIVATE_RESERVE,320
.text
.macro chain_root body,entry,savebytes
lea -CHAIN_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (\savebytes+CHAIN_PRIVATE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l #\entry,72(%sp)
move.l #\entry,76(%sp)
move.l %sp,-(%sp)
bsr.w \body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea CHAIN_PRIVATE_RESERVE(%sp),%sp
.endm
.globl biwn_native_actor_move
biwn_native_actor_move:
movem.l %d2-%d7/%a2-%a5,-(%sp)
chain_root biwn_actor_chain_move_body,0x13c9a,40
movem.l (%sp)+,%d2-%d7/%a2-%a5
.globl biwn_native_actor_move_return
biwn_native_actor_move_return:
rts
.globl biwn_native_actor_collision_outdoor
biwn_native_actor_collision_outdoor:
movem.l %d2/%a2,-(%sp)
chain_root biwn_actor_chain_collision_body,0x13b5a,8
movem.l (%sp)+,%d2/%a2
.globl biwn_native_actor_collision_outdoor_return
biwn_native_actor_collision_outdoor_return:
rts
.globl biwn_native_actor_collision_indoor
biwn_native_actor_collision_indoor:
movem.l %a2,-(%sp)
chain_root biwn_actor_chain_collision_body,0x13bb0,4
movem.l (%sp)+,%a2
.globl biwn_native_actor_collision_indoor_return
biwn_native_actor_collision_indoor_return:
rts

/* Source-owned C ABI boundary. Shadow logicalSP includes the virtual original
 * collision JSR. Actual CPU uses its private C stack here, not the original ABI.
 * The markers allow explicit virtual CPU-context comparisons in the oracle. */
.globl biwn_actor_chain_collision_call
biwn_actor_chain_collision_call:
move.l 4(%sp),-(%sp)
bsr.w biwn_actor_chain_collision_body
lea 4(%sp),%sp
.globl biwn_actor_chain_collision_call_return
biwn_actor_chain_collision_call_return:
rts

.macro chain_begin
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
move.l %sp,68(%a0)
movea.l 60(%a0),%sp
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
.endm
.macro chain_finish bytes
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (62+\bytes-CHAIN_PRIVATE_RESERVE)(%sp),%a0
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
.macro bridge symbol,target,bytes
.globl \symbol
\symbol:
chain_begin
jsr \target
chain_finish \bytes
.endm
bridge biwn_native_actor_move_direction_capture,0x13440,4
bridge biwn_native_actor_move_submit_capture,0xe220,20
bridge biwn_native_actor_collision_outside_index_capture,0x1039c,6
bridge biwn_native_actor_collision_outside_scan_capture,0x102c4,4
bridge biwn_native_actor_collision_inside_outside_capture,0x1028e,4
bridge biwn_native_actor_collision_inside_index_capture,0x10652,6
/* Relative to movement's40byte saves, include10packed args,virtualJSR4,
 * collision's8or4saves and the geometry arguments. */
bridge biwn_actor_chain_outside_index_capture,0x1039c,28
bridge biwn_actor_chain_outside_scan_capture,0x102c4,26
bridge biwn_actor_chain_inside_outside_capture,0x1028e,22
bridge biwn_actor_chain_inside_index_capture,0x10652,24
