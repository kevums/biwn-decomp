#ifndef BIWN_DEBUG_OVERLAY_H
#define BIWN_DEBUG_OVERLAY_H
#include "biwn_world_update.h"
/* Analyst name for complete10734..10966. scratch is mapped guest RAM,
 * corresponding to original entrySP-54, with at least54 bytes available.
 * Formatter1B45A logical args[scratch,format,value] are three longs.
 * Text149AE args[xword,yword,scratch,target,flags,font,colorword,modeword].
 * Full D0 in/out at calls; private stack/CCR/otherregisters/timing excluded.
 * Host status0 success,1 arguments,2bus,3helper; earlier effects persist and
 * out_D0 remains unchanged on errors. Device behavior comes from callbacks. */
int biwn_debug_overlay(struct biwn_world_bus *,uint32_t scratch,
                        uint32_t incoming_D0,uint32_t *out_D0);
#endif
