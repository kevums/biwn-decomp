/* E67C public pushes occupy entrySP-12..entrySP; private frame below. */
.section .text.biwn_native_unsigned_math,"ax",@progbits
.macro entry name,body,frame,fault,remainder
.globl \name
\name:
lea -\frame(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea \frame(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w \body
lea 4(%sp),%sp
tst.l %d0
bne.s .Lzero\@
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea \frame(%sp),%sp
rts
.Lzero\@:
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea \frame(%sp),%sp
.if \remainder
lea -12(%sp),%sp
.endif
.globl \fault
\fault:
divu.w %d2,%d1
move.l %a1,%d3
move.l %a0,%d2
.if \remainder
/* Read/pop saved E686 without executing old wrapper. */
tst.l (%sp)+
lea 8(%sp),%sp
move.l %d1,%d0
.endif
rts
.endm
entry biwn_native_unsigned_divide,biwn_native_unsigned_divide_body,80,biwn_native_unsigned_divide_fault,0
entry biwn_native_unsigned_remainder,biwn_native_unsigned_remainder_body,96,biwn_native_unsigned_remainder_fault,1
