/* Coordinator recovery: complete outer Deck task, not the original source. */
#include "deck-task-source.h"

/* A dependency may suspend inside the scheduler. Preserve its live stack;
 * never consume its outstanding return address when status 6 is reported. */
static void invoke(struct biwn_deck_context *s,uint32_t target,uint32_t ret) {
 uint32_t sp,value;int status;
 if(s->error)return;
 if(!s->budget){s->error=4;return;}s->budget--;
 deck_push(s,ret);s->cpu.pc=target;sp=s->cpu.registers[15];
 if(s->error)return;
 status=s->service(s->opaque,s->bus,&s->cpu,target);
 if(status==6&&(s->cpu.pc==0xdf60u||s->cpu.pc==0xdf8cu)){s->error=6;return;}
 if(status){s->error=3;return;}
 if(s->cpu.registers[15]!=sp){s->error=5;return;}
 value=deck_pop(s);if(s->error)return;
 if(value!=ret){s->error=5;return;}s->cpu.pc=ret;
}
#define CALL(target,ret) do{invoke(&s,(target),(ret));if(s.error)goto finish;}while(0)
#define BUS_OK() do{if(s.error)goto finish;}while(0)

int biwn_deck_task_resume(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,
 biwn_world_cpu_service service,void *opaque,uint32_t helper_budget,uint32_t poll_budget) {
 struct biwn_deck_context s;uint32_t *r,v,mode;
 if(!bus||!cpu||!service||!helper_budget||!poll_budget||!bus->read16||!bus->read32||!bus->write16||!bus->write32)return 1;
 s=(struct biwn_deck_context){bus,*cpu,service,opaque,helper_budget,0};r=s.cpu.registers;
 /* Continuations correspond to semantic calls, not individual instructions.
  * They permit a real dependency to yield and later return via the scheduler. */
 switch(cpu->pc){
 case 0x11e6c:goto initialize;
 case 0x11e86:goto iteration;
 case 0x11e8c:goto choose_mode;
 case 0x11ec4:goto geometry_overlay;
 case 0x11ed6:goto reset_geometry;
 case 0x11edc:goto geometry_cleanup;
 case 0x11ee4:goto display;
 case 0x11f12:goto select_mail_face;
 case 0x11f1a:goto mail_texture;
 case 0x11f32:goto mail_coordinates;
 case 0x11f38:goto mail_cleanup;
 case 0x11f4a:goto submit_display;
 case 0x11f50:goto wait_display;
 case 0x11f58:goto end_display;
 case 0x11f5e:goto tail_update;
 case 0x11f64:goto boundary;
 case 0x11f6a:goto finish;
 default:return 1;
 }
initialize:
 /* LINK A6,-8, then copy the two original local initializer words. */
 deck_push(&s,r[14]);r[14]=r[15];deck_adjust(&s,0xfffffff8u);
 v=deck_read(&s,0x11e64,4);deck_write(&s,r[14]-8,4,v);deck_nz(&s,v,32);
 v=deck_read(&s,0x11e68,4);deck_write(&s,r[14]-4,4,v);deck_nz(&s,v,32);BUS_OK();
 CALL(0x10990,0x11e86);goto boundary;
iteration:
 CALL(0x11828,0x11e8c);
choose_mode:
 v=deck_read(&s,0x403d6,2);r[0]=(r[0]&0xffff0000u)|v;deck_nz(&s,v,16);BUS_OK();
 mode=v;(void)scene_alu16(&s,r[0],1,1,1);
 if(mode==1)goto display;
 if((mode&0x8000u)||mode<=1){
  deck_nz(&s,r[0],16);if(mode)goto display;
  /* Ordinary geometry mode; the optional dirty-face reset retains its
   * word argument until both helpers have returned. */
  deck_push(&s,0);deck_nz(&s,0,32);
  v=deck_read(&s,0xbd83c,4);deck_push(&s,v);deck_nz(&s,v,32);BUS_OK();
  CALL(0xe03a,0x11ec4);
geometry_overlay:
  deck_adjust(&s,8);v=deck_read(&s,0x40400,2);deck_nz(&s,v,16);BUS_OK();
  if(!v)goto geometry_collect;
  scene_push_word(&s,0);deck_nz(&s,0,16);CALL(0x10c6e,0x11ed6);
reset_geometry:
  CALL(0x1102a,0x11edc);
geometry_cleanup:
  deck_adjust(&s,2);
geometry_collect:
  CALL(0x11ad4,0x11ee4);goto display;
 }
 (void)scene_alu16(&s,r[0],2,1,1);
 if(mode==2){
  /* UNLK restores the original A6 and stack bank, without changing CCR. */
  r[15]=r[14];deck_bank(&s);r[14]=deck_pop(&s);s.cpu.pc=0x11f6a;goto finish;
 }
 (void)scene_alu16(&s,r[0],3,1,1);if(mode!=3)goto display;
 /* Mail view has a different argument layout and keeps it through face,
  * texture and coordinate calls. PEA does not set condition flags. */
 deck_push(&s,r[14]-8);
 scene_push_word(&s,180);deck_nz(&s,180,16);
 scene_push_word(&s,224);deck_nz(&s,224,16);
 deck_push(&s,0x3e20);
 v=deck_read(&s,0xbd830,4);deck_push(&s,v);deck_nz(&s,v,32);
 deck_push(&s,0x4c3e0);r[8]=deck_read(&s,0x400e6,4);
 v=deck_read(&s,r[8]+0x8e,4);deck_push(&s,v);deck_nz(&s,v,32);BUS_OK();
 CALL(0x16bf4,0x11f12);
select_mail_face:
 scene_push_word(&s,0);deck_nz(&s,0,16);CALL(0x10c6e,0x11f1a);
mail_texture:
 r[0]=deck_read(&s,0x403dc,4);deck_nz(&s,r[0],32);r[8]=0x403e0;
 r[0]=deck_alu(&s,r[0],r[0],0,0);v=deck_read(&s,r[8]+r[0],2);
 scene_push_word(&s,v);deck_nz(&s,v,16);BUS_OK();CALL(0x10e72,0x11f32);
mail_coordinates:
 CALL(0x11d1a,0x11f38);
mail_cleanup:
 deck_adjust(&s,28);
display:
 v=deck_read(&s,0x49b88,4);deck_nz(&s,v,32);BUS_OK();
 if(!v||(v&0x80000000u))goto end_display;
 CALL(0xe19e,0x11f4a);
submit_display:
 CALL(0xe202,0x11f50);
wait_display:
 /* A bounded host wait preserves the volatile reread and all completed
  * work. It reports a continuation; it does not invent an IRQ or clock. */
 for(uint32_t polls=0;polls<poll_budget;polls++){
  v=deck_read(&s,0x10a684,4);deck_nz(&s,v,32);BUS_OK();
  if(!v)goto end_display;
 }
 s.cpu.pc=0x11f50;s.error=6;goto finish;
end_display:
 CALL(0xe098,0x11f5e);
tail_update:
 CALL(0x17f14,0x11f64);
boundary:
 s.cpu.pc=0x11e86;s.error=6;
finish:
 if(!s.error||s.error==6)*cpu=s.cpu;
 return s.error;
}
int biwn_deck_task_call(struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,
 biwn_world_cpu_service service,void *opaque,uint32_t helper_budget,uint32_t poll_budget) {
 struct biwn_task_cpu state;uint32_t ret;int status;
 if(!cpu)return 1;state=*cpu;
 status=biwn_deck_task_resume(bus,&state,service,opaque,helper_budget,poll_budget);
 if(status){if(status==6)*cpu=state;return status;}
 if(bus->read32(bus->context,state.registers[15]&0xffffffu,&ret))return 2;
 state.pc=ret;state.registers[15]+=4;
 if(state.sr&0x2000u)state.ssp=state.registers[15];else state.usp=state.registers[15];
 *cpu=state;return 0;
}
