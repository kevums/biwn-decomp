/* Coordinator bridge; original scheduler owns task selection and CPU frames. */
#include "biwn_coordinate_yield.h"
static const unsigned saved_registers[11]={2,3,4,5,6,7,10,11,12,13,14};
int biwn_coordinate_yield_begin(struct biwn_world_bus *bus,struct biwn_coordinate_yield *ticket,
 const struct biwn_coordinate_request *request,struct biwn_task_cpu *cpu,uint32_t limit)
{
 struct biwn_coordinate_yield next={0};struct biwn_task_cpu selected;
 uint32_t target;unsigned i;int status;
 if(!bus||!ticket||!request||!cpu||!limit||!bus->read32||!bus->read16||
    !bus->write16||!bus->write32||ticket->phase||!request->context||!request->sequence||
    request->kind!=BIWN_COORDINATE_CALL||request->address!=0xdf60u||
    request->argument_count||request->incoming_d0!=cpu->registers[0])
  return BIWN_COORDINATE_YIELD_BAD_ARGUMENT;
 if(cpu->pc!=0xdf60u||(cpu->sr&0x2000u)||cpu->registers[15]>UINT32_MAX-4u)
  return BIWN_COORDINATE_YIELD_BAD_FRAME;
 if(bus->read32(bus->context,cpu->registers[15],&target)||
    bus->read32(bus->context,0xc0920u,&next.owner))return BIWN_COORDINATE_YIELD_BUS_ERROR;
 if(target!=0x18faau||!next.owner)return BIWN_COORDINATE_YIELD_BAD_FRAME;
 next.context=request->context;next.sequence=request->sequence;
 next.return_sp=cpu->registers[15]+4u;next.phase=1;
 for(i=0;i<11;i++)next.saved[i]=cpu->registers[saved_registers[i]];
 selected=*cpu;status=biwn_scheduler_yield(bus,&selected,limit);
 if(status)return BIWN_COORDINATE_YIELD_SCHEDULER_ERROR;
 *ticket=next;*cpu=selected;return BIWN_COORDINATE_YIELD_PENDING;
}
int biwn_coordinate_yield_poll(struct biwn_world_bus *bus,struct biwn_coordinate_yield *ticket,
 const struct biwn_task_cpu *cpu,struct biwn_coordinate_completion *completion)
{
 uint32_t owner;unsigned i;struct biwn_coordinate_completion reply={0};
 if(!bus||!ticket||!cpu||!completion||!bus->read32||!ticket->phase||
    !ticket->context||!ticket->sequence)return BIWN_COORDINATE_YIELD_BAD_ARGUMENT;
 if(ticket->phase==2)return BIWN_COORDINATE_YIELD_CONSUMED;
 if(ticket->phase!=1)return BIWN_COORDINATE_YIELD_BAD_ARGUMENT;
 if(bus->read32(bus->context,0xc0920u,&owner))return BIWN_COORDINATE_YIELD_BUS_ERROR;
 if(owner!=ticket->owner||cpu->pc!=0x18faau)return BIWN_COORDINATE_YIELD_PENDING;
 if((cpu->sr&0x2000u)||cpu->registers[15]!=ticket->return_sp)
  return BIWN_COORDINATE_YIELD_BAD_FRAME;
 for(i=0;i<11;i++)if(cpu->registers[saved_registers[i]]!=ticket->saved[i])
  return BIWN_COORDINATE_YIELD_BAD_FRAME;
 reply.context=ticket->context;reply.sequence=ticket->sequence;reply.value=cpu->registers[0];
 *completion=reply;ticket->phase=2;return BIWN_COORDINATE_YIELD_COMPLETE;
}
