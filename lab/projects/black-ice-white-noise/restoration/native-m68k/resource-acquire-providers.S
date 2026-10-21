/* Controlled target-68000 dependencies, explicitly not real I/O/scheduler. */
.text
.macro provider_begin tag
move.w %sr,-(%sp)
movem.l %d0-%d1/%a0-%a1,-(%sp)
moveq #0,%d0
move.w 0x130050,%d0
mulu.w #24,%d0
lea 0x131000,%a0
adda.l %d0,%a0
move.w #\tag,(%a0)
move.w 16(%sp),2(%a0)
move.l (%sp),4(%a0)
move.l 4(%sp),8(%a0)
move.l 8(%sp),12(%a0)
move.l 12(%sp),16(%a0)
addq.w #1,0x130050
.endm
.macro provider_finish return_address
move.w 0x13003c,%d0
tst.w 0x13003e
bne 1f
andi.w #15,%d0
move.w 16(%sp),%d1
andi.w #16,%d1
or.w %d1,%d0
1:
move.w %d0,16(%sp)
move.l 8(%sp),%d0
move.l 0x130044,%d1
eor.l %d1,%d0
movea.l %d0,%a0
move.l 4(%sp),%d0
move.l 0x130048,%d1
eor.l %d1,%d0
movea.l %d0,%a1
move.l (%sp),%d1
move.l 0x130040,%d0
eor.l %d0,%d1
move.l \return_address,%d0
move.w 16(%sp),%ccr
lea 18(%sp),%sp
rts
.endm
.globl acquire_provider_wait
acquire_provider_wait:
provider_begin 0
addq.w #1,0x13000a
move.w 0x13000a,%d0
cmp.w 0x130008,%d0
blt 1f
movea.l 0x130004,%a0
move.w 0x13000c,(%a0)
movea.l 0x130028,%a0
cmpa.w #0,%a0
beq 1f
move.l 0x13002c,(%a0)
1:
provider_finish 0x130054
.globl acquire_provider_allocate
acquire_provider_allocate:
provider_begin 1
movea.l 0x130020,%a0
cmpa.w #0,%a0
beq 1f
move.l 0x130024,(%a0)
1:
provider_finish 0x130000
.globl acquire_provider_load
acquire_provider_load:
provider_begin 2
movea.l 38(%sp),%a0
move.w 0x130010,(%a0)
move.w 0x13000e,-2(%a0)
tst.w 0x130014
beq 1f
move.l 0x130018,-6(%a0)
1:
provider_finish 0x130058
.globl acquire_provider_signal
acquire_provider_signal:
provider_begin 3
addq.w #1,0x130012
movea.l 0x130030,%a0
cmpa.w #0,%a0
beq 1f
move.l 0x130034,(%a0)
1:
provider_finish 0x13005c
