#ifndef BIWN_ATTACK_CPU_H
#define BIWN_ATTACK_CPU_H
#include "biwn_input_dispatch_cpu.h"
/* CPU-compatible attack continuation for original18DF2..18E90, one instruction
 * per call. Full registers/SR/active stack bank commit only on success; earlier
 * bus effects remain on error. Required callbacks:R16/R32/W16/W32. Status0OK,
 * 1bad argument,2bus failure,7unsupportedPC. JSR pushes the original return
 * and transfers to source RNG helpers; it does not execute them atomically.
 * Native Chat body plus exact coordinator helpers and15coordinator repairs.
 * All40PCs checked in20480native fixtures;35PCs reached in120/300frame gameplay.
 * This is a compatibility-stage replacement, distinct from biwn_attack_effect.
 * Original Object Processor/devices/IRQ/bootstrap services remain. */
int biwn_attack_CPU_step(struct biwn_world_bus *,struct biwn_task_cpu *);
#endif
