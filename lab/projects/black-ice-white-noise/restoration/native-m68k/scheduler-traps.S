/* Source-assembled at the original addresses. Relocating the TRAP would
 * change its saved resume PC; these stubs therefore remain byte-identical. */
.section .yield,"ax",@progbits
.globl biwn_native_task_yield
biwn_native_task_yield:
movem.l %d2-%d7/%a2-%a6,-(%sp)
trap #0
movem.l (%sp)+,%d2-%d7/%a2-%a6
rts
.section .remove,"ax",@progbits
.globl biwn_native_task_remove_trap
biwn_native_task_remove_trap:
trap #2
