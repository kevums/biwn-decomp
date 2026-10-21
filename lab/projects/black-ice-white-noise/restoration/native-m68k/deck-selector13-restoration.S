/* Coordinator source form of the existing selector13 restoration patch.
 * Original constructor multiplied by16. The retained disc mode3 groups
 * contain13x8192bytes plus a64byte marker run. Original behavior changes.
 * Keep the public 1AC68 call and its stack/result ABI. Compare returned D0
 * directly, then retain the original failure destination10BA0.
 */
.section .text.deck_selector13,"ax",@progbits
.globl biwn_restored_deck_group_selector
biwn_restored_deck_group_selector:
mulu.w #13,%d0
move.w %d0,0x403d8
move.w %d0,-(%sp)
jsr 0x1ac68
move.w %d0,0x403da
addq.w #4,%sp
cmpi.w #-1,%d0
beq.w biwn_original_deck_failure
nop

.section .rodata.deck_frame_count,"a",@progbits
.globl biwn_restored_deck_frames_per_group
biwn_restored_deck_frames_per_group:
.word 13
