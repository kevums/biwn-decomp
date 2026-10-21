#ifndef BIWN_CPU_IRQ_SELECT_H
#define BIWN_CPU_IRQ_SELECT_H
/* Pinned-emulator decision compatibility. kind0=ordinary, kind1=new assertion.
 * Inputs: kind0..1 and levels/mask0..7. Invalid returns-1; no service0; otherwise
 * selected level. No ACK, queue, stack, timing or hardware-accuracy claim. */
int biwn_cpu_irq_select(unsigned, unsigned, unsigned, unsigned);
#endif
