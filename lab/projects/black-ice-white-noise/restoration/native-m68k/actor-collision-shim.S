/* Original root save areas8outdoor/4indoor. Nested private reserve provisional. */
.equ COLLISION_PRIVATE_RESERVE,704
.text
.macro collision_root entry,savebytes
lea -COLLISION_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (\savebytes+COLLISION_PRIVATE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l #\entry,72(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_actor_collision_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea COLLISION_PRIVATE_RESERVE(%sp),%sp
.endm
.globl biwn_native_actor_collision_outdoor
biwn_native_actor_collision_outdoor:
movem.l %d2/%a2,-(%sp)
collision_root 0x13b5a,8
movem.l (%sp)+,%d2/%a2
.globl biwn_native_actor_collision_outdoor_return
biwn_native_actor_collision_outdoor_return:
rts
.globl biwn_native_actor_collision_indoor
biwn_native_actor_collision_indoor:
movem.l %a2,-(%sp)
collision_root 0x13bb0,4
movem.l (%sp)+,%a2
.globl biwn_native_actor_collision_indoor_return
biwn_native_actor_collision_indoor_return:
rts
.macro collision_begin
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
move.l %sp,68(%a0)
movea.l 60(%a0),%sp
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
.endm
.macro collision_finish bytes
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (62+\bytes-COLLISION_PRIVATE_RESERVE)(%sp),%a0
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
.globl biwn_native_actor_collision_outside_index_capture
biwn_native_actor_collision_outside_index_capture:
collision_begin
jsr 0x1039c
collision_finish 6
.globl biwn_native_actor_collision_outside_scan_capture
biwn_native_actor_collision_outside_scan_capture:
collision_begin
jsr 0x102c4
collision_finish 4
.globl biwn_native_actor_collision_inside_outside_capture
biwn_native_actor_collision_inside_outside_capture:
collision_begin
jsr 0x1028e
collision_finish 4
.globl biwn_native_actor_collision_inside_index_capture
biwn_native_actor_collision_inside_index_capture:
collision_begin
jsr 0x10652
collision_finish 6
