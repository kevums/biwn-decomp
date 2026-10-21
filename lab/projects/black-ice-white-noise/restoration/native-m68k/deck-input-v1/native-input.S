.equ POOL_BASE,0xc0928
.equ POOL_BYTES,0x19400
.equ FRAME_OFFSET,144
.equ C_STACK_FROM_FRAME,560
.text
.globl biwn_native_deck_input
biwn_native_deck_input:
move.w %sr,-(%sp)
movem.l %d0/%a0,-(%sp)
move.l 0xc0920,%d0
subi.l #POOL_BASE,%d0
cmpi.l #POOL_BYTES,%d0
bhs.w .Lfallback
movea.l %d0,%a0
andi.l #0x3ff,%d0
bne.w .Lfallback
adda.l #(DECK_ARENA_BASE+FRAME_OFFSET),%a0
tst.l 100(%a0)
bne.w .Lfallback
movem.l %d1-%d7,4(%a0)
movem.l %a1-%a6,36(%a0)
move.l (%sp),(%a0)
move.l 4(%sp),32(%a0)
lea 10(%sp),%a1
move.l %a1,60(%a0)
move.l #0x11b4c,64(%a0)
clr.l 68(%a0)
clr.l 72(%a0)
move.w 8(%sp),76(%a0)
btst #5,76(%a0)
beq.s 1f
move.l %a1,72(%a0)
bra.s 2f
1:move.l %a1,68(%a0)
2:move.l #1,100(%a0)
lea C_STACK_FROM_FRAME(%a0),%sp
move.l %a0,-(%sp)
bsr.w biwn_native_deck_input_body
lea 4(%sp),%sp
lea -C_STACK_FROM_FRAME(%sp),%a0
tst.l 96(%a0)
bne.s .Lerror
clr.l 100(%a0)
movea.l 60(%a0),%sp
move.w 76(%a0),%ccr
movem.l (%a0),%d0-%d7/%a0-%a6
.globl biwn_native_deck_input_return
biwn_native_deck_input_return:
rts
.Lerror:illegal
.Lfallback:
movem.l (%sp)+,%d0/%a0
move.w (%sp)+,%ccr
.globl biwn_native_input_original_fallback
biwn_native_input_original_fallback:
/* Two original MOVE.L pushes update CCR before the original poll call. */
move.l %d3,-(%sp)
move.l %d2,-(%sp)
/* PEA/JMP reproduces the original JSR's return word without changing CCR. */
pea 0x11b56
jmp 0xe4c0

.macro capture symbol,target
.globl \symbol
\symbol:
movem.l %d2-%d7/%a2-%a6,-(%sp)
movea.l 48(%sp),%a0
movea.l 52(%sp),%a1
move.l %sp,80(%a0)
move.l %a1,84(%a0)
move.l 60(%a1),88(%a0)
movea.l 60(%a1),%a2
move.l (%a2),92(%a0)
move.l #biwn_native_input_helper_return,(%a2)
movea.l %a2,%sp
move.w 76(%a1),%ccr
movem.l (%a1),%d0-%d7/%a0-%a6
jmp \target
.endm
capture biwn_input_poll_capture,0xe4c0
capture biwn_input_record_capture,0x10c6e
capture biwn_input_first_texture_capture,0x10e72
capture biwn_input_texture_capture,0x10cb6
capture biwn_input_reset_capture,0x1102a

.globl biwn_native_input_helper_return
biwn_native_input_helper_return:
/* This1024:1024 mapping touches only SP before private-stack capture.
 * A valid pool identity is guaranteed by the root; helpers must return
 * in the same task,with their normal RTS stack contract. */
movea.l 0xc0920,%sp
adda.l #(DECK_ARENA_BASE+FRAME_OFFSET-POOL_BASE),%sp
movea.l 80(%sp),%sp
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
movea.l 0xc0920,%a0
adda.l #(DECK_ARENA_BASE+FRAME_OFFSET-POOL_BASE),%a0
movea.l 84(%a0),%a1
movea.l %sp,%a2
moveq #14,%d0
3:move.l (%a2)+,(%a1)+
dbra %d0,3b
move.l 88(%a0),(%a1)
move.l #0,4(%a1)
move.w 60(%sp),16(%a1)
movea.l 88(%a0),%a2
move.l 92(%a0),(%a2)
movea.l 80(%a0),%sp
movem.l (%sp)+,%d2-%d7/%a2-%a6
moveq #0,%d0
rts
