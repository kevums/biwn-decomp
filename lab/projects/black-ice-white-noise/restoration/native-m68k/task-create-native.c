#include <stdint.h>

uint32_t biwn_native_task_create_body(uint32_t callback, uint32_t parameter, uint32_t *current_out)
{
    volatile uint32_t *const current_ptr = (volatile uint32_t *)0xC0920u;
    volatile uint32_t *const free_ptr    = (volatile uint32_t *)0xC0924u;

    uint32_t current = *current_ptr;
    uint32_t free    = *free_ptr;

    *current_out = current;

    if (free == 0u) {
        return 0u;
    }

    *free_ptr = *(volatile uint32_t *)free;

    *(volatile uint32_t *)free = *(volatile uint32_t *)current;

    *(volatile uint32_t *)(free + 4u) = current;

    *(volatile uint32_t *)current = free;

    uint32_t successor = *(volatile uint32_t *)free;

    *(volatile uint32_t *)(successor + 4u) = free;

    *(volatile uint32_t *)(free + 8u)  = callback;
    *(volatile uint32_t *)(free + 16u) = callback;
    *(volatile uint32_t *)(free + 30u) = parameter;

    uint32_t stack_top = free + 0x400u;
    *(volatile uint32_t *)(free + 12u) = stack_top;

    *(volatile uint16_t *)(free + 20u) = 0u;
    *(volatile uint32_t *)(free + 26u) = 0u;
    *(volatile uint32_t *)(free + 22u) = 0u;
    *(volatile uint32_t *)(free + 34u) = 0u;

    return free;
}
