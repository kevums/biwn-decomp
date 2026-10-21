.section .text.biwn_native_format_core,"ax",@progbits
.macro CORE_ENTRY name,body
.globl \name
\name:
lea -224(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea 224(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w \body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea 224(%sp),%sp
rts
.endm
CORE_ENTRY biwn_native_format_core,biwn_native_format_core_body
CORE_ENTRY biwn_native_format_variadic,biwn_native_format_variadic_body
