#include "faces-contract.h"
int biwn_geometry_faces_service(struct biwn_world_bus *b,struct biwn_task_cpu *cpu,biwn_world_cpu_service service,void *opaque,uint32_t helper_budget,uint32_t iteration_budget){
 struct biwn_deck_context s;
 if(!b||!cpu||cpu->pc!=0x1142e||!service||!helper_budget||!b->read16||!b->read32||!b->write16||!b->write32)return 1;
 s=(struct biwn_deck_context){b,*cpu,service,opaque,helper_budget,0};biwn_geometry_faces_body(&s,iteration_budget);
 if(s.error)return s.error;*cpu=s.cpu;return 0;
}
