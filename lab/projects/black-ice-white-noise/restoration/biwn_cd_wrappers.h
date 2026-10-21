#ifndef BIWN_CD_WRAPPERS_H
#define BIWN_CD_WRAPPERS_H
#include "biwn_world_update.h"
/* Coordinator recovered D2F0..D304 and D306.
 * At BIOS303C the three callback values are register seeds A0,A1,D0,
 * rather than original stack arguments. BIOS3042 receives no logical args.
 * Callback D0 is in/out. Original private A2 save/restore, other registers,
 * CCR and timing are outside this portable interface.
 * Host1badargs/3dependency errors retain effects and leave output untouched.
 */
int biwn_cd_read_wrapper(struct biwn_world_bus *,uint32_t,uint32_t,uint32_t,uint32_t *);
int biwn_cd_stop_wrapper(struct biwn_world_bus *,uint32_t,uint32_t *);
#endif
