#ifndef BIWN_CAMERA_H
#define BIWN_CAMERA_H
#include "biwn_world_update.h"
#include "biwn_input_dispatch.h"
enum biwn_camera_status { BIWN_CAMERA_OK=0,BIWN_CAMERA_BAD_ARGUMENT=1,
 BIWN_CAMERA_BUS_ERROR=2,BIWN_CAMERA_DEPENDENCY_ERROR=3 };
/* Analyst names: multiply E540..E588, direction13440..134DC,
 * camera F0FA..F35E. Two's-complement arithmetic wraps at source widths.
 * Camera debug branch consumes low words of incoming D2/D3. Out D0 is the
 * final shared long read, not a terrain-height query. Logical calls preserve
 * original stack argument widths/order; errors retain prior side effects.
 * Direction's zero-Z path preserves incoming D0 upper16. Other caller-saved
 * registers/CCR and private CPU stack are outside these host interfaces. */
uint32_t biwn_multiply32(uint32_t,uint32_t);
enum biwn_camera_status biwn_camera_direction(struct biwn_world_bus *,
 uint16_t x,uint16_t z,uint32_t incoming_d0,uint32_t *out_d0);
enum biwn_camera_status biwn_camera_update(struct biwn_world_bus *,
 biwn_input_write8,uint32_t incoming_d2,uint32_t incoming_d3,uint32_t *out_d0);
#endif
