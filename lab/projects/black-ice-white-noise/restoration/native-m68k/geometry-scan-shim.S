.text
.globl biwn_native_geometry_scan
.globl biwn_native_geometry_scan_return
.extern biwn_geometry_scan_kernel
/* C returns full original D0; out[0..3] = D1,A0,A1,CCR.
 * out[2] starts as incoming A1 and must remain untouched if scan is skipped.
 * D1 failure preserves its incoming high word. Callee-saved C regs stay intact.
 */
biwn_native_geometry_scan:
    lea -24(%sp),%sp
    move.l %d1,(%sp)
    move.l %a1,16(%sp)
    move.l 28(%sp),%a0
    pea 8(%sp)
    move.l %a0,-(%sp)
    jsr biwn_geometry_scan_kernel
    addq.l #8,%sp
    tst.w %d0
    beq 1f
    movem.l 8(%sp),%d1/%a0-%a1
    bra 2f
1:  move.l (%sp),%d1
    move.w 10(%sp),%d1
    movem.l 12(%sp),%a0-%a1
2:  move.w 22(%sp),%ccr
    lea 24(%sp),%sp
biwn_native_geometry_scan_return:
    rts
