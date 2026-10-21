.equ TRANSIENT_CONTEXT,96
.text
.globl biwn_native_actor_dispatch
biwn_native_actor_dispatch:
movem.l %d2-%d5,-(%sp)
lea -TRANSIENT_CONTEXT(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (16+TRANSIENT_CONTEXT)(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
jsr biwn_actor_dispatch_phase
lea 4(%sp),%sp
tst.l %d0
beq.w .Ldone
cmpi.l #1,%d0
beq.w .Lactor
cmpi.l #2,%d0
beq.w .Lsprite
illegal
.macro restore_context
move.w 66(%sp),%ccr
movem.l (%sp),%d0-%d7/%a0-%a6
lea TRANSIENT_CONTEXT(%sp),%sp
.endm
.Lactor:
restore_context
move.w %d2,-(%sp)
move.l %d3,-(%sp)
move.w %d4,-(%sp)
move.l %d5,-(%sp)
move.w %d1,-(%sp)
move.w %a1,-(%sp)
jsr 0x134dc
.globl biwn_actor_dispatch_after_actor
biwn_actor_dispatch_after_actor:
lea 16(%sp),%sp
bra.s .Lreturn
.Lsprite:
restore_context
move.w %d2,-(%sp)
move.l %d3,-(%sp)
move.w %d4,-(%sp)
move.l %d5,-(%sp)
move.w %a1,-(%sp)
jsr 0x137e0
.globl biwn_actor_dispatch_after_sprite
biwn_actor_dispatch_after_sprite:
lea 14(%sp),%sp
bra.s .Lreturn
.Ldone:
restore_context
.Lreturn:
movem.l (%sp)+,%d2-%d5
.globl biwn_native_actor_dispatch_return
biwn_native_actor_dispatch_return:
rts
