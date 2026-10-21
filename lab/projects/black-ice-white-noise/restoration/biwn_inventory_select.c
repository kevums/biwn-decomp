#include "biwn_inventory_select.h"

uint32_t biwn_button_digit(uint32_t input, uint32_t incoming_d0)
{
    if (input & (1u<<19)) return 1;
    if (input & (1u<<18)) return 4;
    if (input & (1u<<17)) return 7;
    if (input & (1u<<7)) return 2;
    if (input & (1u<<6)) return 5;
    if (input & (1u<<5)) return 8;
    if (input & (1u<<4)) return incoming_d0 & 0xffff0000u;
    if (input & (1u<<3)) return 3;
    if (input & (1u<<2)) return 6;
    return (input & (1u<<1)) ? 9u : 0xffffffffu;
}

#define BUS_OK(expression) do { \
    if (expression) return BIWN_SELECTION_BUS_ERROR; \
} while (0)

enum biwn_selection_result biwn_inventory_select(struct biwn_ui_bus *bus, struct biwn_selection_cpu *cpu)
{
    uint8_t byte;
    uint16_t word;
    if (!bus || !cpu || !bus->read8 || !bus->read16 || !bus->read32 || !bus->write16 || !bus->redraw)
        return BIWN_SELECTION_BAD_ARGUMENT;
    cpu->a0 = 0x49bacu;
    BUS_OK(bus->read32(bus->context, cpu->a0, &cpu->d0));
    cpu->d0 &= 0xe02feu;
    if (!cpu->d0) return BIWN_SELECTION_OK;
    BUS_OK(bus->read8(bus->context, cpu->a0+2u, &byte));
    if (byte & 2u) {
        cpu->d0 &= 0xffff0000u;
        BUS_OK(bus->read16(bus->context, 0x49d54u, &word));
        if (word != 9) {
            BUS_OK(bus->read16(bus->context, 0x49d54u, &word));
            cpu->d0 |= (uint16_t)(word+1u);
        }
        BUS_OK(bus->write16(bus->context, 0x49d54u, (uint16_t)cpu->d0));
    } else {
        BUS_OK(bus->read32(bus->context, cpu->a0, &cpu->d1));
        cpu->d0 = biwn_button_digit(cpu->d1,cpu->d0);
        BUS_OK(bus->write16(bus->context, 0x49d54u, (uint16_t)cpu->d0));
        if (!(uint16_t)cpu->d0)
            BUS_OK(bus->write16(bus->context, 0x49d54u, 10));
        BUS_OK(bus->read16(bus->context, 0x49d54u, &word));
        BUS_OK(bus->write16(bus->context, 0x49d54u, (uint16_t)(word-1u)));
    }
    BUS_OK(bus->read16(bus->context, 0x49d54u, &word));
    BUS_OK(bus->write16(bus->context, 0x49d56u, word));
    return bus->redraw(bus->context) ? BIWN_SELECTION_REDRAW_ERROR : BIWN_SELECTION_OK;
}

#undef BUS_OK
