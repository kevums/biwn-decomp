.text
.globl biwn_native_deck_six_finalize
biwn_native_deck_six_finalize:
lea 0x17b3c0,%a0
move.w #51711,%d0
deck_clear:
clr.w (%a0)+
dbra %d0,deck_clear
lea 0x1947c0,%a0
move.w #19391,%d0
outer_clear:
clr.w (%a0)+
dbra %d0,outer_clear
lea 0x17b3c0,%a0
lea 0x1947d0,%a1
move.w #100,%d0
move.l #0xa5a5a5a5,%d1
deck_fences:
move.l %d1,0(%a0)
move.l %d1,4(%a0)
move.l %d1,8(%a0)
move.l %d1,12(%a0)
move.l %d1,136(%a0)
move.l %d1,140(%a0)
move.l %d1,264(%a0)
move.l %d1,268(%a0)
move.l %d1,400(%a0)
move.l %d1,404(%a0)
move.l %d1,408(%a0)
move.l %d1,412(%a0)
move.l %d1,592(%a0)
move.l %d1,596(%a0)
move.l %d1,600(%a0)
move.l %d1,604(%a0)
move.l %d1,816(%a0)
move.l %d1,820(%a0)
move.l %d1,824(%a0)
move.l %d1,828(%a0)
move.l %d1,1008(%a0)
move.l %d1,1012(%a0)
move.l %d1,1016(%a0)
move.l %d1,1020(%a0)
move.l %a1,392(%a0)
lea 1024(%a0),%a0
lea 384(%a1),%a1
dbra %d0,deck_fences
lea 0x1947c0,%a0
move.w #100,%d0
outer_fences:
move.l %d1,0(%a0)
move.l %d1,4(%a0)
move.l %d1,8(%a0)
move.l %d1,12(%a0)
move.l %d1,136(%a0)
move.l %d1,140(%a0)
move.l %d1,368(%a0)
move.l %d1,372(%a0)
move.l %d1,376(%a0)
move.l %d1,380(%a0)
lea 384(%a0),%a0
dbra %d0,outer_fences
lea 0xe1bc0,%a0
move.w #58143,%d0
stage_clear:
clr.w (%a0)+
dbra %d0,stage_clear
movem.l (%sp)+,%d0-%d7/%a0-%a6
move.w #0x2700,%sr
jmp 0x400a
