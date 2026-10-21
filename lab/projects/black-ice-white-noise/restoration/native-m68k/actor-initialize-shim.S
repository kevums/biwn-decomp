/* Coordinator134DC original-facing ABI. Preserve earlier artifacts unchanged. */
.equ INIT_PRIVATE_RESERVE,448
.text
.globl biwn_native_actor_initialize
biwn_native_actor_initialize:
movem.l %d2-%d7/%a2-%a3,-(%sp)
lea -INIT_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (32+INIT_PRIVATE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_actor_initialize_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea INIT_PRIVATE_RESERVE(%sp),%sp
movem.l (%sp)+,%d2-%d7/%a2-%a3
.globl biwn_native_actor_initialize_return
biwn_native_actor_initialize_return:
rts
.macro init_begin
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
move.l %sp,68(%a0)
movea.l 60(%a0),%sp
lea -32(%sp),%sp
.endm
.macro init_finish bytes
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (62+\bytes-INIT_PRIVATE_RESERVE)(%sp),%a0
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
.globl biwn_native_actor_initialize_outside_capture
biwn_native_actor_initialize_outside_capture:
init_begin
move.l 32(%a0),-(%sp)
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0x102c4
init_finish 4
.globl biwn_native_actor_initialize_inside_capture
biwn_native_actor_initialize_inside_capture:
init_begin
move.l 32(%a0),-(%sp)
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0x10520
init_finish 4
.globl biwn_native_actor_initialize_task_capture
biwn_native_actor_initialize_task_capture:
init_begin
move.l 44(%a0),-(%sp)
move.l 72(%a0),-(%sp)
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xdf6c
init_finish 8
