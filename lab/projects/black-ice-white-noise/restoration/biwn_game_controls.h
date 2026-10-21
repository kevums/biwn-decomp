#ifndef BIWN_GAME_CONTROLS_H
#define BIWN_GAME_CONTROLS_H
#include "biwn_input_dispatch.h"
/* Readable control-flow component: input dispatcher -> attack effect ->
 * indexed RNG, signed division/remainder, multiplication and animation
 * advance/enqueue, raw controller polling, elevator input, resource get/release, allocation/free
 * and compaction/copy. Elevator scene exit20F0C executes source cleanup;
 * new-scene setup20F78 remains external.
 * Resource stream loading (1B044), waiting (DF8C) and signaling (DF9C)
 * remain external bus services. The host bus must
 * supply source blitter MMIO effects if a large copy is requested.
 * Animation catch-up and memory work are bounded to1024steps per call; an
 * exhausted/nonprogressing sequence reports a nested dependency error.
 * These bodies
 * execute C directly. Other original helper addresses remain explicit calls
 * through the supplied bus; no original CPU fallback occurs in this module.
 * Same public D0/ordered bus/error contract as biwn_input_dispatch. Nested
 * component errors become dispatcher DEPENDENCY_ERROR. This is not a full
 * gameplay runtime, CPU-register/CCR implementation or standalone port.
 */
enum biwn_dispatch_status biwn_game_controls(struct biwn_world_bus *,
 biwn_input_write8,uint32_t loop_budget,uint32_t incoming_d0,uint32_t *out_d0);
/* Executes elevator labels/floor display190BC as readable C as well.
 * scratch is a reserved mapped16byte private buffer; original input entrySP-46.
 * Formatter1B45A uses recovered static C and a private argument frame;
 * its saved-register seeds are not a CPU ABI claim. Panel refresh12620 and
 * text149AE execute source C and emit actual blitter MMIO writes through
 * the host bus. The host supplies blitter processing. Reserve at
 * least1024mapped private stack bytes below scratch.
 * The older API
 * above retains190BC as an external call because it has no private buffer.
 */
enum biwn_dispatch_status biwn_game_controls_with_scratch(struct biwn_world_bus *,
 biwn_input_write8,uint32_t scratch,uint32_t loop_budget,uint32_t incoming_d0,uint32_t *out_d0);
#endif
