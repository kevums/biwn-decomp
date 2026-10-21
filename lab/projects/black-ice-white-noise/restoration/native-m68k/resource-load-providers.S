/* Test-only CPU providers, not CD firmware or game runtime replacements.
 * 134000:yields,004:busy count,006:lock count,008:read count,
 * 010:install marker address,014:marker,018:install on request,
 * 01C:request count,020:read delay,024:read end,028:stops,02C:copies.
 * 03C:returned CCR,040:D0,044:D1,048:A0,04C:A1.
 */
.text
.macro provider_return
move.l 0x134040,%d0
move.l 0x134044,%d1
movea.l 0x134048,%a0
movea.l 0x13404c,%a1
move.w 0x13403c,%ccr
rts
.endm
.globl load_provider_yield
load_provider_yield:
addq.l #1,0x134000
tst.w 0x47b82
beq.s 1f
subq.w #1,0x134004
bne.s 4f
clr.w 0x47b82
bra.s 4f
1:
tst.w 0x47b80
beq.s 2f
tst.w 0x134006
beq.s 2f
subq.w #1,0x134006
bne.s 4f
clr.w 0x47b80
bra.s 4f
2:
tst.w 0x134008
beq.s 4f
subq.w #1,0x134008
bne.s 4f
move.l 0x134024,0xbd848
4:
provider_return
.globl load_provider_seek
load_provider_seek:
provider_return
.globl load_provider_start
load_provider_start:
addq.l #1,0x13401c
move.l 8(%sp),0x134024
move.w 0x134020,0x134008
move.l 0x134018,%d0
beq.s 2f
cmp.l 0x13401c,%d0
bne.s 2f
movea.l 0x134010,%a0
move.l 0x134014,%d1
moveq #15,%d0
1:
move.l %d1,(%a0)+
dbra %d0,1b
2:
provider_return
.globl load_provider_stop
load_provider_stop:
addq.l #1,0x134028
provider_return
.globl load_provider_copy
load_provider_copy:
addq.l #1,0x13402c
movea.l 4(%sp),%a0
movea.l 8(%sp),%a1
move.l 12(%sp),%d0
beq.s 2f
1:
move.b (%a0)+,(%a1)+
subq.l #1,%d0
bne.s 1b
2:
provider_return
