/* Coordinator target ABI and retained native dependency captures. */
.section .text.biwn_native_heap,"ax",@progbits
.macro heap_entry name, body
.globl \name
\name:
lea -72(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea 72(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w \body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea 72(%sp),%sp
rts
.endm
heap_entry biwn_native_heap_allocate,biwn_native_heap_allocate_body
heap_entry biwn_native_heap_compact,biwn_native_heap_compact_body

.macro seed_capture
movem.l (%a2),%d0-%d1
movea.l 32(%a2),%a0
movea.l 36(%a2),%a1
move.w 66(%a2),%ccr
.endm
.macro finish_capture
move.w %sr,-(%sp)
movem.l %d0-%d1,(%a2)
move.l %a0,32(%a2)
move.l %a1,36(%a2)
move.w (%sp)+,66(%a2)
.endm
.globl biwn_native_heap_compact_capture
biwn_native_heap_compact_capture:
move.l %a2,-(%sp)
movea.l 8(%sp),%a2
seed_capture
jsr 0x15200
finish_capture
movea.l (%sp)+,%a2
rts
.globl biwn_native_heap_copy_capture
biwn_native_heap_copy_capture:
move.l %a2,-(%sp)
movea.l 8(%sp),%a2
seed_capture
move.l 20(%sp),-(%sp)
move.l 20(%sp),-(%sp)
move.l 20(%sp),-(%sp)
jsr 0xe3e0
finish_capture
lea 12(%sp),%sp
movea.l (%sp)+,%a2
rts
.globl biwn_native_heap_clear_tail
biwn_native_heap_clear_tail:
movea.l 4(%sp),%a0
clr.l 4(%a0)
clr.l 8(%a0)
rts
