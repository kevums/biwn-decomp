/* Complete original 1AC3C caller ABI, with a scalar C search kernel.
 * C returns first matching index or36. Preserve public original D2 save;
 * C-private D1/A1 saves retain caller values the C ABI may clobber.
 */
.text
.globl biwn_native_frame_lookup
biwn_native_frame_lookup:
move.l %d2,-(%sp)
move.w 8(%sp),%d2
movem.l %d1/%a1,-(%sp)
move.l %d2,-(%sp)
bsr.w biwn_frame_lookup_body
lea 4(%sp),%sp
movem.l (%sp)+,%d1/%a1
move.w %d0,%d1
cmpi.w #36,%d0
bne.s 1f
moveq #0,%d0
1:
lea 0x15b4a0,%a0
move.w #0,%ccr
move.l (%sp)+,%d2
.globl biwn_native_frame_lookup_return
biwn_native_frame_lookup_return:
rts
