/* Nested service stops before its logical RTS, consumed by parent deck_call. */
#include "plane-contract.h"
int biwn_plane_layout_service(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu){
 struct biwn_deck_context s;
 if(!bus||!cpu||cpu->pc!=0x110d4||!bus->read16||!bus->read32||!bus->write16)return 1;
 s=(struct biwn_deck_context){bus,*cpu,0,0,0,0};biwn_plane_layout_body(&s);
 if(s.error)return s.error;*cpu=s.cpu;return 0;
}
