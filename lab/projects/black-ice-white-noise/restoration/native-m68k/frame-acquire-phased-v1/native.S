.equ TRANSIENT_CONTEXT,96
.text
/* At every C phase boundary SP is the original S-44 public frame.
 * All C frames are gone before the loader or actual DIVS instruction. */
.macro capture_context
lea -TRANSIENT_CONTEXT(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea (44+TRANSIENT_CONTEXT)(%sp),%a0
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
jsr biwn_frame_phased_\name
lea 4(%sp),%sp
bra.w .Ldispatch
.endm
.globl biwn_frame_phased_entry
biwn_frame_phased_entry:
link.w %a6,#-4
movem.l %d2-%d7/%a2-%a4,-(%sp)
phase start
.Ldispatch:
tst.l %d0
beq.w .Ldone
cmpi.l #1,%d0
beq.w .Ldiv_first
cmpi.l #2,%d0
beq.w .Ldiv_empty
cmpi.l #3,%d0
beq.w .Ldiv_evict
cmpi.l #4,%d0
beq.w .Lload
illegal
.Ldiv_first:
restore_context
.globl biwn_frame_phased_divs_first_instruction
biwn_frame_phased_divs_first_instruction:
divs.w %d3,%d0
phase after_first_divs
.Ldiv_empty:
restore_context
.globl biwn_frame_phased_divs_empty_instruction
biwn_frame_phased_divs_empty_instruction:
divs.w %d3,%d0
bra.s .Lgroup_done
.Ldiv_evict:
restore_context
.globl biwn_frame_phased_divs_evict_instruction
biwn_frame_phased_divs_evict_instruction:
divs.w %d3,%d0
.Lgroup_done:
phase after_group_divs
.Lload:
restore_context
clr.l -(%sp)
move.l %d5,-(%sp)
pea -4(%a6)
move.l %a4,-(%sp)
pea 0(%a1,%a2.l)
jsr 0x1b044
.globl biwn_frame_phased_after_loader
biwn_frame_phased_after_loader:
lea 20(%sp),%sp
phase after_load
.Ldone:
restore_context
movem.l -40(%a6),%d2-%d7/%a2-%a4
unlk %a6
.globl biwn_frame_phased_return
biwn_frame_phased_return:
rts
