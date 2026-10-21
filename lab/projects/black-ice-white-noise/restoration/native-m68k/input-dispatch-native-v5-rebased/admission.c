#include <stdint.h>
int biwn_input_task_admit(uint32_t task, uint32_t sp, uint32_t sr, uint32_t reserve)
{
    uint32_t offset;
    uint32_t min_sp;
    uint32_t max_sp;
    uint32_t min_reserve;
    uint32_t max_reserve;
    uint32_t available;

    if (task < 0x000c0928u) {
        return 0;
    }

    offset = task - 0x000c0928u;

    if (offset > 100u * 1024u) {
        return 0;
    }

    if (offset % 1024u != 0u) {
        return 0;
    }

    if ((sr & 0x2000u) != 0u) {
        return 0;
    }

    if ((sp & 1u) != 0u) {
        return 0;
    }

    min_sp = task + 64u;
    max_sp = task + 1020u;

    if (sp < min_sp) {
        return 0;
    }

    if (sp > max_sp) {
        return 0;
    }

    if ((reserve & 1u) != 0u) {
        return 0;
    }

    min_reserve = 2u;
    max_reserve = 960u;

    if (reserve < min_reserve) {
        return 0;
    }

    if (reserve > max_reserve) {
        return 0;
    }

    available = sp - min_sp;

    if (available < reserve) {
        return 0;
    }

    return 1;
}
