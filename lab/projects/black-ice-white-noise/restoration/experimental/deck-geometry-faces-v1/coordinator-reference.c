/* Structured recovery: emit one geometry record per descriptor face.
 * Source offsets describe six face-centroid layouts,not guest instructions.
 */
#include "faces-contract.h"
static void faces_move_word(struct biwn_deck_context *s,unsigned n,uint32_t v){s->cpu.registers[n]=(s->cpu.registers[n]&0xffff0000u)|(v&65535u);deck_nz(s,v,16);}
static void faces_clr_word(struct biwn_deck_context *s,uint32_t a){(void)deck_read(s,a,2);deck_write(s,a,2,0);deck_nz(s,0,16);}
static void faces_push_long(struct biwn_deck_context *s,uint32_t v){deck_push(s,v);deck_nz(s,v,32);}
static uint32_t faces_asr_one(struct biwn_deck_context *s,uint32_t v){uint32_t out=(v>>1)|(v&0x80000000u);deck_nz(s,out,32);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|((v&1u)?0x11u:0u));return out;}
static void faces_centroid(struct biwn_deck_context *s,unsigned plane){
 static const uint8_t sources[6][3][2]={
  {{4,16},{8,20},{24,0}},{{4,0},{8,20},{12,24}},
  {{4,16},{8,20},{12,0}},{{16,0},{8,20},{12,24}},
  {{4,16},{8,0},{12,24}},{{4,16},{20,0},{12,24}}};
 uint32_t *r=s->cpu.registers,v;
 for(unsigned axis=0;axis<3;axis++){
  unsigned dest=6-axis,lo=sources[plane][axis][0],hi=sources[plane][axis][1];
  if(hi){r[0]=deck_read(s,r[8]+lo,4);deck_nz(s,r[0],32);r[0]=deck_alu(s,r[0],deck_read(s,r[8]+hi,4),0,0);r[0]=faces_asr_one(s,r[0]);r[dest]=r[0];deck_nz(s,r[dest],32);}
  else {r[dest]=deck_read(s,r[8]+lo,4);deck_nz(s,r[dest],32);}
  r[dest]=deck_alu(s,r[dest],deck_read(s,0x3d6cau+plane*12u+axis*4u,4),0,0);
 }
 for(unsigned n=0;n<3;n++){v=deck_read(s,0x3d712u+plane*12u+n*4u,4);r[3-n]=v;deck_nz(s,v,32);}
}
void biwn_geometry_faces_body(struct biwn_deck_context *s,uint32_t iteration_budget){
 static const unsigned saved[9]={2,3,4,5,6,7,10,11,12};uint32_t *r=s->cpu.registers,v;
 for(unsigned n=9;n>0;n--)deck_push(s,r[saved[n-1]]);
 r[12]=0;r[9]=deck_read(s,0x400e6,4);faces_move_word(s,7,deck_read(s,r[9]+0x88,2));scene_alu16(s,r[7],r[12],1,1);
 if((s->cpu.sr&5u)==0){
  r[10]=0x47b88;r[11]=0;
  do{
   if(s->error)return;if(!iteration_budget){s->error=4;return;}iteration_budget--;
   v=deck_alu(s,deck_read(s,0x49b88,4),1,0,0);deck_write(s,0x49b88,4,v);r[0]=deck_read(s,0x49b88,4);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],6,1);
   for(unsigned off=0;off<=16;off+=2){if(off==0||off==8||off==16){deck_write(s,r[10]+r[0]+off,2,0x4000);deck_nz(s,0x4000,16);}else faces_clr_word(s,r[10]+r[0]+off);}
   r[7]=r[11];deck_nz(s,r[7],32);faces_move_word(s,7,deck_read(s,r[9],2));r[11]=r[7];r[0]=r[11];deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],5,1);r[8]=r[0]+0x400c4;
   r[1]=0;deck_nz(s,0,32);r[3]=0;deck_nz(s,0,32);r[2]=0;deck_nz(s,0,32);
   faces_move_word(s,0,r[12]);r[0]=(uint32_t)((int32_t)deck_sx16(r[0])*20);deck_nz(s,r[0],32);faces_move_word(s,0,deck_read(s,r[9]+r[0]+0x10,2));scene_alu16(s,r[0],5,1,1);
   if((s->cpu.sr&5u)!=0){unsigned plane=r[0]&65535u;r[0]&=65535u;deck_nz(s,r[0],32);r[0]=deck_alu(s,r[0],r[0],0,0);faces_move_word(s,0,deck_read(s,0x114c0+r[0],2));faces_centroid(s,plane);}
   r[0]=deck_read(s,0x49b88,4);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],6,1);
   for(unsigned off=0x12;off<=0x16;off+=2)faces_clr_word(s,r[10]+r[0]+off);
   r[15]-=2;deck_bank(s);faces_clr_word(s,r[15]);faces_push_long(s,r[3]);faces_push_long(s,r[2]);faces_push_long(s,r[1]);deck_push(s,r[10]+r[0]);deck_call(s,0xe26c,0x11684);if(s->error)return;
   r[1]=deck_read(s,0x49b88,4);deck_nz(s,r[1],32);r[1]=scene_shift(s,r[1],6,1);
   for(unsigned n=0;n<12;n++){v=deck_read(s,0x3d75a+n*2u,2);deck_write(s,r[10]+r[1]+0x24+n*2u,2,v);deck_nz(s,v,16);}
   for(unsigned n=0;n<3;n++){faces_move_word(s,7,r[6-n]);v=scene_alu16(s,r[7],deck_read(s,0x49b8c+n*2u,2),1,0);faces_move_word(s,7,v);deck_write(s,r[10]+r[1]+0x12+n*2u,2,r[7]);deck_nz(s,r[7],16);}
   deck_write(s,r[10]+r[1]+0x20,2,7);deck_nz(s,7,16);r[9]=deck_read(s,0x400e6,4);
   faces_move_word(s,0,r[12]);r[0]=(uint32_t)((int32_t)deck_sx16(r[0])*20);deck_nz(s,r[0],32);faces_move_word(s,0,deck_read(s,r[9]+r[0]+0x14,2));r[0]&=65535u;deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],3,1);r[8]=0x3d772;
   v=deck_read(s,r[8]+r[0],4);deck_write(s,r[10]+r[1]+0x3c,4,v);deck_nz(s,v,32);
   r[0]=deck_read(s,0x49b88,4);deck_nz(s,r[0],32);r[0]=deck_alu(s,r[0],1,1,0);r[0]=scene_shift(s,r[0],6,1);v=deck_read(s,0x49b8a,2);deck_write(s,r[10]+r[0]+0x18,2,v);deck_nz(s,v,16);
   deck_adjust(s,18);r[12]++;faces_move_word(s,7,deck_read(s,r[9]+0x88,2));scene_alu16(s,r[7],r[12],1,1);
  }while((s->cpu.sr&5u)==0);
 }
 for(unsigned n=0;n<9;n++)r[saved[n]]=deck_pop(s);
 s->cpu.pc=0x11760;
}
