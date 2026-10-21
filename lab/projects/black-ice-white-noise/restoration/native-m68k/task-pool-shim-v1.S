.text
.globl biwn_native_task_pool_initialize
biwn_native_task_pool_initialize:
lea -80(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea 80(%sp),%a0
move.l %a0,60(%sp)
move %usp,%a0
move.l %a0,68(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_task_pool_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea 80(%sp),%sp
.globl biwn_native_task_pool_switch
biwn_native_task_pool_switch:
move.w %sr,%d0
andi.w #0xdfff,%d0
move.w %d0,%sr
jmp 0xddcc
.globl biwn_native_task_pool_set_usp
biwn_native_task_pool_set_usp:
movea.l 4(%sp),%a0
.globl biwn_native_task_pool_set_usp_instruction
biwn_native_task_pool_set_usp_instruction:
move %a0,%usp
rts
