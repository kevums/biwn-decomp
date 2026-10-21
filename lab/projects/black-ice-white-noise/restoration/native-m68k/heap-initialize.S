/* Coordinator source transcription of1557A..155C2. Operands use the same
 * raised heap boundary as native23; checked byte-for-byte after relocation. */
.section .text.biwn_native_heap_initialize,"ax",@progbits
.globl biwn_native_heap_initialize
.type biwn_native_heap_initialize,@function
biwn_native_heap_initialize:
move.l #biwn_native_heap_start,0x112d60
move.l #0x1c0000,%d0
subi.l #biwn_native_heap_start,%d0
move.l %d0,biwn_native_heap_start
clr.l biwn_native_heap_start+4
clr.l biwn_native_heap_start+8
move.l %d0,0x112d64
move.w #255,%d1
lea 0x112960,%a0
1:
move.w %d1,%d0
ext.l %d0
asl.l #2,%d0
clr.l 0(%a0,%d0.l)
dbf %d1,1b
.globl biwn_native_heap_initialize_return
biwn_native_heap_initialize_return:
rts
.size biwn_native_heap_initialize,.-biwn_native_heap_initialize
