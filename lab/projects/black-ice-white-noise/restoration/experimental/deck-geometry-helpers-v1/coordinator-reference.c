/* Coordinator structured recovery, kept separate from raw local output. */
#include "helper-contract.h"
static void clear_records(struct biwn_deck_context *s,biwn_deck_write8 w8,uint32_t budget) {
 uint32_t *r=s->cpu.registers;
 r[0]=(r[0]&0xffff0000u)|deck_read(s,r[15]+4,2);deck_nz(s,r[0],16);
 r[0]=deck_sx16(r[0]);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],6,1);
 r[9]=r[0];r[9]+=0x47b88;r[1]&=0xffff0000u;deck_nz(s,0,16);
 r[0]=(r[0]&0xffff0000u)|deck_read(s,r[15]+6,2);deck_nz(s,r[0],16);
 r[0]=deck_sx16(r[0]);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],6,1);
 if(!(s->cpu.sr&4u))do {
  if(s->error)return;if(!budget){s->error=4;return;}budget--;
  helper_clr8(s,w8,r[9]);r[9]++;
  r[1]=(r[1]&0xffff0000u)|scene_alu16(s,r[1],1,0,0);
  r[8]=deck_sx16(r[1]);(void)deck_alu(s,r[0],r[8],1,1);
 }while(!(s->cpu.sr&5u));
 s->cpu.pc=0x1098e;
}
static void advance_texture(struct biwn_deck_context *s) {
 uint32_t *r=s->cpu.registers,v;
 v=deck_read(s,0x403d4,2);deck_nz(s,v,16);
 if(!(s->cpu.sr&12u)){
  v=scene_alu16(s,v,1,1,0);deck_write(s,0x403d4,2,v);s->cpu.pc=0x10bb2;return;
 }
 r[8]=deck_read(s,0x400e6,4);v=deck_read(s,r[8]+0x90,2);deck_write(s,0x403d4,2,v);deck_nz(s,v,16);
 v=scene_alu16(s,deck_read(s,0x403d0,2),1,0,0);deck_write(s,0x403d0,2,v);
 r[1]=(r[1]&0xffff0000u)|deck_read(s,0x403d2,2);deck_nz(s,r[1],16);
 (void)scene_alu16(s,r[1],deck_read(s,0x403d0,2),1,1);
 if((s->cpu.sr&4u)||(((s->cpu.sr>>3)^(s->cpu.sr>>1))&1u)){
  deck_write(s,0x403d0,2,0);deck_nz(s,0,16);
 }
 r[8]=0x23f84;r[0]=(r[0]&0xffff0000u)|deck_read(s,0x403d0,2);deck_nz(s,r[0],16);
 r[0]=(r[0]&0xffff0000u)|(r[0]&1u);deck_nz(s,r[0],16);
 r[0]=(r[0]&0xffff0000u)|scene_alu16(s,r[0],1,0,0);
 r[0]=deck_sx16(r[0]);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],2,1);
 v=deck_read(s,r[8]+r[0],4);deck_write(s,r[8],4,v);deck_nz(s,v,32);
 r[0]=(r[0]&0xffff0000u)|deck_read(s,0x403d0,2);deck_nz(s,r[0],16);
 r[0]=(r[0]&0xffff0000u)|helper_asr16(s,r[0]);
 r[0]=(r[0]&0xffff0000u)|scene_alu16(s,r[0],deck_read(s,0x403da,2),0,0);
 r[0]=deck_sx16(r[0]);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],3,1);
 r[8]=0x4674c;v=deck_read(s,r[8]+r[0],4);deck_write(s,0x23f7c,4,v);deck_nz(s,v,32);s->cpu.pc=0x10c16;
}
static void setup_matrix(struct biwn_deck_context *s) {
 uint32_t *r=s->cpu.registers,v;
 deck_push(s,r[10]);deck_nz(s,r[10],32);
 v=deck_alu(s,deck_read(s,0x49b88,4),1,0,0);deck_write(s,0x49b88,4,v);
 r[0]=deck_read(s,0x49b88,4);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],6,1);r[10]=0x47b88;
 for(unsigned off=0;off<=16;off+=2){v=off==0||off==8||off==16?0x4000:0;deck_write(s,r[10]+r[0]+off,2,v);deck_nz(s,v,16);}
 for(unsigned i=0;i<3;i++){
  r[1]=(r[1]&0xffff0000u)|deck_read(s,0x49b8c+i*2,2);deck_nz(s,r[1],16);
  r[1]=(r[1]&0xffff0000u)|scene_alu16(s,0,r[1],1,0);
  deck_write(s,r[10]+r[0]+18+i*2,2,r[1]);deck_nz(s,r[1],16);
 }
 v=deck_read(s,0x403ce,2);scene_push_word(s,v);deck_nz(s,v,16);
 deck_push(s,r[10]+r[0]);v=deck_read(s,0x400e6,4);deck_push(s,v);deck_nz(s,v,32);
 deck_call(s,0x110d4,0x113fe);if(s->error)return;
 r[0]=deck_read(s,0x49b88,4);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],6,1);
 deck_write(s,r[10]+r[0]+32,2,7);deck_nz(s,7,16);
 v=deck_read(s,0x400c4,4);deck_write(s,r[10]+r[0]+60,4,v);deck_nz(s,v,32);
 r[0]=deck_read(s,0x49b88,4);deck_nz(s,r[0],32);r[0]=deck_alu(s,r[0],1,1,0);r[0]=scene_shift(s,r[0],6,1);
 v=deck_read(s,0x49b8a,2);deck_write(s,r[10]+r[0]+24,2,v);deck_nz(s,v,16);
 deck_adjust(s,10);r[10]=deck_pop(s);s->cpu.pc=0x1142c;
}
void biwn_geometry_helper_body(struct biwn_deck_context *s,biwn_deck_write8 w8,uint32_t budget) {
 switch(s->cpu.pc){case 0x10968:clear_records(s,w8,budget);break;case 0x10ba4:advance_texture(s);break;case 0x11384:setup_matrix(s);break;default:s->error=1;}
}
