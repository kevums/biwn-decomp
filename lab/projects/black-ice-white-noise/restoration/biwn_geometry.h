#ifndef BIWN_GEOMETRY_H
#define BIWN_GEOMETRY_H
#include "biwn_world_update.h"
/* Analyst names, original CPU entries1028E,102C4,1039C,10430,10652.
 * These routines make no nested calls. Object/record formats and access order
 * are retained through the bus; private stack and full CCR are not modeled.
 * D0 outputs are full32bit register values, not just the caller-used lowword.
 */
enum biwn_geometry_status { BIWN_GEOMETRY_OK=0,BIWN_GEOMETRY_BAD_ARGUMENT=1,
    BIWN_GEOMETRY_SCAN_LIMIT=2,BIWN_GEOMETRY_BUS_ERROR=3 };
enum biwn_geometry_status biwn_geometry_outside(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t *);
enum biwn_geometry_status biwn_geometry_find_tile(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t *);
enum biwn_geometry_status biwn_geometry_select_tile(struct biwn_world_bus *,uint32_t,uint16_t,uint32_t *);
enum biwn_geometry_status biwn_geometry_select_portal(struct biwn_world_bus *,uint32_t,uint16_t,uint16_t,uint32_t,uint32_t,uint32_t *);
enum biwn_geometry_status biwn_geometry_select_region(struct biwn_world_bus *,uint32_t,uint16_t,uint32_t,uint32_t *);
/* Added argument/error/scan guards retain prior stores and do not commit D0.
 * Negative signed indexes are not clamped: the original accepts index<count.
 */
#endif
