/* Coordinator ABI adapters. Fixed256 gap must be verified before nesting. */
.equ LOAD_PRIVATE_RESERVE,256
.section .text.biwn_native_resource_load,"ax",@progbits
.globl biwn_native_resource_load
biwn_native_resource_load:
movem.l %d2-%d3/%a2-%a5,-(%sp)
lea -LOAD_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (24+LOAD_PRIVATE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_resource_load_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea LOAD_PRIVATE_RESERVE(%sp),%sp
movem.l (%sp)+,%d2-%d3/%a2-%a5
.globl biwn_native_resource_load_return
biwn_native_resource_load_return:
rts

.macro load_begin extra=0
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
move.l %sp,68(%a0)
movea.l 60(%a0),%sp
lea (-24-\extra)(%sp),%sp
move.w 66(%a0),%ccr
.endm
.macro load_finish nargs
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (62+4*\nargs-LOAD_PRIVATE_RESERVE)(%sp),%a0
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
.globl biwn_native_load_yield_capture
biwn_native_load_yield_capture:
load_begin
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xdf60
load_finish 0
.globl biwn_native_load_seek_capture
biwn_native_load_seek_capture:
load_begin
move.l 12(%a0),-(%sp)
pea 2
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xd206
load_finish 2
.globl biwn_native_load_start_capture
biwn_native_load_start_capture:
load_begin 8
move.l (%a0),-(%sp)
move.l 40(%a0),-(%sp)
move.l #0x1c0000,-(%sp)
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xd2f0
load_finish 5
.globl biwn_native_load_stop_capture
biwn_native_load_stop_capture:
load_begin
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xd306
load_finish 0
.globl biwn_native_load_copy_capture
biwn_native_load_copy_capture:
load_begin
move.l 44(%a0),-(%sp)
movea.l 48(%a0),%a1
move.l (%a1),-(%sp)
move.l 40(%a0),-(%sp)
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xe3e0
load_finish 3
