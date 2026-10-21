#include "deck-coordinate-contract.h"
int biwn_deck_coordinate_call(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,
 biwn_world_cpu_service service,void *opaque,uint32_t budget) {
 struct biwn_deck_context s;
 if(!bus||!cpu||!service||!budget||!bus->read16||!bus->read32||
    !bus->write16||!bus->write32||cpu->pc!=0x11d1au)return 1;
 s=(struct biwn_deck_context){bus,*cpu,service,opaque,budget,0};
 biwn_deck_coordinate_body(&s);
 if(s.error)return s.error;
 if(s.cpu.pc!=0x11e62u)return 5;
 s.cpu.pc=deck_pop(&s);if(s.error)return s.error;
 *cpu=s.cpu;return 0;
}
