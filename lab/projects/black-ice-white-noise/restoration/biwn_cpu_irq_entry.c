#include "biwn_cpu_irq_entry.h"
int biwn_cpu_irq_entry(struct biwn_world_bus *bus,
 const struct biwn_task_cpu *input,unsigned level,unsigned resolved_vector,
 struct biwn_task_cpu *output)
{
    struct biwn_task_cpu next;
    uint32_t handler;
    uint16_t old_sr;
    if (!bus || !input || !output || !bus->read32 || !bus->write16 ||
        !bus->write32 || level > 7u || resolved_vector > 255u ||
        (input->sr & ~0x271fu))
        return 1;
    next = *input;
    old_sr = input->sr;
    if (!(old_sr & 0x2000u)) {
        next.usp = next.registers[15];
        next.registers[15] = next.ssp;
    }
    next.sr = (uint16_t)((old_sr & ~0x0700u) | 0x2000u | (level << 8));
    /* The pinned original fetches the vector BEFORE either stack write. */
    if (bus->read32(bus->context, resolved_vector * 4u, &handler))
        return 2;
    if (!handler && bus->read32(bus->context, 15u * 4u, &handler))
        return 2;
    next.registers[15] -= 4u;
    if (bus->write32(bus->context, next.registers[15], input->pc))
        return 2;
    next.registers[15] -= 2u;
    if (bus->write16(bus->context, next.registers[15], old_sr))
        return 2;
    next.ssp = next.registers[15];
    next.pc = handler;
    *output = next;
    return 0;
}
