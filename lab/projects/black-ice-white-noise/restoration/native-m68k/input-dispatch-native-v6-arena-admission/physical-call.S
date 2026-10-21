/* C ABI bridge to declared original helper stack arguments.
 * Each word bit selects a 16-bit original argument; all others are long.
 * Original callee-save convention is required. Untested yielding paths are
 * deliberately not treated as qualified by the arithmetic fixture results.
 */
.section .text.biwn_input_physical_call,"ax",@progbits
.globl biwn_input_physical_call
biwn_input_physical_call:
movem.l %d2-%d7/%a2-%a6,-(%sp)
move.l 48(%sp),%a2
move.l 52(%sp),%a3
move.l 56(%sp),%d2
move.l 60(%sp),%d3
move.l 64(%sp),%d0
move.l %sp,%a4
tst.l %d2
beq.s 2f
1:
subq.l #1,%d2
move.l %d2,%d4
lsl.l #2,%d4
move.l (%a3,%d4.l),%d5
btst %d2,%d3
beq.s 3f
move.w %d5,-(%sp)
bra.s 4f
3:
move.l %d5,-(%sp)
4:
tst.l %d2
bne.s 1b
2:
jsr (%a2)
move.l %a4,%sp
movem.l (%sp)+,%d2-%d7/%a2-%a6
rts
