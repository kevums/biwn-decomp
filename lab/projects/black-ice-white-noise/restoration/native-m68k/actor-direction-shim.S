/* Original13440 saves D2-D4. Capture actual E588 outputs and preserve original
 * packed word arguments and its original stack depth. */
.equ DIRECTION_PRIVATE_RESERVE,112
.text
.globl biwn_native_actor_direction
biwn_native_actor_direction:
movem.l %d2-%d4,-(%sp)
lea -DIRECTION_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (12+DIRECTION_PRIVATE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l #0x13440,68(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_actor_direction_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea DIRECTION_PRIVATE_RESERVE(%sp),%sp
movem.l (%sp)+,%d2-%d4
.globl biwn_native_actor_direction_return
biwn_native_actor_direction_return:
rts
.globl biwn_native_actor_direction_division_capture
biwn_native_actor_direction_division_capture:
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
move.l %sp,72(%a0)
movea.l 60(%a0),%sp
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xe588
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (62+8-DIRECTION_PRIVATE_RESERVE)(%sp),%a0
movea.l %sp,%a1
moveq #14,%d0
1:
move.l (%a1)+,(%a0)+
dbra %d0,1b
move.w 60(%sp),6(%a0)
movea.l 12(%a0),%sp
lea 4(%sp),%sp
movem.l (%sp)+,%d2-%d7/%a2-%a6
rts
