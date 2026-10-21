/* Caller-specific prototype for JSR at 1A266, not global 191F4 replacement.
 * D0 and D2-D7/A2-A6 plus entry SR/stack banks are preserved up to route.
 * D1/A0/A1 are scratch; complete caller qualification remains required.
 * No stack access or public write until user-mode slot identity, even SP,
 * upper bound and 40 bytes below SP inside the stack have been established.
 * C preflight consumes at most 36 bytes (24 arguments/saves+4 JSR+8 callee).
 * Native reserve512 is provisional for the currently bounded helper test.
 * Rejection tails to original191F4; it cannot make an invalid original
 * stack safe. No native side effects occur before that fallback decision.
 */
.section .admission_entry,"ax",@progbits
.globl biwn_native_input_admission_entry
biwn_native_input_admission_entry:
move.w %sr,%d1
movea.l %d1,%a1
btst #13,%d1
bne.w biwn_input_early_original
move.l 0xc0920,%d1
movea.l %d1,%a0
cmpi.l #0xc0928,%d1
bcs.w biwn_input_early_original
subi.l #0xc0928,%d1
cmpi.l #102400,%d1
bhi.w biwn_input_early_original
andi.l #1023,%d1
bne.w biwn_input_early_original
move.l %sp,%d1
btst #0,%d1
bne.w biwn_input_early_original
adda.w #1020,%a0
cmpa.l %sp,%a0
bcs.w biwn_input_early_original
suba.w #916,%a0
cmpa.l %sp,%a0
bhi.w biwn_input_early_original
suba.w #104,%a0
move.l %a1,-(%sp)
move.l %d0,-(%sp)
move.l #512,-(%sp)
move.l %a1,-(%sp)
pea 16(%sp)
move.l %a0,-(%sp)
jsr biwn_input_task_admit
lea 16(%sp),%sp
tst.l %d0
beq.s biwn_input_checked_original
move.l (%sp)+,%d0
addq.l #2,%sp
move.w (%sp)+,%ccr
jmp biwn_native_input_entry
biwn_input_checked_original:
move.l (%sp)+,%d0
addq.l #2,%sp
move.w (%sp)+,%ccr
jmp 0x191f4
biwn_input_early_original:
move.l %a1,%d1
move.w %d1,%ccr
jmp 0x191f4
