/* Per-task private C stacks:101verified original slots + one boot slot.
 *256bytes/slot,16byte guards at each end. Context124bytes at usable top.
 * Original task stack uses only a10byte entry capture and8byte wait scratch.
 * Fixed E098 variants preserve D/A; actual SR is copied back after each call.
 */
.equ POOL_BASE,0xc0928
.equ POOL_BYTES,0x19400
.equ ARENA_SLOT_USABLE_TOP,240
.equ ARENA_CONTEXT,124
.text
.macro arena_root symbol,entry,suffix
.globl \symbol
\symbol:
move.w %sr,-(%sp)
movem.l %d0/%a0,-(%sp)
.globl biwn_native_gpu_arena_identity_\suffix
biwn_native_gpu_arena_identity_\suffix:
move.l 0xc0920,%d0
subi.l #POOL_BASE,%d0
cmpi.l #POOL_BYTES,%d0
bhs.s 2f
movea.l %d0,%a0
andi.l #0x3ff,%d0
bne.s 2f
move.l %a0,%d0
lsr.l #2,%d0
lea GPU_ARENA_BASE+ARENA_SLOT_USABLE_TOP,%a0
adda.l %d0,%a0
bra.s 3f
2:
lea GPU_ARENA_BASE+101*256+ARENA_SLOT_USABLE_TOP,%a0
3:
lea -ARENA_CONTEXT(%a0),%a0
movem.l %d1-%d7,4(%a0)
movem.l %a1-%a6,36(%a0)
move.l (%sp),(%a0)
move.l 4(%sp),32(%a0)
lea 10(%sp),%a1
move.l %a1,60(%a0)
clr.w 64(%a0)
move.w 8(%sp),66(%a0)
move.l #\entry,68(%a0)
movea.l %a0,%sp
move.l %sp,-(%sp)
bsr.w biwn_native_gpu_mailbox_body
lea 4(%sp),%sp
movea.l %sp,%a0
movea.l 60(%a0),%sp
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
.globl \symbol\()_return
\symbol\()_return:
rts
.endm
arena_root biwn_native_gpu_submit_4320,0xe220,4320
arena_root biwn_native_gpu_submit_4b00,0xe2b8,4b00
.globl biwn_native_gpu_mailbox_wait_capture
biwn_native_gpu_mailbox_wait_capture:
movea.l 4(%sp),%a0
movem.l %d2-%d7/%a2-%a6,76(%a0)
move.l %sp,72(%a0)
movea.l 60(%a0),%a1
move.l %a0,-8(%a1)
movea.l %a1,%sp
move.w 66(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
jsr 0xe098
move.w %sr,-(%sp)
movea.l -6(%sp),%a0
move.w (%sp),66(%a0)
movea.l 72(%a0),%sp
movem.l 76(%a0),%d2-%d7/%a2-%a6
rts
