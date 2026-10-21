#include "biwn_scheduler.h"
#include <stdint.h>

int biwn_divzero_entry(struct biwn_world_bus *bus, struct biwn_task_cpu *cpu, uint32_t resume_pc) {
    if (!bus || !cpu || !bus->read32 || !bus->write16 || !bus->write32) return 1;
    if ((cpu->sr & ~0x271f) != 0) return 1;

    struct biwn_task_cpu c = *cpu;
    c.sr &= ~0x0002;
    uint16_t old_sr = c.sr;

    if ((c.sr & 0x2000) == 0) {
        c.usp = c.registers[15];
        c.registers[15] = c.ssp;
    }
    c.sr |= 0x2000;

    c.registers[15] -= 4;
    if (bus->write32(bus->context, c.registers[15], resume_pc) != 0) return 2;
    c.registers[15] -= 2;
    if (bus->write16(bus->context, c.registers[15], old_sr) != 0) return 2;

    uint32_t new_pc;
    if (bus->read32(bus->context, 20, &new_pc) != 0) return 2;
    c.pc = new_pc;
    c.ssp = c.registers[15];

    *cpu = c;
    return 11;
}