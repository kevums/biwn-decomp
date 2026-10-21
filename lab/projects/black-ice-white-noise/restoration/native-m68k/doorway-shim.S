.text
.globl biwn_native_doorway
.globl biwn_native_doorway_return
.extern biwn_doorway_kernel
/* Original10430 LONG object,WORD index,WORD direction on caller stack.
 * Private frame0D1,4D3,8object,12index,16direction,20outD1,24outA0,28outCCR.
 * C returns fullD0; original A1 always object. Other callee-saved regs intact.
 */
biwn_native_doorway:
    lea -32(%sp),%sp
    move.l %d1,(%sp)
    move.l %d3,4(%sp)
    move.l 36(%sp),%a0
    move.l %a0,8(%sp)
    moveq #0,%d1
    move.w 40(%sp),%d1
    move.l %d1,12(%sp)
    move.w 42(%sp),%d1
    move.l %d1,16(%sp)
    pea 20(%sp)
    move.l 8(%sp),-(%sp)
    move.l 8(%sp),-(%sp)
    move.l 28(%sp),-(%sp)
    move.l 28(%sp),-(%sp)
    move.l 28(%sp),-(%sp)
    jsr biwn_doorway_kernel
    lea 24(%sp),%sp
    movem.l 20(%sp),%d1/%a0
    move.l 8(%sp),%a1
    move.w 30(%sp),%ccr
    lea 32(%sp),%sp
biwn_native_doorway_return:
    rts
