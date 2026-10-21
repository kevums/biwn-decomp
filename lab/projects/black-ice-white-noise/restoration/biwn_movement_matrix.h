#ifndef BIWN_MOVEMENT_MATRIX_H
#define BIWN_MOVEMENT_MATRIX_H
#include <stdint.h>
/* Analyst translation of GPU4320 overlay, not original symbols.
 * Three angles use their low byte; speed is signed low16. The matrix starts
 * as identity and rotations occur in original angle2, angle1, angle3 order.
 * Existing translation words are read and incremented. Fraction stores keep
 * raw product low16, not normalized positive fractions. Halfword-aligned
 * main-RAM bases and fixed original sine table are the checked domain.
 */
struct biwn_movement_bus {
    int (*read16)(void *,uint32_t,uint16_t *);
    int (*write16)(void *,uint32_t,uint16_t);
    void *context;
    uint32_t read_budget;
};
struct biwn_movement_result {
    uint32_t matrix_and_translation[12];
    uint32_t raw_products[3];
    uint32_t final_pointer;
};
enum biwn_movement_status { BIWN_MOVEMENT_OK=0,BIWN_MOVEMENT_BAD_ARGUMENT=1,
    BIWN_MOVEMENT_READ_LIMIT=2,BIWN_MOVEMENT_BUS_ERROR=3 };
/* Host errors/read limits are added behavior; earlier stores remain.
 * GPU mailbox/dispatcher, register flags, timing and physical hardware are
 * outside this high-level algorithm. Result is committed only on success.
 */
enum biwn_movement_status biwn_movement_matrix(struct biwn_movement_bus *,
    uint32_t base,uint32_t angle1,uint32_t angle2,uint32_t angle3,uint32_t speed,
    struct biwn_movement_result *);
#endif
