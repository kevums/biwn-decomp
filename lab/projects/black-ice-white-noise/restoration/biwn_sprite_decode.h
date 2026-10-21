#ifndef BIWN_SPRITE_DECODE_H
#define BIWN_SPRITE_DECODE_H
#include <stdint.h>

/* Analyst translation of GPU overlay: CPU4B08..4D68 maps to F03240..F034A0.
 * Outputs the original16bit words; display color conversion and blitting are
 * not part of this routine. Callbacks return zero on success. Source reads
 * include the original literal-run trailing prefetch, even though discarded.
 * Host read limits/errors are added guards; partial writes remain. */
typedef int (*biwn_sprite_r8)(void *,uint32_t,uint8_t *);
typedef int (*biwn_sprite_r16)(void *,uint32_t,uint16_t *);
typedef int (*biwn_sprite_r32)(void *,uint32_t,uint32_t *);
typedef int (*biwn_sprite_w16)(void *,uint32_t,uint16_t);
typedef int (*biwn_sprite_w32)(void *,uint32_t,uint32_t);
struct biwn_sprite_bus {
    biwn_sprite_r8 read8;
    biwn_sprite_r16 read16;
    biwn_sprite_r32 read32;
    biwn_sprite_w16 write16;
    biwn_sprite_w32 write32;
    void *context;
    uint32_t read_budget;
};
struct biwn_sprite_result {
    uint32_t width,height,declared_pixels,emitted_pixels;
    int16_t origin_x,origin_y;
    uint32_t source_next,destination_next,palette,remaining_counter;
    uint32_t reservoir,bits_left;
};
enum biwn_sprite_status {
    BIWN_SPRITE_OK=0,BIWN_SPRITE_BAD_ARGUMENT=1,
    BIWN_SPRITE_READ_LIMIT=2,BIWN_SPRITE_BUS_ERROR=3
};
/* Zero dimensions still consume one run; run writes are not clipped to the
 * declared pixel count, matching the original. Signed origin words go to
 * destination-12/-10. Completion writes0toF0211C. No GPU register/CCR ABI,
 * timing, mailbox handshaking or full-game reconstruction is provided here.
 * Result is filled only on success; original GPU has no corresponding struct. */
enum biwn_sprite_status biwn_sprite_decode(struct biwn_sprite_bus *,uint32_t base,uint32_t index,uint32_t destination,struct biwn_sprite_result *);
#endif
