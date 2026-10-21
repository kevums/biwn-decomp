/* Coordinator native boundaries. Selection C is a separate local draft.
 * Original task frame offsets, memory order, USP transfer and RTE remain
 * explicit. No host context transplant, budget, return PC or idle task.
 * The scratch frame is15saved registers + one private flag word. */
.section .text.biwn_native_scheduler,"ax",@progbits
.globl biwn_native_scheduler_dispatch
.globl biwn_native_scheduler_remove
.globl biwn_native_scheduler_select_entry
.globl biwn_native_scheduler_rte
biwn_native_scheduler_dispatch:
movea.l 0xc0920,%a0
move %usp,%a1
move.l %a1,12(%a0)
move.w (%sp)+,20(%a0)
move.l (%sp)+,16(%a0)
bra.s biwn_native_scheduler_select_entry
biwn_native_scheduler_remove:
movea.l 0xc0920,%a0
movea.l (%a0),%a1
move.l 0xc0924,(%a0)
move.l %a0,0xc0924
movea.l 4(%a0),%a0
move.l %a0,4(%a1)
move.l %a1,(%a0)
lea 6(%sp),%sp
biwn_native_scheduler_select_entry:
/* Keep the original six-byte exception-frame addresses outside scratch. */
lea -12(%sp),%sp
movem.l %d0-%d7/%a0-%a6,-(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_scheduler_select
lea 4(%sp),%sp
tst.l 60(%sp)
movem.l (%sp)+,%d0-%d7/%a0-%a6
lea 12(%sp),%sp
beq.s .Lpublish
move.l #0,22(%a0)
.Lpublish:
move.l %a0,0xc0920
move.l 16(%a0),-(%sp)
move.w 20(%a0),-(%sp)
movea.l 12(%a0),%a1
move %a1,%usp
biwn_native_scheduler_rte:
rte
