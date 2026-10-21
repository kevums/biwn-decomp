.text
.globl biwn_GPU_wait_complete
biwn_GPU_wait_complete:
1: cmpi.l #-1,0xf03204
bne.s 1b
cmpi.l #0,0xf03200
bne.s 1b
rts
