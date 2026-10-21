#ifndef BIWN_INVENTORY_DRAW_H
#define BIWN_INVENTORY_DRAW_H
#include <stdint.h>

/* Analyst translation of the whole CPU routine [1B786,1BC78).
 * Original names/ABI and device timing are not reconstructed. Text and sprite
 * callbacks model call boundaries149AE/E2B8; actual glyph/pixel work remains
 * the backend's responsibility. Callbacks return zero on success.
 */
struct biwn_inventory_text {
    uint16_t x,y;
    uint32_t text_address,target,target_flags,font;
    uint16_t color,mode;
    const char *local_text; /* First money string only; text_address then0. */
};
typedef int (*biwn_draw_r8)(void *,uint32_t,uint8_t *);
typedef int (*biwn_draw_r16)(void *,uint32_t,uint16_t *);
typedef int (*biwn_draw_r32)(void *,uint32_t,uint32_t *);
typedef int (*biwn_draw_w32)(void *,uint32_t,uint32_t);
typedef int (*biwn_draw_sprite)(void *,uint32_t,uint32_t,uint32_t);
typedef int (*biwn_draw_text)(void *,const struct biwn_inventory_text *);
struct biwn_inventory_draw_bus {
    biwn_draw_r8 read8;
    biwn_draw_r16 read16;
    biwn_draw_r32 read32;
    biwn_draw_w32 write32;
    biwn_draw_sprite sprite;
    biwn_draw_text text;
    void *context;
};
enum biwn_inventory_draw_result {
    BIWN_DRAW_OK=0,BIWN_DRAW_BAD_ARGUMENT=1,
    BIWN_DRAW_BUS_ERROR=2,BIWN_DRAW_DEPENDENCY_ERROR=3
};
/* Image-specific "$%ld" money formatting is implemented locally, checked
 * against the original CPU formatter for the preserved format literal.
 * Source rereads and command-store order are retained, without adding waits.
 * Host callback errors retain prior writes; they are not original exceptions.
 */
enum biwn_inventory_draw_result biwn_inventory_draw(struct biwn_inventory_draw_bus *);
#endif
