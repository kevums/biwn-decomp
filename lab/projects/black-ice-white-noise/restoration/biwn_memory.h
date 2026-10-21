#ifndef BIWN_MEMORY_H
#define BIWN_MEMORY_H
#include "biwn_world_update.h"
typedef int (*biwn_memory_write8)(void *,uint32_t,uint8_t);
enum biwn_memory_status {BIWN_MEMORY_OK=0,BIWN_MEMORY_BAD_ARGUMENT=1,
 BIWN_MEMORY_BUS_ERROR=2,BIWN_MEMORY_DEPENDENCY_ERROR=3,BIWN_MEMORY_WORK_LIMIT=4};
/* Complete source bodies 152A2..1545C,15200..152A2 and shared copy entries
 * E3E0/E3EE..E4AA. Original widths, rereads, logical dependency calls and
 * full D0 are preserved. Private stack, CCR and other caller-saved registers
 * are outside this API. Work limits/errors are host behavior; previous
 * memory/device effects remain, output D0 stays unchanged on error.
 * E3E0 logical args source,destination,count; E3EE destination,source,count.
 * Large copy emits actual source blitter writes; its backend supplies effects.
 * Odd lengths preserve truncated word count and byte-based advancement.
 */
enum biwn_memory_status biwn_memory_allocate(struct biwn_world_bus *,uint32_t requested,uint32_t budget,uint32_t *out_D0);
enum biwn_memory_status biwn_memory_compact(struct biwn_world_bus *,uint32_t budget,uint32_t *out_D0);
enum biwn_memory_status biwn_memory_copy(struct biwn_world_bus *,biwn_memory_write8,
 uint32_t entry,uint32_t arg0,uint32_t arg1,uint32_t count,uint32_t incoming_D0,uint32_t budget,uint32_t *out_D0);
#endif
