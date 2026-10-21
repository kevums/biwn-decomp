/* Coordinator recovery: structured object scan and geometry collection.
 * Physical CPU register bookkeeping preserves the original service ABI. */
#include "deck-scene-contract.h"
static void update_active_objects(struct biwn_deck_context *s) {
 uint32_t *r=s->cpu.registers,v;
 deck_push(s,r[10]);deck_nz(s,r[10],32);
 deck_push(s,r[2]);deck_nz(s,r[2],32);
 r[2]&=0xffff0000u;deck_nz(s,r[2]&65535u,16);r[10]=0x400ea;
 do {
  r[0]=(r[0]&0xffff0000u)|(r[2]&65535u);deck_nz(s,r[0],16);
  r[0]=deck_sx16(r[0])*46u;deck_nz(s,r[0],32);
  v=deck_read(s,r[10]+r[0],2);(void)scene_alu16(s,v,1,1,1);
  if(s->cpu.sr&4u){
   deck_call(s,0x11b4c,0x11848);
   v=deck_read(s,0x40104,4);deck_nz(s,v,32);
   if(!(s->cpu.sr&12u))deck_call(s,0x1186a,0x11856);
   deck_call(s,0x11d1a,0x1185c);
  }
  v=scene_alu16(s,r[2],1,0,0);r[2]=(r[2]&0xffff0000u)|v;
  (void)scene_alu16(s,r[2],15,1,1);
  if(s->error)return;
 } while((s->cpu.sr&4u)||(((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u));
 r[2]=deck_pop(s);deck_nz(s,r[2],32);r[10]=deck_pop(s);s->cpu.pc=0x11868;
}
static void collect_geometry(struct biwn_deck_context *s) {
 uint32_t *r=s->cpu.registers,v;
 deck_push(s,r[3]);deck_nz(s,r[3],32);
 deck_push(s,r[2]);deck_nz(s,r[2],32);
 scene_push_word(s,7);deck_nz(s,7,16);scene_push_word(s,1);deck_nz(s,1,16);
 deck_call(s,0x10968,0x11ae6);
 deck_write(s,0x49b88,4,0);deck_nz(s,0,32);
 r[1]=32;deck_nz(s,r[1],32);
 r[1]=deck_alu(s,r[1],deck_read(s,0x40100,4),0,0);
 r[3]=0;deck_nz(s,0,32);r[3]=255;deck_nz(s,255,8);
 r[1]&=r[3];deck_nz(s,r[1],32);
 r[2]=32;deck_nz(s,r[2],32);
 r[2]=deck_alu(s,r[2],deck_read(s,0x400f8,4),0,0);
 r[2]&=r[3];deck_nz(s,r[2],32);
 r[0]=32;deck_nz(s,r[0],32);
 r[0]=deck_alu(s,r[0],deck_read(s,0x400fc,4),0,0);
 r[0]&=r[3];deck_nz(s,r[0],32);
 /* Round wrapped 8-bit angles to four sectors, then select the original
  * orientation word using strides 32,8,2 in the 64-entry lookup table. */
 r[1]=scene_shift(s,r[1],6,0);r[1]=scene_shift(s,r[1],5,1);
 r[0]=scene_shift(s,r[0],6,0);r[0]=scene_shift(s,r[0],3,1);
 r[1]=deck_alu(s,r[1],0x3d7a2,0,0);
 r[2]=scene_shift(s,r[2],6,0);r[2]=deck_alu(s,r[2],r[2],0,0);
 r[8]=r[0];r[8]+=r[1];
 v=deck_read(s,r[8]+r[2],2);deck_write(s,0x403ce,2,v);deck_nz(s,v,16);
 deck_call(s,0x11384,0x11b32);
 deck_call(s,0x10ba4,0x11b38);
 deck_call(s,0x1142e,0x11b3e);
 deck_call(s,0x10734,0x11b44);
 deck_adjust(s,4);
 r[2]=deck_pop(s);deck_nz(s,r[2],32);
 r[3]=deck_pop(s);deck_nz(s,r[3],32);s->cpu.pc=0x11b4a;
}
int biwn_deck_scene_body(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,
 biwn_world_cpu_service service,void *opaque,uint32_t budget) {
 struct biwn_deck_context s;
 if(!bus||!cpu||!service||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||
    (cpu->pc!=0x11828&&cpu->pc!=0x11ad4))return 1;
 s=(struct biwn_deck_context){bus,*cpu,service,opaque,budget,0};
 if(cpu->pc==0x11828)update_active_objects(&s);else collect_geometry(&s);
 if(s.error)return s.error;*cpu=s.cpu;return 0;
}
int biwn_deck_scene_call(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,
 biwn_world_cpu_service service,void *opaque,uint32_t budget) {
 struct biwn_task_cpu s;uint32_t ret;int status;if(!cpu)return 1;s=*cpu;
 status=biwn_deck_scene_body(bus,&s,service,opaque,budget);if(status)return status;
 if(bus->read32(bus->context,s.registers[15]&0xffffffu,&ret))return 2;
 s.pc=ret;s.registers[15]+=4;if(s.sr&0x2000u)s.ssp=s.registers[15];else s.usp=s.registers[15];*cpu=s;return 0;
}
