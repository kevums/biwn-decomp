/* Private80byte frame leaves the top8bytes for original public D3/D2 saves. */
.section .text.biwn_native_frame_reference_release,"ax",@progbits
.globl biwn_native_frame_reference_release
biwn_native_frame_reference_release:
lea -80(%sp),%sp
movem.l %d0-%d7/%a0-%a6,(%sp)
move.w %sr,66(%sp)
clr.w 64(%sp)
lea 80(%sp),%a0
move.l %a0,60(%sp)
move.l %sp,-(%sp)
bsr.w biwn_native_frame_reference_release_body
lea 4(%sp),%sp
movem.l (%sp),%d0-%d7/%a0-%a6
move.w 66(%sp),%ccr
lea 80(%sp),%sp
rts
