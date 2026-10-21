/* Enter only after the temporary disc loader copied the entire resident
 * bundle and while original D0-D7/A0-A6 remain saved on the supervisor stack.
 * Restore the original zero-filled staging window before regular startup.
 */
.section .text.biwn_native_startup_finalize,"ax",@progbits
.globl biwn_native_startup_finalize
biwn_native_startup_finalize:
lea 0xff000,%a0
move.w #2047,%d0
1: clr.w (%a0)+
dbra %d0,1b
movem.l (%sp)+,%d0-%d7/%a0-%a6
move.w #0x2700,%sr
jmp 0x400a
