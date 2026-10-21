#include <stdint.h>

void biwn_native_scheduler_select(uint32_t *frame)
{
    uint32_t task = frame[8];

    frame[15] = 0u;

    for (;;)
    {
        task = *(volatile uint32_t *)task;

        if (*(volatile uint32_t *)(task + 26u) != 0u)
        {
            continue;
        }

        if (*(volatile uint32_t *)(task + 34u) != 0u)
        {
            continue;
        }

        if (*(volatile uint32_t *)(task + 22u) == 0u)
        {
            frame[8] = task;
            return;
        }

        frame[0] = *(volatile uint32_t *)(task + 22u);

        uint32_t clock = *(volatile uint32_t *)0x778CCu;

        if (frame[0] > clock)
        {
            continue;
        }

        frame[15] = 1u;
        frame[8] = task;
        return;
    }
}
