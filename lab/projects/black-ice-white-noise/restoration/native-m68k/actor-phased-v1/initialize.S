.equ TRANSIENT_CONTEXT,96
.text
.macro capture_context
lea -TRANSIENT_CONTEXT(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (32+TRANSIENT_CONTEXT)(%sp),%a0
move.l %a0,60(%sp)
.endm
.macro restore_context
move.w 66(%sp),%ccr
movem.l (%sp),%d0-%d7/%a0-%a6
lea TRANSIENT_CONTEXT(%sp),%sp
.endm
.macro phase name
capture_context
move.l %sp,-(%sp)
jsr biwn_actor_initialize_\name
lea 4(%sp),%sp
bra.w .Ldispatch
.endm
.globl biwn_native_actor_initialize
biwn_native_actor_initialize:
movem.l %d2-%d7/%a2-%a3,-(%sp)
phase start
.Ldispatch:
tst.l %d0
beq.w .Ldone
cmpi.l #1,%d0
beq.w .Loutside
cmpi.l #2,%d0
beq.w .Linside
cmpi.l #3,%d0
beq.w .Ltask
cmpi.l #4,%d0
beq.w .Lcontinue
illegal
.Loutside:
restore_context
move.l %a0,-(%sp)
jsr 0x102c4
.globl biwn_actor_initialize_after_outside
biwn_actor_initialize_after_outside:
lea 4(%sp),%sp
bra.s .Lplacement_done
.Linside:
restore_context
move.l %a0,-(%sp)
jsr 0x10520
.globl biwn_actor_initialize_after_inside
biwn_actor_initialize_after_inside:
lea 4(%sp),%sp
bra.s .Lplacement_done
.Lcontinue:
restore_context
.Lplacement_done:
phase after_placement
.Ltask:
/* Stage callback at T-8, preserving every hardware GPR. Original order is
 * slot at T-4, callback at T-8. The slot MOVE supplies original NZ flags;
 * PEA callback in the original does not change them. */
move.l 72(%sp),88(%sp)
restore_context
move.l %a3,-(%sp)
lea -4(%sp),%sp
jsr 0xdf6c
.globl biwn_actor_initialize_after_task
biwn_actor_initialize_after_task:
lea 8(%sp),%sp
bra.s .Lreturn
.Ldone:
restore_context
.Lreturn:
movem.l (%sp)+,%d2-%d7/%a2-%a3
.globl biwn_native_actor_initialize_return
biwn_native_actor_initialize_return:
rts
