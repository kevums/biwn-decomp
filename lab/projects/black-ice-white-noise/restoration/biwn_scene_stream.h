#ifndef BIWN_SCENE_STREAM_H
#define BIWN_SCENE_STREAM_H
#include "biwn_actor_creation.h"
/* Linked readable20F78 scene setup and nested parsing, texture/cache, actor,
 * memory, outdoor geometry and CD wrapper bodies. BIOS303C/3042 and DF60
 * completion/context switch remain external. Addresses decode to24physical
 * bits; stored pointer values and logical arguments retain their tag bits.
 * Odd word/long accesses stop with a host bus error; the original processor
 * address-error exception frame is outside this logical API.
 * E2B8 issues the source4B00protocol
 * through device MMIO; the host owns GPU execution/acknowledgement.
 * DF6C task creation
 * computes actual list/frame records; executing those tasks stays external.
 * scratch must map private guest RAM. It holds texture-loader handles or
 * the task creator's private RTS slot, used at separate call boundaries.
 * word_scan explicitly selects the experimental18byte loader repair (0 or1).
 * No scheduler, interrupts, physical device timing or full CPU ABI here.
 * Original partial effects persist on error; result commits on success only.
 */
int biwn_scene_stream(struct biwn_world_bus *,biwn_actor_write8,
 uint16_t mode,uint32_t scratch,uint32_t word_scan,uint32_t budget,
 uint32_t incoming_D0,uint32_t *out_D0);
struct biwn_scene_alignment_fault {
 uint32_t logical_address,physical_address,width,is_write;
};
/* Optional diagnostic variant. width0 means no alignment fault was observed;
 * other bus/dependency errors still use the returned status. Diagnostic is
 * cleared on bad arguments and filled on completion/error; out_D0 commits
 * only on success. No CPU exception frame or handler execution is emulated. */
int biwn_scene_stream_with_fault(struct biwn_world_bus *,biwn_actor_write8,
 uint16_t mode,uint32_t scratch,uint32_t word_scan,uint32_t budget,
 uint32_t incoming_D0,uint32_t *out_D0,struct biwn_scene_alignment_fault *);
/* Opt-in restoration of the pending-texture queue. Caller supplies at least
 *50 uint16_t slots (up to32767); additional IDs avoid the original count/
 *actor-list overlap. Existing stream APIs retain original overflow behavior.
 * Requires pending count0 at entry. Queue peak and fault are diagnostics,
 * including on failure; out_D0 still commits only on success. This is a
 * deliberate behavior change, not an original-program equivalence claim. */
int biwn_scene_stream_repaired_queue(struct biwn_world_bus *,biwn_actor_write8,
 uint16_t,uint32_t,uint32_t,uint32_t,uint32_t,uint32_t *,
 struct biwn_scene_alignment_fault *,uint16_t *,uint32_t,uint32_t *);
/* Original1AA40 texture initialization with the same linked loader/memory/CD
 * services. Mode1 loads actual RTXT bytes and reserves the original15slots.
 * This is separate because original callers initialize textures before scene
 * setup, not during20F78. Same scratch/wordscan/device limits apply. */
int biwn_scene_stream_textures(struct biwn_world_bus *,biwn_actor_write8,
 uint16_t mode,uint32_t scratch,uint32_t word_scan,uint32_t budget,uint32_t *out_D0);
#endif
