/* Coordinator prototype: park resource-acquire compiler state in the existing
 * per-task GPU scratch slot. Original guest helper SP/arguments remain intact.
 * Slot lifetime conflicts, real scheduler reentry and IRQs require proofs.
 * No additional RAM is allocated; this prototype is not installed in a disc.
 */
.equ POOL_BASE,0xc0928
.equ POOL_BYTES,0x19400
.equ RESOURCE_CONTEXT,168

.macro arena_context
move.l 0xc0920,%d0
subi.l #POOL_BASE,%d0
cmpi.l #POOL_BYTES,%d0
bhs.s 2f
movea.l %d0,%a0
andi.l #0x3ff,%d0
bne.s 2f
move.l %a0,%d0
lsr.l #2,%d0
lea GPU_ARENA_BASE+RESOURCE_CONTEXT,%a0
adda.l %d0,%a0
bra.s 3f
2:
lea GPU_ARENA_BASE+101*256+RESOURCE_CONTEXT,%a0
3:
.endm

.text
.globl biwn_acquire_arena_entry
biwn_acquire_arena_entry:
movem.l %d2-%d5/%a2-%a3,-(%sp)
move.w %sr,-(%sp)
movem.l %d0/%a0,-(%sp)
arena_context
movem.l %d1-%d7,4(%a0)
movem.l %a1-%a6,36(%a0)
move.l (%sp),(%a0)
move.l 4(%sp),32(%a0)
lea 34(%sp),%a1
move.l %a1,60(%a0)
clr.w 64(%a0)
move.w 8(%sp),66(%a0)
movea.l %a0,%sp
move.l %sp,-(%sp)
jsr ACQUIRE_BODY
lea 4(%sp),%sp
movea.l %sp,%a0
movea.l 60(%a0),%sp
lea -24(%sp),%sp
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
movem.l (%sp)+,%d2-%d5/%a2-%a3
.globl biwn_acquire_arena_return
biwn_acquire_arena_return:
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
.macro acquire_finish
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
arena_context
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

.globl biwn_acquire_arena_wait
biwn_acquire_arena_wait:
acquire_begin
acquire_legacy_stack
pea 1
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xdf8c
.globl biwn_acquire_arena_wait_return
biwn_acquire_arena_wait_return:
acquire_finish

.globl biwn_acquire_arena_signal
biwn_acquire_arena_signal:
acquire_begin
acquire_legacy_stack
pea 1
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xdf9c
.globl biwn_acquire_arena_signal_return
biwn_acquire_arena_signal_return:
acquire_finish

.globl biwn_acquire_arena_allocate
biwn_acquire_arena_allocate:
acquire_begin
movea.l 56(%sp),%a1
acquire_legacy_stack
move.l 8(%a1),-(%sp)
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0x152a2
.globl biwn_acquire_arena_allocate_return
biwn_acquire_arena_allocate_return:
acquire_finish

.globl biwn_acquire_arena_load
biwn_acquire_arena_load:
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
.globl biwn_acquire_arena_load_return
biwn_acquire_arena_load_return:
acquire_finish
