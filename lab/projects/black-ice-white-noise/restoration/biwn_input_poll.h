#ifndef BIWN_INPUT_POLL_H
#define BIWN_INPUT_POLL_H
#include "biwn_world_update.h"
/* Complete original CPU [E4C0,E53C). Four ordered word-select/long-read
 * pairs atF14000, then held/press-edge globals at49BA4/49BAC.
 * The MMIO backend supplies raw values; this is not physical-pad proof.
 * OriginalD0-D2 are preserved. Host status is separate from originalD0.
 * Added callback failures retain prior register writes and RAM stores.
 */
enum biwn_input_status { BIWN_INPUT_OK=0,BIWN_INPUT_BAD_ARGUMENT=1,BIWN_INPUT_BUS_ERROR=2 };
enum biwn_input_status biwn_input_poll(struct biwn_world_bus *);
#endif
