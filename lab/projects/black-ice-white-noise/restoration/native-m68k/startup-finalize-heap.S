/* New8KB staging window FC000..FE000, consumed before original400A. */
.section .text.biwn_native_startup_finalize,"ax",@progbits
.globl biwn_native_startup_finalize
biwn_native_startup_finalize:
lea 0xfc000,%a0
move.w #4095,%d0
1: clr.w (%a0)+
dbra %d0,1b
movem.l (%sp)+,%d0-%d7/%a0-%a6
move.w #0x2700,%sr
jmp 0x400a
