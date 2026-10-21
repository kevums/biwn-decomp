#ifndef BIWN_MOVEMENT_SUBMIT_H
#define BIWN_MOVEMENT_SUBMIT_H
#include "biwn_gpu_commands.h"
/* Original CPU E220..E26C: publish five 32-bit arguments and command4320.
 * Same nonzero-unequal acknowledgement and final idle protocol as E2B8.
 * Return enum is added host status, not original D0. GPU work is external.
 */
enum biwn_gpu_result biwn_movement_submit(struct biwn_gpu_bus *,uint32_t,
    uint32_t,uint32_t,uint32_t,uint32_t);
#endif
