.text
.globl biwn_native_geometry_select
.globl biwn_native_geometry_select_return
.extern biwn_geometry_select_kernel
/* Private scalar-result ABI for complete original1039C..1042E.
 * C preserves D2-D7/A2-A6. The kernel supplies D0,D1,A0,A1,CCR.
 * 0..16 incoming scratch;20..36 outputs;40 object;44 requested word.
 */
biwn_native_geometry_select:
    lea -64(%sp),%sp
    movem.l %d0-%d1/%a0-%a1,(%sp)
    move.w %sr,16(%sp)
    move.l 68(%sp),%a0
    move.l %a0,40(%sp)
    moveq #0,%d1
    move.w 72(%sp),%d1
    move.l %d1,44(%sp)
    pea 20(%sp)
    move.l 16(%sp),-(%sp)
    move.l 12(%sp),-(%sp)
    move.l 56(%sp),-(%sp)
    move.l 56(%sp),-(%sp)
    jsr biwn_geometry_select_kernel
    lea 20(%sp),%sp
    movem.l 20(%sp),%d0-%d1/%a0-%a1
    move.w 38(%sp),%ccr
    lea 64(%sp),%sp
biwn_native_geometry_select_return:
    rts
