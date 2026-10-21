/* Local27B authored body from the coordinator-recovered contract; only Markdown
 * fences removed. Original-core/runtime verification is separate. */
#include "biwn_cpu_irq_select.h"
int biwn_cpu_irq_select(unsigned kind, unsigned previous_level, unsigned level, unsigned mask)
{
    if (kind > 1u)
        return -1;
    if (previous_level > 7u)
        return -1;
    if (level > 7u)
        return -1;
    if (mask > 7u)
        return -1;

    if (kind == 1u)
    {
        if (previous_level != 7u && level == 7u)
            return 7;
    }

    if (level > mask)
        return (int)level;
    return 0;
}
