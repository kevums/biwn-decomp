#include "../../biwn_render_queue_cpu.h"
#include "../deck-scene-source/deck-scene-contract.h"
typedef void (*gpu_event_fn)(unsigned,const struct biwn_task_cpu *);
static gpu_event_fn event_callback;
void lab_scene_gpu_set_observer(gpu_event_fn callback){event_callback=callback;}
#define SCENE_GPU_WAIT_BEGIN(s) do{if(event_callback)event_callback(0,&(s)->cpu);}while(0)
#define SCENE_GPU_WAIT_END(s) do{if(event_callback)event_callback(1,&(s)->cpu);}while(0)
#include "coordinator-reference.inc"
static int run(struct biwn_world_bus *bus,struct biwn_task_cpu *state,
 biwn_input_write8 write8,biwn_world_cpu_service service,void *context,
 uint32_t budget,int stop,int full) {
 struct biwn_deck_context s;uint32_t ret;
 if(!bus||!state||!write8||!service||!budget||!bus->read8||!bus->read16||
 !bus->read32||!bus->write16||!bus->write32||(stop!=0&&stop!=1))return 1;
 if(state->pc!=0xe098u&&state->pc!=0xe0a6u&&state->pc!=0xe0f2u&&
 state->pc!=0xe148u&&state->pc!=0xe19eu&&state->pc!=0xe202u)return 7;
 s=(struct biwn_deck_context){bus,*state,service,context,budget,0};
 scene_gpu_family_body(&s);if(s.error)return s.error;
 if(full){ret=deck_pop(&s);if(s.error)return s.error;s.cpu.pc=ret;}
 *state=s.cpu;return 0;
}
enum biwn_render_queue_cpu_status biwn_render_queue_cpu_body(struct biwn_world_bus *b,struct biwn_task_cpu *s,
 biwn_input_write8 w,biwn_world_cpu_service fn,void *ctx,uint32_t limit,int stop){return run(b,s,w,fn,ctx,limit,stop,0);}
enum biwn_render_queue_cpu_status biwn_render_queue_cpu_call(struct biwn_world_bus *b,struct biwn_task_cpu *s,
 biwn_input_write8 w,biwn_world_cpu_service fn,void *ctx,uint32_t limit,int stop){return run(b,s,w,fn,ctx,limit,stop,1);}
