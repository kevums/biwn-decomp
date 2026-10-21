#include "/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/projects/black-ice-white-noise/restoration/biwn_scene_draw_cpu.h"
#include "/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/projects/black-ice-white-noise/restoration/experimental/deck-scene-source/deck-scene-contract.h"
#include "/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/runs/local-scene-clear-worker-v2/20261021T012913.731494Z/Author/host-gate/candidate-with-primitives.inc"
/* Host error limits are separate from always-successful target memory access. */
static int run(struct biwn_world_bus *bus,struct biwn_task_cpu *state,
 biwn_input_write8 write8,biwn_world_cpu_service service,void *context,
 uint32_t budget,int stop,int full){
 struct biwn_deck_context s;uint32_t ret;
 if(!bus||!state||!write8||!service||!budget||!bus->read8||!bus->read16||
 !bus->read32||!bus->write16||!bus->write32||stop)return 1;
 if(state->pc!=0xe03a)return 7;
 s=(struct biwn_deck_context){bus,*state,service,context,budget,0};
 scene_clear_body(&s);
 if(s.error)return s.error;
 if(full){ret=deck_pop(&s);if(s.error)return s.error;s.cpu.pc=ret;}
 *state=s.cpu;return 0;
}
int biwn_scene_clear_body(struct biwn_world_bus *b,struct biwn_task_cpu *s,
 biwn_input_write8 w,biwn_world_cpu_service fn,void *ctx,uint32_t limit,int stop){
 return run(b,s,w,fn,ctx,limit,stop,0);
}
int biwn_scene_clear_call(struct biwn_world_bus *b,struct biwn_task_cpu *s,
 biwn_input_write8 w,biwn_world_cpu_service fn,void *ctx,uint32_t limit,int stop){
 return run(b,s,w,fn,ctx,limit,stop,1);
}
