.text
.globl biwn_native_geometry_outside
.globl biwn_native_geometry_outside_return
.extern biwn_geometry_outside_kernel
/* Original1028E has no public register save. This scratch frame is private.
 * Kernel result:0 inside at last compare,1 outside at last compare,2 early.
 * Kernel writes the last observed coordinate to a private output pointer.
 */
biwn_native_geometry_outside:
    lea -32(%sp),%sp
    movem.l %d0-%d1/%a0-%a1,(%sp)
    move.w %sr,16(%sp)
    move.l 36(%sp),%a1
    move.l %a1,28(%sp)
    pea 20(%sp)
    move.l %a1,-(%sp)
    jsr biwn_geometry_outside_kernel
    addq.l #8,%sp
    cmpi.l #2,%d0
    beq 2f
    tst.l %d0
    bne 1f
    move.l (%sp),%d0
    clr.w %d0
    move.w #4,24(%sp)
    bra 3f
1:  move.l (%sp),%d0
    move.w #1,%d0
    move.w #17,24(%sp)
    bra 3f
2:  moveq #1,%d0
    move.w 16(%sp),%d1
    andi.w #16,%d1
    move.w %d1,24(%sp)
3:  move.l 20(%sp),%d1
    move.l 28(%sp),%a0
    move.l 12(%sp),%a1
    move.w 24(%sp),%ccr
    lea 32(%sp),%sp
biwn_native_geometry_outside_return:
    rts
