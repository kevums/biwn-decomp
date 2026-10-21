#ifndef BIWN_STARTUP_SERVICES_H
#define BIWN_STARTUP_SERVICES_H
#include "biwn_world_update.h"
typedef int (*biwn_startup_write8)(void *,uint32_t,uint8_t);
enum biwn_services_status {BIWN_SERVICES_OK=0,BIWN_SERVICES_BAD_ARGUMENT=1,
 BIWN_SERVICES_BUS_ERROR=2,BIWN_SERVICES_DEPENDENCY_ERROR=3};
/* Complete source caller bodies, logical raw stack arguments, full D0.
 * Nested calls are explicit bus dependencies, not an implementation claim.
 * Private stack/CCR and other caller-saved registers are outside this API.
 * Partial bus effects remain on error, out_D0 remains unchanged.
 * 18160 emits source MMIO accesses; backend timing/hardware is external. */
enum biwn_services_status biwn_startup_service(struct biwn_world_bus *,
 biwn_startup_write8,uint32_t entry,uint32_t incoming_D0,uint32_t *out_D0);
/* Supported entries: E2F4,18160,21242,18BA8,DFC0,1AEDA,F0C0. */
#endif
