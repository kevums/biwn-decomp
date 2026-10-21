.text
.globl biwn_native_geometry_select_lean
.globl biwn_native_geometry_select_lean_return
.extern biwn_geometry_select_lean_kernel
/* Original1039C scalar ABI: kernel returns full D0, writes D1/A0/A1/CCR.
 * Failure D1 high half and A1 stay in the shim instead of crossing C twice.
 * Frame:0 saved D1,4 saved A1,8 object,12 requested,16..31 output.
 */
biwn_native_geometry_select_lean:
    lea -32(%sp),%sp
    move.l %d1,(%sp)
    move.l %a1,4(%sp)
    move.l 36(%sp),%a0
    move.l %a0,8(%sp)
    moveq #0,%d1
    move.w 40(%sp),%d1
    move.l %d1,12(%sp)
    pea 16(%sp)
    move.l 16(%sp),-(%sp)
    move.l 16(%sp),-(%sp)
    jsr biwn_geometry_select_lean_kernel
    lea 12(%sp),%sp
    tst.w %d0
    beq 1f
    movem.l 16(%sp),%d1/%a0-%a1
    bra 2f
1:  move.l (%sp),%d1
    move.w 14(%sp),%d1
    move.l 20(%sp),%a0
    move.l 4(%sp),%a1
2:  move.w 30(%sp),%ccr
    lea 32(%sp),%sp
biwn_native_geometry_select_lean_return:
    rts
