#include <stdint.h>
#include <string.h>
#include "biwn_cpu_irq_entry.h"
struct irq_host {
    void (*read_cpu)(struct biwn_task_cpu *);
    uint32_t (*read32)(uint32_t);
    void (*write16)(uint32_t,uint32_t);
    void (*write32)(uint32_t,uint32_t);
    void (*commit)(const struct biwn_task_cpu *,uint32_t);
};
struct irq_stats { uint64_t calls,owned,errors; uint32_t error_level,error_vector,error_code; };
static struct irq_host H;
static struct irq_stats S;
static int read32(void *context,uint32_t address,uint32_t *out)
{ (void)context; *out=H.read32(address); return 0; }
static int write16(void *context,uint32_t address,uint16_t value)
{ (void)context; H.write16(address,value); return 0; }
static int write32(void *context,uint32_t address,uint32_t value)
{ (void)context; H.write32(address,value); return 0; }
int biwn_CPU_IRQ_begin(const struct irq_host *host)
{
    if (!host || !host->read_cpu || !host->read32 || !host->write16 ||
        !host->write32 || !host->commit) return 1;
    H=*host; memset(&S,0,sizeof(S)); return 0;
}
int biwn_CPU_IRQ_owner(uint32_t level,uint32_t vector)
{
    struct biwn_task_cpu before,after;
    struct biwn_world_bus bus;
    int status;
    S.calls++;
    if (S.errors) return 0;
    memset(&bus,0,sizeof(bus));
    bus.read32=read32; bus.write16=write16; bus.write32=write32;
    H.read_cpu(&before);
    status=biwn_cpu_irq_entry(&bus,&before,level,vector,&after);
    if (status) {
        S.errors++; S.error_level=level; S.error_vector=vector;
        S.error_code=(uint32_t)status; return 0;
    }
    H.commit(&after,level); S.owned++; return 1;
}
const struct irq_stats *biwn_CPU_IRQ_stats(void) { return &S; }
unsigned biwn_CPU_IRQ_host_size(void) { return sizeof(struct irq_host); }
