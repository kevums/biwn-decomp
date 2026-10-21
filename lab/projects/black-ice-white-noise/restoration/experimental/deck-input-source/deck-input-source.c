/* Coordinator structured recovery of Deck/C-Space input, 11B4C..11D1A. */
#include "deck-input-source.h"
static unsigned bit(struct biwn_deck_context *s,uint32_t value,unsigned n) {
 unsigned set=(value>>n)&1u;s->cpu.sr=(uint16_t)((s->cpu.sr&~4u)|(set?0u:4u));return set;
}
static void input(struct biwn_deck_context *s) {
 uint32_t *r=s->cpu.registers,v;unsigned selected;
 deck_push(s,r[3]);deck_nz(s,r[3],32);deck_push(s,r[2]);deck_nz(s,r[2],32);
 deck_call(s,0xe4c0,0x11b56);
 r[1]=deck_read(s,0x49ba4,4);deck_nz(s,r[1],32);
 r[2]=deck_read(s,0x49bac,4);deck_nz(s,r[2],32);
 r[0]=r[1];deck_nz(s,r[0],32);r[3]=9;deck_nz(s,r[3],32);
 r[0]=scene_shift(s,r[0],r[3]&63u,0);
 r[0]=(r[0]&0xffff0000u)|((r[0]&65535u)&1u);deck_nz(s,r[0],16);
 deck_write(s,0x403cc,2,r[0]);deck_nz(s,r[0],16);
 deck_write(s,0x4040a,4,0);deck_nz(s,0,32);
 deck_write(s,0x40406,4,0);deck_nz(s,0,32);
 deck_write(s,0x40402,4,0);deck_nz(s,0,32);
 /* Held-direction precedence and modifier select rotation versus speed.
  * Original signed comparisons allow an increment at15 and a decrement
  * above-16. Do not clamp all other raw values as an invented behavior. */
 if(bit(s,r[1],20)){
  if(bit(s,r[1],25)){
   r[3]=2;deck_nz(s,r[3],32);deck_write(s,0x40402,4,r[3]);deck_nz(s,r[3],32);
  }else{
   r[8]=0x40104;r[3]=15;deck_nz(s,r[3],32);
   v=deck_read(s,r[8],4);(void)deck_alu(s,r[3],v,1,1);
   if(!(((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u)){
    v=deck_read(s,r[8],4);v=deck_alu(s,v,1,0,0);deck_write(s,r[8],4,v);
   }
  }
 }else if(bit(s,r[1],21)){
  if(bit(s,r[1],25)){
   r[3]=0xfffffffeu;deck_nz(s,r[3],32);deck_write(s,0x40402,4,r[3]);deck_nz(s,r[3],32);
  }else{
   r[8]=0x40104;r[3]=0xfffffff0u;deck_nz(s,r[3],32);
   v=deck_read(s,r[8],4);(void)deck_alu(s,r[3],v,1,1);
   if(((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u){
    v=deck_read(s,r[8],4);v=deck_alu(s,v,1,1,0);deck_write(s,r[8],4,v);
   }
  }
 }else{deck_write(s,0x40104,4,0);deck_nz(s,0,32);}
 if(bit(s,r[2],13)){deck_write(s,0x40400,2,1);deck_nz(s,1,16);}
 selected=0;
 if(bit(s,r[1],22)){r[3]=2;deck_nz(s,r[3],32);selected=1;}
 else if(bit(s,r[1],23)){r[3]=0xfffffffeu;deck_nz(s,r[3],32);selected=1;}
 if(selected){deck_write(s,0x4040a,4,r[3]);deck_nz(s,r[3],32);}

 /* Six face-selection paths share the same record count check, with
  * the source's special first-face texture lookup retained separately. */
 for(unsigned face=0;face<6;face++){
  static const unsigned pressed_bits[]={4,19,7,3,18,6};
  if(face==2){deck_nz(s,r[2]&255u,8);selected=(r[2]&128u)!=0;}
  else selected=bit(s,r[2],pressed_bits[face]);
  if(!selected)continue;
  r[8]=deck_read(s,0x400e6,4);v=deck_read(s,r[8]+0x88,2);
  if(!face){deck_nz(s,v,16);if(!v)continue;}
  else{(void)scene_alu16(s,v,face,1,1);if(s->cpu.sr&5u)continue;}
  scene_push_word(s,face);deck_nz(s,face,16);
  if(!face){
   deck_call(s,0x10c6e,0x11c16);
   r[0]=deck_read(s,0x403dc,4);deck_nz(s,r[0],32);r[8]=0x403e0;
   r[0]=deck_alu(s,r[0],r[0],0,0);v=deck_read(s,r[8]+r[0],2);
   scene_push_word(s,v);deck_nz(s,v,16);deck_call(s,0x10e72,0x11c2e);
  }else{
   static const uint32_t first_returns[]={0,0x11c4e,0x11c74,0x11c9c,0x11cc4,0x11cec};
   static const uint32_t second_returns[]={0,0x11c56,0x11c7c,0x11ca4,0x11ccc,0x11cf4};
   deck_call(s,0x10c6e,first_returns[face]);scene_push_word(s,0);deck_nz(s,0,16);
   deck_call(s,0x10cb6,second_returns[face]);
  }
  deck_adjust(s,4);if(s->error)return;
 }
 if(bit(s,r[2],16)){
  deck_write(s,0x4040a,4,0);deck_nz(s,0,32);
  deck_write(s,0x40406,4,0);deck_nz(s,0,32);
  deck_write(s,0x40402,4,0);deck_nz(s,0,32);deck_call(s,0x1102a,0x11d14);
 }
 r[2]=deck_pop(s);deck_nz(s,r[2],32);r[3]=deck_pop(s);deck_nz(s,r[3],32);s->cpu.pc=0x11d18;
}
int biwn_deck_input_body(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,
 biwn_world_cpu_service service,void *opaque,uint32_t budget) {
 struct biwn_deck_context s;if(!bus||!cpu||!service||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||cpu->pc!=0x11b4c)return 1;
 s=(struct biwn_deck_context){bus,*cpu,service,opaque,budget,0};input(&s);if(s.error)return s.error;*cpu=s.cpu;return 0;
}
int biwn_deck_input_call(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,
 biwn_world_cpu_service service,void *opaque,uint32_t budget) {
 struct biwn_task_cpu s;uint32_t ret;int status;if(!cpu)return 1;s=*cpu;
 status=biwn_deck_input_body(bus,&s,service,opaque,budget);if(status)return status;
 if(bus->read32(bus->context,s.registers[15]&0xffffffu,&ret))return 2;
 s.pc=ret;s.registers[15]+=4;if(s.sr&0x2000u)s.ssp=s.registers[15];else s.usp=s.registers[15];*cpu=s;return 0;
}
