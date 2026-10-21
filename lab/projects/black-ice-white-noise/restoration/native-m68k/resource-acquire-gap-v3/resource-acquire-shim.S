/* Coordinator ABI: private compiled stack and original helper stack positions.
 * The gap keeps compiler state below the bounded original helper frames.
 * Helpers receive all source semantic D/A registers; no host state repairs.
 */
.equ ACQUIRE_PRIVATE_RESERVE,448
.section .text.biwn_native_resource_acquire,"ax",@progbits
.globl biwn_native_resource_acquire
biwn_native_resource_acquire:
movem.l %d2-%d5/%a2-%a3,-(%sp)
lea -ACQUIRE_PRIVATE_RESERVE(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (24+ACQUIRE_PRIVATE_RESERVE)(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_resource_acquire_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea ACQUIRE_PRIVATE_RESERVE(%sp),%sp
movem.l (%sp)+,%d2-%d5/%a2-%a3
.globl biwn_native_resource_acquire_return
biwn_native_resource_acquire_return:
rts

.macro acquire_begin
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),-(%sp)
movea.l (%sp),%a0
.endm
.macro acquire_legacy_stack
move.l %sp,68(%a0)
movea.l 60(%a0),%sp
lea -24(%sp),%sp
move.w 66(%a0),%ccr
.endm
.macro acquire_finish nargs
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (62+4*\nargs-ACQUIRE_PRIVATE_RESERVE)(%sp),%a0
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

.globl biwn_native_acquire_wait_capture
biwn_native_acquire_wait_capture:
acquire_begin
acquire_legacy_stack
pea 1
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xdf8c
acquire_finish 1

.globl biwn_native_acquire_signal_capture
biwn_native_acquire_signal_capture:
acquire_begin
acquire_legacy_stack
pea 1
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xdf9c
acquire_finish 1

.globl biwn_native_acquire_allocate_capture
biwn_native_acquire_allocate_capture:
acquire_begin
movea.l 56(%sp),%a1
acquire_legacy_stack
move.l 8(%a1),-(%sp)
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0x152a2
acquire_finish 1

.globl biwn_native_acquire_load_capture
biwn_native_acquire_load_capture:
acquire_begin
movea.l 56(%sp),%a3
movea.l 60(%sp),%a1
lea 8(%a1),%a2
move.l %a2,4(%a0)
acquire_legacy_stack
move.w #0,%ccr
move.l %a2,-(%sp)
move.l 8(%a3),-(%sp)
move.l 2(%a1),-(%sp)
move.l 4(%a3),-(%sp)
move.l (%a3),-(%sp)
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0x1b044
acquire_finish 5
