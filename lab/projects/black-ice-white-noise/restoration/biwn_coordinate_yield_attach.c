/* Coordinator backend; actual scheduler/IRQ/device execution stays clocked. */
#include "biwn_coordinate_yield_attach.h"
int biwn_coordinate_yield_attach(struct biwn_world_bus *bus,struct biwn_coordinate_yield *ticket,
 const struct biwn_coordinate_request *request,const struct biwn_task_cpu *cpu)
{
 static const unsigned saved_registers[11]={2,3,4,5,6,7,10,11,12,13,14};
 struct biwn_coordinate_yield next={0};uint32_t target;unsigned i;
 if(!bus||!ticket||!request||!cpu||!bus->read32||ticket->phase||
    !request->context||!request->sequence||request->kind!=BIWN_COORDINATE_CALL||
    request->address!=0xdf60u||request->argument_count||request->incoming_d0!=cpu->registers[0])
  return BIWN_COORDINATE_YIELD_BAD_ARGUMENT;
 if(cpu->pc!=0xdf60u||(cpu->sr&0x2000u)||cpu->registers[15]>UINT32_MAX-4u)
  return BIWN_COORDINATE_YIELD_BAD_FRAME;
 if(bus->read32(bus->context,cpu->registers[15],&target)||
    bus->read32(bus->context,0xc0920u,&next.owner))return BIWN_COORDINATE_YIELD_BUS_ERROR;
 if(target!=0x18faau||!next.owner)return BIWN_COORDINATE_YIELD_BAD_FRAME;
 next.context=request->context;next.sequence=request->sequence;
 next.return_sp=cpu->registers[15]+4u;next.phase=1;
 for(i=0;i<11;i++)next.saved[i]=cpu->registers[saved_registers[i]];
 *ticket=next;return BIWN_COORDINATE_YIELD_PENDING;
}
