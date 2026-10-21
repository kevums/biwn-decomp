#ifndef BIWN_INVENTORY_PIPELINE_H
#define BIWN_INVENTORY_PIPELINE_H
#include "biwn_inventory_draw.h"

/* Connected CPU command generation: inventory1B786, text149AE/147A6/14776,
 * spriteE2B8 and idleE098. GPU processing and drawing hardware are external.
 * One shared read budget covers external memory/device reads; the private
 * formatted money string is read locally. Host status is not original D0. */
struct biwn_inventory_pipeline_bus {
    biwn_draw_r8 read8;
    biwn_draw_r16 read16;
    biwn_draw_r32 read32;
    biwn_draw_w32 write32;
    void *context;
    uint32_t read_budget;
};
enum biwn_inventory_pipeline_result {
    BIWN_PIPELINE_OK=0,BIWN_PIPELINE_BAD_ARGUMENT=1,
    BIWN_PIPELINE_READ_LIMIT=2,BIWN_PIPELINE_BUS_ERROR=3,
    BIWN_PIPELINE_DEPENDENCY_ERROR=4
};
enum biwn_inventory_pipeline_result biwn_inventory_pipeline(struct biwn_inventory_pipeline_bus *);
#endif
