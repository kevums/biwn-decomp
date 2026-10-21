.text
.globl task_A
task_A:
move.w #0,-(%sp)
jsr 0x1af04
addq.l #2,%sp
rts
.org 0x100
.globl task_B
task_B:
addq.l #1,0x7000
pea 1
clr.l -(%sp)
pea 64
clr.l -(%sp)
pea 0x98000
jsr 0xe220
lea 20(%sp),%sp
move.l 0x7000,%d0
cmp.l 0x7004,%d0
bne.s 1f
move.w #1,0x15b53c
1:
pea 1
jsr 0xdf9c
addq.l #4,%sp
move.l #0x22222222,%d2
move.l #0x33333333,%d3
move.l #0x44444444,%d4
move.l #0x55555555,%d5
move.l #0x66666666,%d6
move.l #0x77777777,%d7
move.l #0xa2a2a2a2,%a2
move.l #0xa3a3a3a3,%a3
move.l #0xa4a4a4a4,%a4
move.l #0xa5a5a5a5,%a5
move.l #0xa6a6a6a6,%a6
jsr 0xdf60
bra.w task_B
