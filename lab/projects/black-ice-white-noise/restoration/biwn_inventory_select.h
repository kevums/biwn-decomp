#ifndef BIWN_INVENTORY_SELECT_H
#define BIWN_INVENTORY_SELECT_H
#include <stdint.h>

/* Analyst names; original symbols and physical controller mapping unknown.
 * Whole original helper1B718 returns in D0 and loads input intoD1.
 * Zero digit uses CLR.W, retaining incomingD0's upper16bits.
 */
uint32_t biwn_button_digit(uint32_t input, uint32_t incoming_d0);

struct biwn_selection_cpu { uint32_t d0, d1, a0; };
typedef int (*biwn_ui_read8)(void *, uint32_t, uint8_t *);
typedef int (*biwn_ui_read16)(void *, uint32_t, uint16_t *);
typedef int (*biwn_ui_read32)(void *, uint32_t, uint32_t *);
typedef int (*biwn_ui_write16)(void *, uint32_t, uint16_t);
typedef int (*biwn_ui_redraw)(void *);
struct biwn_ui_bus {
    biwn_ui_read8 read8;
    biwn_ui_read16 read16;
    biwn_ui_read32 read32;
    biwn_ui_write16 write16;
    biwn_ui_redraw redraw;
    void *context;
};
enum biwn_selection_result {
    BIWN_SELECTION_OK=0, BIWN_SELECTION_BAD_ARGUMENT=1,
    BIWN_SELECTION_BUS_ERROR=2, BIWN_SELECTION_REDRAW_ERROR=3
};

/* CPU basic block [1A1F0,1A254), not a whole original function/RTS.
 * Every source reread is retained. redraw models only the1B786call boundary;
 * actual drawing, scheduling, CCR and full-game behavior are not implemented.
 * Callback/argument errors are added host behavior; partial writes remain.
 */
enum biwn_selection_result biwn_inventory_select(struct biwn_ui_bus *, struct biwn_selection_cpu *);
#endif
