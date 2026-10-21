/* Structured recovery: six plane layouts emit four three-word coordinates.
 * Each source word is reloaded at its original position, including aliases.
 * Table entries describe coordinate fields and scale, not guest instructions.
 */
#include "plane-contract.h"
static uint32_t plane_asl_word3(struct biwn_deck_context *s,uint32_t value){
 uint32_t v=value&65535u;unsigned carry=0,overflow=0;
 for(unsigned n=0;n<3;n++){uint32_t old=v;carry=v>>15;v=(v<<1)&65535u;overflow|=((old^v)>>15)&1u;}
 deck_nz(s,v,16);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|(carry?0x11u:0u)|(overflow?2u:0u));
 return (value&0xffff0000u)|v;
}
void biwn_plane_layout_body(struct biwn_deck_context *s){
 /* Top bit marks a field scaled by8 through D0.W. Other fields are direct
  * memory-to-memory MOVE.W and must leave D0 unchanged. */
 static const uint8_t fields[6][12]={
  {0x92,0x8a,0x1a, 0x92,0x96,0x1a, 0x86,0x96,0x1a, 0x86,0x8a,0x1a},
  {0x06,0x8a,0x8e, 0x06,0x8a,0x9a, 0x06,0x96,0x9a, 0x06,0x96,0x8e},
  {0x92,0x8a,0x0e, 0x86,0x8a,0x0e, 0x86,0x96,0x0e, 0x92,0x96,0x0e},
  {0x12,0x8a,0x9a, 0x12,0x8a,0x8e, 0x12,0x96,0x8e, 0x12,0x96,0x9a},
  {0x92,0x16,0x9a, 0x92,0x16,0x8e, 0x86,0x16,0x8e, 0x86,0x16,0x9a},
  {0x92,0x0a,0x9a, 0x86,0x0a,0x9a, 0x86,0x0a,0x8e, 0x92,0x0a,0x9a}
 };
 static const uint32_t end[6]={0x11178,0x111e2,0x1124c,0x111e2,0x111e2,0x11382};
 uint32_t *r=s->cpu.registers,v,selector;
 r[8]=deck_read(s,r[15]+4,4);r[9]=deck_read(s,r[15]+8,4);
 v=deck_read(s,r[15]+12,2);r[1]=(r[1]&0xffff0000u)|v;deck_nz(s,v,16);
 r[0]=0;deck_nz(s,0,32);v=deck_read(s,r[8],2);r[0]=v;deck_nz(s,v,16);
 r[0]=scene_shift(s,r[0],5,1);r[8]=r[0]+0x400c4u;
 selector=r[1]&65535u;scene_alu16(s,selector,5,1,1);
 if(selector>5){s->cpu.pc=0x11382;return;}
 r[0]=0;deck_nz(s,0,32);r[0]=selector;deck_nz(s,selector,16);
 r[0]=deck_alu(s,r[0],r[0],0,0);v=deck_read(s,0x11104+r[0],2);r[0]=(r[0]&0xffff0000u)|v;deck_nz(s,v,16);
 for(unsigned n=0;n<12;n++){
  unsigned field=fields[selector][n];v=deck_read(s,r[8]+(field&127u),2);
  if(field&128u){r[0]=(r[0]&0xffff0000u)|v;deck_nz(s,v,16);r[0]=plane_asl_word3(s,r[0]);v=r[0]&65535u;}
  deck_write(s,r[9]+0x24u+n*2u,2,v);deck_nz(s,v,16);
 }
 s->cpu.pc=end[selector];
}
