/* Reference clear/rotation and internal-PC resumptions stay separate from the
 * new readable entry body. This wrapper is a host component test provider. */
#define biwn_scene_draw_cpu_body legacy_scene_draw_body
#define biwn_scene_draw_cpu_call legacy_scene_draw_call
#include "../../biwn_scene_draw_cpu.c"
#undef biwn_scene_draw_cpu_body
#undef biwn_scene_draw_cpu_call
#include "scene-context.h"
#ifndef SCENE17_BODY_FILE
#define SCENE17_BODY_FILE "coordinator-reference.inc"
#endif
#include SCENE17_BODY_FILE
static enum biwn_scene_draw_cpu_status structured_entry(
 struct biwn_world_bus *bus,struct biwn_task_cpu *state,biwn_input_write8 write8,
 biwn_world_cpu_service service,void *context,uint32_t budget,int stop,int full){
 struct biwn_deck_context s;uint32_t ret;
 if(!bus||!state||!write8||!service||!budget||!bus->read8||!bus->read16||
 !bus->read32||!bus->write16||!bus->write32||(stop!=0&&stop!=1))return 1;
 if(state->pc!=0x17e0e)return full?
 legacy_scene_draw_call(bus,state,write8,service,context,budget,stop):
 legacy_scene_draw_body(bus,state,write8,service,context,budget,stop);
 s=(struct biwn_deck_context){bus,*state,service,context,budget,0};scene17_body(&s);
 if(s.error)return(enum biwn_scene_draw_cpu_status)s.error;
 if(full){ret=deck_pop(&s);if(s.error)return(enum biwn_scene_draw_cpu_status)s.error;s.cpu.pc=ret;}
 *state=s.cpu;return 0;
}
enum biwn_scene_draw_cpu_status biwn_scene_draw_cpu_body(
 struct biwn_world_bus *b,struct biwn_task_cpu *s,biwn_input_write8 w,
 biwn_world_cpu_service fn,void *ctx,uint32_t limit,int stop){
 return structured_entry(b,s,w,fn,ctx,limit,stop,0);
}
enum biwn_scene_draw_cpu_status biwn_scene_draw_cpu_call(
 struct biwn_world_bus *b,struct biwn_task_cpu *s,biwn_input_write8 w,
 biwn_world_cpu_service fn,void *ctx,uint32_t limit,int stop){
 return structured_entry(b,s,w,fn,ctx,limit,stop,1);
}
