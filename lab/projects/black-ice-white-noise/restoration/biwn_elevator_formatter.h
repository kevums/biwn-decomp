#ifndef BIWN_ELEVATOR_FORMATTER_H
#define BIWN_ELEVATOR_FORMATTER_H
#include "biwn_formatter_cpu.h"
/* Source formatter1B45A adapter for the elevator's one-word argument.
 * scratch is original display entrySP-14; the formatter argument frame
 * begins scratch-20. The caller reserves enough mapped private stack below
 * it for the recovered formatter. Private saved-register values are seeded,
 * not a CPU ABI reconstruction. Public formatter scratch effects and D0
 * are computed by source C; no hostprintf or original CPU provider.
 */
int biwn_elevator_format(struct biwn_world_bus *,biwn_input_write8,
 uint32_t scratch,uint32_t format,uint16_t word,uint32_t *out_D0);
#endif
