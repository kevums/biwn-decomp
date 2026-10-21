/* Coordinator ABI and added host-error behavior; algorithm body is separate. */
#include "helper-contract.h"
int biwn_geometry_helper_call(struct biwn_world_bus *bus,biwn_deck_write8 w8,struct biwn_task_cpu *cpu,
 biwn_world_cpu_service service,void *opaque,uint32_t helper_budget,uint32_t byte_budget) {
 struct biwn_deck_context s;uint32_t ret;
 if(!bus||!cpu||!w8||!service||!helper_budget||!byte_budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||
    (cpu->pc!=0x10968&&cpu->pc!=0x10ba4&&cpu->pc!=0x11384))return 1;
 s=(struct biwn_deck_context){bus,*cpu,service,opaque,helper_budget,0};biwn_geometry_helper_body(&s,w8,byte_budget);
 if(s.error)return s.error;ret=deck_pop(&s);if(s.error)return s.error;s.cpu.pc=ret;*cpu=s.cpu;return 0;
}
