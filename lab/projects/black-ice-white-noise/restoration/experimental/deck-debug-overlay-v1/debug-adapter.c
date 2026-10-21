#include "debug-contract.h"
int biwn_debug_overlay_cpu_call(struct biwn_world_bus *b,struct biwn_task_cpu *cpu,biwn_world_cpu_service service,void *opaque,uint32_t budget){
 struct biwn_deck_context s;uint32_t ret;
 if(!b||!cpu||cpu->pc!=0x10734||!service||!budget||!b->read16||!b->read32||!b->write16||!b->write32)return 1;
 s=(struct biwn_deck_context){b,*cpu,service,opaque,budget,0};biwn_debug_overlay_body(&s);
 if(s.error)return s.error;ret=deck_pop(&s);if(s.error)return s.error;s.cpu.pc=ret;*cpu=s.cpu;return 0;
}
