#ifndef BIWN_GPU_RENDER_COMMANDS_H
#define BIWN_GPU_RENDER_COMMANDS_H
#include "biwn_gpu_commands.h"
/* Original E19E projection and E202 draw CPU protocols. Every read shares
 * read_budget, including source49B88. E202 returns at acknowledgement and
 * has no final idle wait. E19E establishes D0=47BC8 only on success.
 * GPU execution, asynchronous completion, CPU ABI/CCR remain external.
 * Host limits/errors retain prior effects and leave out_D0 untouched. */
enum biwn_gpu_result biwn_gpu_submit_52e0(struct biwn_gpu_bus *,uint32_t *);
enum biwn_gpu_result biwn_gpu_submit_57a0(struct biwn_gpu_bus *);
#endif
