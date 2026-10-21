/* Coordinator ABI frame; the algorithm body is separately authored/tested. */
.section .text.biwn_native_rng,"ax",@progbits
.macro rng_entry name, address
.globl \name
\name:
move.w %sr,-(%sp)
movem.l %d0-%d7/%a0-%a6,-(%sp)
lea (%sp),%a0
move.l %a0,-(%sp)
move.l #\address,-(%sp)
bsr.w biwn_native_rng_dispatch
lea 8(%sp),%sp
movem.l (%sp)+,%d0-%d7/%a0-%a6
move.w (%sp)+,%ccr
rts
.endm
rng_entry biwn_native_rng_init,0x1a6e0
rng_entry biwn_native_rng_current,0x1a6f8
rng_entry biwn_native_rng_indexed,0x1a77c
rng_entry biwn_native_rng_fill,0x1a7f4
rng_entry biwn_native_rng_select,0x1a87a
rng_entry biwn_native_rng_seed,0x1a8c6
rng_entry biwn_native_rng_get,0x1a8e2
rng_entry biwn_native_rng_set,0x1a8f8
