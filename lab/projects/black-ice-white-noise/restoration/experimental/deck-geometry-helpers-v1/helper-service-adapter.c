/* Coordinator adapter: a nested service stops at its own outer RTS.
 * The parent deck_call consumes that return word. */
#include "helper-contract.h"
int biwn_geometry_helper_service(struct biwn_world_bus *bus,biwn_deck_write8 w8,struct biwn_task_cpu *cpu,
 biwn_world_cpu_service service,void *opaque,uint32_t byte_budget) {
 struct biwn_deck_context s;
 if(!bus||!cpu||!w8||!service||!byte_budget)return 1;
 s=(struct biwn_deck_context){bus,*cpu,service,opaque,1,0};biwn_geometry_helper_body(&s,w8,byte_budget);
 if(s.error)return s.error;*cpu=s.cpu;return 0;
}
