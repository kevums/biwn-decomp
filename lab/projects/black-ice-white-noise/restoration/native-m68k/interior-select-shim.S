.text
.globl biwn_native_interior_actor_select
.globl biwn_native_interior_sprite_select
.globl biwn_native_interior_select_return
.extern biwn_interior_select_kernel
biwn_native_interior_actor_select:
    moveq #0,%d0
    bra 1f
biwn_native_interior_sprite_select:
    moveq #1,%d0
1:  lea -16(%sp),%sp
    movem.l %d1/%a0-%a1,(%sp)
    pea (%sp)
    move.l %d0,-(%sp)
    move.l 28(%sp),-(%sp)
    jsr biwn_interior_select_kernel
    lea 12(%sp),%sp
    movem.l (%sp),%d1/%a0-%a1
    move.w 14(%sp),%ccr
    lea 16(%sp),%sp
biwn_native_interior_select_return:
    rts
