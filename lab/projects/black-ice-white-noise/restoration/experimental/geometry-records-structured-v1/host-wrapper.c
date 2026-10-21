#include "../../biwn_geometry_records_cpu.h"
#include "../deck-scene-source/deck-scene-contract.h"
/* Keep earlier generated providers for E220/E098, without using their170A0
 * body. The Runtime supplies actual E3E0 copy and GPU matrix providers. */
#define biwn_geometry_records_cpu_body legacy_geometry_records_body
#define biwn_geometry_records_cpu_call legacy_geometry_records_call
#include "../../biwn_geometry_records_cpu.c"
#undef biwn_geometry_records_cpu_body
#undef biwn_geometry_records_cpu_call
#undef CHECK
#ifndef GEOMETRY_RECORDS_BODY_FILE
#include "coordinator-reference.inc"
#else
#include GEOMETRY_RECORDS_BODY_FILE
#endif
static int run_readable(struct biwn_world_bus *bus,struct biwn_task_cpu *state,
 biwn_input_write8 write8,biwn_world_cpu_service service,void *context,
 uint32_t budget,int stop,int full){
 struct biwn_deck_context s;uint32_t ret;
 if(!bus||!state||!write8||!service||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||(stop!=0&&stop!=1))return 1;
 if(state->pc!=0x170a0u){
  if(state->pc==0xe220u||state->pc==0xe098u)return full?legacy_geometry_records_call(bus,state,write8,service,context,budget,stop):legacy_geometry_records_body(bus,state,write8,service,context,budget,stop);
  return 7;
 }
 s=(struct biwn_deck_context){bus,*state,service,context,budget,0};geometry_records_body(&s);
 if(s.error)return s.error;
 if(full){ret=deck_pop(&s);if(s.error)return s.error;s.cpu.pc=ret;}
 *state=s.cpu;return 0;
}
enum biwn_geometry_records_cpu_status biwn_geometry_records_cpu_body(struct biwn_world_bus *b,struct biwn_task_cpu *s,biwn_input_write8 w,biwn_world_cpu_service fn,void *ctx,uint32_t limit,int stop){return run_readable(b,s,w,fn,ctx,limit,stop,0);}
enum biwn_geometry_records_cpu_status biwn_geometry_records_cpu_call(struct biwn_world_bus *b,struct biwn_task_cpu *s,biwn_input_write8 w,biwn_world_cpu_service fn,void *ctx,uint32_t limit,int stop){return run_readable(b,s,w,fn,ctx,limit,stop,1);}
