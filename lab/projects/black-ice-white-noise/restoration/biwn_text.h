#ifndef BIWN_TEXT_H
#define BIWN_TEXT_H
#include <stdint.h>

/* Analyst translations of CPU helpers14776,147A6 and149AE. External device
 * processing is not implemented. Callbacks return zero on success. Read
 * budgets, argument errors and callback errors are added host behavior;
 * effects before an error remain and original loops have no read limit. */
typedef int (*biwn_text_r8)(void *,uint32_t,uint8_t *);
typedef int (*biwn_text_r16)(void *,uint32_t,uint16_t *);
typedef int (*biwn_text_w32)(void *,uint32_t,uint32_t);
struct biwn_text_bus {
    biwn_text_r8 read8;
    biwn_text_r16 read16;
    biwn_text_w32 write32;
    void *context;
    uint32_t read_budget;
};
struct biwn_text_args {
    uint16_t x,y;
    uint32_t text,target,target_flags,font;
    uint16_t color,mode;
};
enum biwn_text_result {
    BIWN_TEXT_OK=0,BIWN_TEXT_BAD_ARGUMENT=1,
    BIWN_TEXT_READ_LIMIT=2,BIWN_TEXT_BUS_ERROR=3
};
/* Pure original14776 result in full D0; low16 wrapping arithmetic. */
uint32_t biwn_text_alignment(uint16_t position,uint16_t width,uint16_t mask);
/* Original147A6 format3 path, also called by149AE. */
enum biwn_text_result biwn_text_draw_format3(struct biwn_text_bus *,const struct biwn_text_args *,uint32_t *d0);
/* Whole original149AE, including its147A6 delegation. Output is full D0
 * (height highword plus advances with original wrapping), not host status.
 * On host errors d0 is left unchanged; MMIO writes may already have occurred. */
enum biwn_text_result biwn_text_draw(struct biwn_text_bus *,const struct biwn_text_args *,uint32_t *d0);
#endif
