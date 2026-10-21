.equ NAV_PRIVATE_RESERVE,96
.text
.macro navigation_root name,entry,savebytes
.globl \name
\name:
.if \savebytes
movem.l %d2/%a2,-(%sp)
.endif
lea -NAV_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (\savebytes+NAV_PRIVATE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l #\entry,68(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_actor_navigation_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea NAV_PRIVATE_RESERVE(%sp),%sp
.if \savebytes
movem.l (%sp)+,%d2/%a2
.endif
.globl \name\()_return
\name\()_return:
rts
.endm
navigation_root biwn_native_actor_waypoint,0xf368,8
navigation_root biwn_native_actor_nav_left_entry,0x13f12,0
navigation_root biwn_native_actor_nav_right_entry,0x13f7c,0
navigation_root biwn_native_actor_nav_front_entry,0x13fea,0
