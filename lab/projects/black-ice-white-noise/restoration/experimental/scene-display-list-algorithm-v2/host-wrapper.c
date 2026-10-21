#include "../../biwn_display_list_cpu.h"
#include "../deck-scene-source/deck-scene-contract.h"
#include "coordinator-reference.inc"
/* Host error limits are separate from always-successful target memory access. */
static int run(struct biwn_world_bus *bus,struct biwn_task_cpu *state,
 biwn_input_write8 write8,biwn_world_cpu_service service,void *context,
 uint32_t budget,int stop,int full){
 struct biwn_deck_context s;uint32_t ret;
 if(!bus||!state||!write8||!service||!budget||!bus->read8||!bus->read16||
 !bus->read32||!bus->write16||!bus->write32||(stop!=0&&stop!=1))return 1;
 if(state->pc!=0x185b2)return 7;
 s=(struct biwn_deck_context){bus,*state,service,context,budget,0};
 scene_display_list_body(&s);
 if(s.error)return s.error;
 if(full){ret=deck_pop(&s);if(s.error)return s.error;s.cpu.pc=ret;}
 *state=s.cpu;return 0;
}
enum biwn_display_list_cpu_status biwn_display_list_cpu_body(struct biwn_world_bus *b,struct biwn_task_cpu *s,
 biwn_input_write8 w,biwn_world_cpu_service fn,void *ctx,uint32_t limit,int stop){
 return run(b,s,w,fn,ctx,limit,stop,0);
}
enum biwn_display_list_cpu_status biwn_display_list_cpu_call(struct biwn_world_bus *b,struct biwn_task_cpu *s,
 biwn_input_write8 w,biwn_world_cpu_service fn,void *ctx,uint32_t limit,int stop){
 return run(b,s,w,fn,ctx,limit,stop,1);
}
