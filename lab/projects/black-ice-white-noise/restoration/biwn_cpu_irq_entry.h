#ifndef BIWN_CPU_IRQ_ENTRY_H
#define BIWN_CPU_IRQ_ENTRY_H
#include "biwn_world_cpu.h"
/* Pinned-emulator compatibility after device ACK resolves the vector.
 * This is runtime reconstruction, not recovered BIWN source or hardware timing.
 * Input SR is normalized by the host. Selection/masking/ACK are host services.
 * On a bus error, CPU output is unchanged and prior writes remain visible. */
int biwn_cpu_irq_entry(struct biwn_world_bus *,const struct biwn_task_cpu *,
                      unsigned level,unsigned resolved_vector,
                      struct biwn_task_cpu *);
#endif
