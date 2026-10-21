/* Coordinator structured recovery of the six-face contact scan, 1186A. */
#include "deck-face-contact.h"
static uint32_t half(struct biwn_deck_context *s,uint32_t value) {
 uint32_t result=(value>>1)|(value&0x80000000u);unsigned carry=value&1u;
 deck_nz(s,result,32);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|(carry?0x11u:0u));return result;
}
static void midpoint(struct biwn_deck_context *s,unsigned low,unsigned high,uint32_t offset) {
 uint32_t *r=s->cpu.registers;
 r[0]=deck_read(s,r[9]+low,4);deck_nz(s,r[0],32);
 r[0]=deck_alu(s,r[0],deck_read(s,r[9]+high,4),0,0);r[0]=half(s,r[0]);
 r[8]=r[0];r[8]+=deck_read(s,offset,4);
}
static void x_window(struct biwn_deck_context *s,uint32_t offset) {
 uint32_t *r=s->cpu.registers;midpoint(s,4,16,offset);
 r[1]=0xffffffe0u;deck_nz(s,r[1],32);r[1]=deck_alu(s,r[1],r[8],0,0);r[14]=r[8]+32;
}
static void y_window(struct biwn_deck_context *s,uint32_t offset) {
 uint32_t *r=s->cpu.registers;midpoint(s,8,20,offset);r[13]=r[8]-32;r[12]=r[8]+32;
}
static void z_window(struct biwn_deck_context *s,uint32_t offset) {
 uint32_t *r=s->cpu.registers;midpoint(s,12,24,offset);r[11]=r[8]-32;
 r[4]=32;deck_nz(s,r[4],32);r[4]=deck_alu(s,r[4],r[8],0,0);
}
static int greater(const struct biwn_deck_context *s) {
 return !(s->cpu.sr&4u)&&!(((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u);
}
static int less(const struct biwn_deck_context *s) {return ((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u;}
static void contact(struct biwn_deck_context *s) {
 uint32_t *r=s->cpu.registers,v,kind;
 /* MOVEM: A6,A5,A4,A3,A2,D4,D3,D2 in descending predecrement order. */
 for(unsigned i=15;i-->10;)deck_push(s,r[i]);
 deck_push(s,r[4]);deck_push(s,r[3]);deck_push(s,r[2]);
 r[8]=deck_read(s,0x400e6,4);r[0]=0;deck_nz(s,0,32);
 r[0]=(r[0]&0xffff0000u)|deck_read(s,r[8],2);deck_nz(s,r[0],16);
 r[0]=deck_asl5(s,r[0]);r[9]=r[0]+0x400c4;
 r[2]&=0xffff0000u;deck_nz(s,0,16);
 v=deck_read(s,r[8]+0x88,2);(void)scene_alu16(s,r[2],v,1,1);
 if(!(s->cpu.sr&1u))goto restore;
 do {
  if(s->error)return;if(!s->budget){s->error=4;return;}s->budget--;
  r[0]=(r[0]&0xffff0000u)|(r[2]&65535u);deck_nz(s,r[0],16);
  r[0]=deck_sx16(r[0])*20u;deck_nz(s,r[0],32);
  r[3]=16;deck_nz(s,r[3],32);r[0]=deck_alu(s,r[0],r[3],0,0);
  r[8]=r[0];r[8]+=deck_read(s,0x400e6,4);
  kind=deck_read(s,r[8],2);(void)scene_alu16(s,kind,5,1,1);
  if((s->cpu.sr&5u)!=0){
   /* Preserve the source jump-table word in D0 even though structured C
    * selects the corresponding semantic face block directly. */
   r[0]=0;deck_nz(s,0,32);r[0]=(r[0]&0xffff0000u)|deck_read(s,r[8],2);deck_nz(s,r[0],16);
   r[0]=deck_alu(s,r[0],r[0],0,0);v=deck_read(s,0x118b4+r[0],2);
   r[0]=(r[0]&0xffff0000u)|v;deck_nz(s,v,16);
   switch(kind){
   case 0:
    x_window(s,0x3d6ca);y_window(s,0x3d6ce);
    r[4]=deck_read(s,r[9]+24,4);deck_nz(s,r[4],32);
    r[4]=deck_alu(s,r[4],deck_read(s,0x3d6d2,4),0,0);r[10]=r[4];r[11]=r[10]-32;break;
   case 1:
    r[1]=deck_read(s,r[9]+4,4);deck_nz(s,r[1],32);
    r[1]=deck_alu(s,r[1],deck_read(s,0x3d6d6,4),0,0);r[10]=r[1];r[14]=r[10]+32;
    y_window(s,0x3d6da);z_window(s,0x3d6de);break;
   case 2:
    x_window(s,0x3d6e2);y_window(s,0x3d6e6);
    r[11]=deck_read(s,r[9]+12,4);r[11]+=deck_read(s,0x3d6ea,4);
    r[4]=32;deck_nz(s,32,32);r[4]=deck_alu(s,r[4],r[11],0,0);break;
   case 3:
    r[14]=deck_read(s,r[9]+16,4);r[14]+=deck_read(s,0x3d6ee,4);
    r[1]=0xffffffe0u;deck_nz(s,r[1],32);r[1]=deck_alu(s,r[1],r[14],0,0);
    y_window(s,0x3d6f2);z_window(s,0x3d6f6);break;
   case 4:
    x_window(s,0x3d6fa);
    r[13]=deck_read(s,r[9]+8,4);r[13]+=deck_read(s,0x3d6fe,4);r[12]=r[13]+32;
    z_window(s,0x3d702);break;
   case 5:
    x_window(s,0x3d706);
    r[12]=deck_read(s,r[9]+20,4);r[12]+=deck_read(s,0x3d70a,4);r[13]=r[12]-32;
    z_window(s,0x3d70e);break;
   }
  }
  /* Source kinds >5 intentionally reach this block with existing bound
   * registers. Do not invent a safe skip or zero initialization for them. */
  r[8]=deck_read(s,0x400e6,4);
  r[1]=deck_alu(s,r[1],deck_read(s,r[8]+4,4),0,0);r[14]+=deck_read(s,r[8]+4,4);
  r[13]+=deck_read(s,r[8]+8,4);r[12]+=deck_read(s,r[8]+8,4);
  r[11]+=deck_read(s,r[8]+12,4);r[4]=deck_alu(s,r[4],deck_read(s,r[8]+12,4),0,0);
  r[8]=0x400ec;(void)deck_alu(s,r[1],deck_read(s,r[8],4),1,1);if(greater(s))goto next;
  (void)deck_alu(s,r[14],deck_read(s,r[8],4),1,1);if(less(s))goto next;
  r[8]=0x400f0;(void)deck_alu(s,r[13],deck_read(s,r[8],4),1,1);if(greater(s))goto next;
  (void)deck_alu(s,r[12],deck_read(s,r[8],4),1,1);if(less(s))goto next;
  r[8]=0x400f4;(void)deck_alu(s,r[11],deck_read(s,r[8],4),1,1);if(greater(s))goto next;
  (void)deck_alu(s,r[4],deck_read(s,r[8],4),1,1);if(less(s))goto next;
  scene_push_word(s,r[2]);deck_nz(s,r[2],16);deck_call(s,0x10c6e,0x11a98);
  deck_nz(s,r[2],16);
  if(!(r[2]&65535u)){
   r[0]=deck_read(s,0x403dc,4);deck_nz(s,r[0],32);r[8]=0x403e0;
   r[0]=deck_alu(s,r[0],r[0],0,0);v=deck_read(s,r[8]+r[0],2);
   r[0]=(r[0]&0xffff0000u)|v;deck_nz(s,v,16);
  }else{r[0]&=0xffff0000u;deck_nz(s,0,16);}
  scene_push_word(s,r[0]);deck_nz(s,r[0],16);deck_call(s,0x10cb6,0x11aba);deck_adjust(s,4);break;
next:
  v=scene_alu16(s,r[2],1,0,0);r[2]=(r[2]&0xffff0000u)|v;
  r[8]=deck_read(s,0x400e6,4);v=deck_read(s,r[8]+0x88,2);(void)scene_alu16(s,r[2],v,1,1);
  if(s->error)return;
 }while(s->cpu.sr&1u);
restore:
 r[2]=deck_pop(s);r[3]=deck_pop(s);r[4]=deck_pop(s);
 for(unsigned i=10;i<15;i++)r[i]=deck_pop(s);
 s->cpu.pc=0x11ad2;
}
int biwn_deck_face_contact_body(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,biwn_world_cpu_service service,void *opaque,uint32_t budget) {
 struct biwn_deck_context s;
 if(!bus||!cpu||!service||!budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32||cpu->pc!=0x1186a)return 1;
 s=(struct biwn_deck_context){bus,*cpu,service,opaque,budget,0};contact(&s);if(s.error)return s.error;*cpu=s.cpu;return 0;
}
int biwn_deck_face_contact_call(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,biwn_world_cpu_service service,void *opaque,uint32_t budget) {
 struct biwn_task_cpu s;uint32_t ret;int status;if(!cpu)return 1;s=*cpu;
 status=biwn_deck_face_contact_body(bus,&s,service,opaque,budget);if(status)return status;
 if(bus->read32(bus->context,s.registers[15]&0xffffffu,&ret))return 2;
 s.pc=ret;s.registers[15]+=4;if(s.sr&0x2000u)s.ssp=s.registers[15];else s.usp=s.registers[15];*cpu=s;return 0;
}
