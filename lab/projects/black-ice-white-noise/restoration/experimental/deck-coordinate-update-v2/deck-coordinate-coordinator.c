/* Coordinator recovery of 11D1A..11E64, kept separate from both raw local
 * predictions. Register bookkeeping retains the original helper-call ABI. */
#include "deck-coordinate-contract.h"
void biwn_deck_coordinate_body(struct biwn_deck_context *s) {
 uint32_t *r=s->cpu.registers,v;
 const unsigned saved[]={2,3,4,5,6,7,10,11,12,13,14};
 for(unsigned i=11;i>0;i--)deck_push(s,r[saved[i-1]]);

 /* Add angular deltas and wrap each stored angle to 0..255. The NOT.B
  * mask is 000000FF, retaining the original byte operation's flag effects. */
 r[0]=deck_read(s,0x400f8,4);deck_nz(s,r[0],32);
 r[0]=deck_alu(s,r[0],deck_read(s,0x40402,4),0,0);
 r[1]=0;deck_nz(s,0,32);r[1]=255;deck_nz(s,255,8);
 r[0]&=r[1];deck_nz(s,r[0],32);
 deck_write(s,0x400f8,4,r[0]);deck_nz(s,r[0],32);
 r[0]=deck_read(s,0x400fc,4);deck_nz(s,r[0],32);
 r[0]=deck_alu(s,r[0],deck_read(s,0x4040a,4),0,0);
 r[0]&=r[1];deck_nz(s,r[0],32);
 deck_write(s,0x400fc,4,r[0]);deck_nz(s,r[0],32);
 r[0]=deck_read(s,0x40100,4);deck_nz(s,r[0],32);
 r[0]=deck_alu(s,r[0],deck_read(s,0x40406,4),0,0);
 r[0]&=r[1];deck_nz(s,r[0],32);
 deck_write(s,0x40100,4,r[0]);deck_nz(s,r[0],32);

 /* Transform the delta through the resident GPU. These five arguments
  * remain on the original stack during the following three products. */
 v=deck_read(s,0x40104,4);deck_push(s,v);deck_nz(s,v,32);
 v=deck_read(s,0x40406,4);deck_push(s,v);deck_nz(s,v,32);
 v=deck_read(s,0x4040a,4);deck_push(s,v);deck_nz(s,v,32);
 v=deck_read(s,0x40402,4);deck_push(s,v);deck_nz(s,v,32);
 deck_push(s,0x47b88);deck_call(s,0xe26c,0x11d82);
 deck_write(s,0x40406,4,0);deck_nz(s,0,32);
 deck_write(s,0x4040a,4,0);deck_nz(s,0,32);
 deck_write(s,0x40402,4,0);deck_nz(s,0,32);
 r[10]=0x47b9a;r[11]=deck_sx16(deck_read(s,r[10],2));
 r[12]=deck_sx16(deck_read(s,0x47b9c,2));
 r[8]=0x47b9e;r[13]=deck_sx16(deck_read(s,r[8],2));
 deck_write(s,r[10],2,0);deck_nz(s,0,16);
 deck_write(s,0x47b9c,2,0);deck_nz(s,0,16);
 deck_write(s,r[8],2,0);deck_nz(s,0,16);

 /* Proposed position and displacement from the selected record's center.
  * Address-register additions below deliberately leave CCR unchanged. */
 r[7]=0x400ec;deck_nz(s,r[7],32);
 r[5]=r[11];deck_nz(s,r[5],32);r[9]=r[7];
 r[5]=deck_alu(s,r[5],deck_read(s,r[9],4),0,0);
 r[11]=deck_read(s,0x400e6,4);
 r[0]=r[5];deck_nz(s,r[0],32);
 r[0]=deck_alu(s,r[0],deck_read(s,r[11]+4,4),1,0);
 r[6]=0x400f0;deck_nz(s,r[6],32);r[9]=r[6];
 r[12]+=deck_read(s,r[9],4);
 r[3]=r[12];deck_nz(s,r[3],32);
 r[3]=deck_alu(s,r[3],deck_read(s,r[11]+8,4),1,0);
 r[14]=0x400f4;r[13]+=deck_read(s,r[14],4);
 r[4]=r[13];deck_nz(s,r[4],32);
 r[4]=deck_alu(s,r[4],deck_read(s,r[11]+12,4),1,0);
 r[10]=0xe540;

 /* Sum three low-32-bit squares using the original multiplication service.
  * Retain each original argument pair, JSR return and stack reclamation. */
 deck_push(s,r[0]);deck_nz(s,r[0],32);
 deck_push(s,r[0]);deck_nz(s,r[0],32);
 deck_call(s,r[10],0x11df6);deck_adjust(s,8);
 r[2]=r[0];deck_nz(s,r[2],32);
 deck_push(s,r[3]);deck_nz(s,r[3],32);
 deck_push(s,r[3]);deck_nz(s,r[3],32);
 deck_call(s,r[10],0x11e00);deck_adjust(s,8);
 r[2]=deck_alu(s,r[2],r[0],0,0);
 deck_push(s,r[4]);deck_nz(s,r[4],32);
 deck_push(s,r[4]);deck_nz(s,r[4],32);
 deck_call(s,r[10],0x11e0a);deck_adjust(s,8);
 r[2]=deck_alu(s,r[2],r[0],0,0);
 r[0]=0;deck_nz(s,0,32);
 r[0]=deck_read(s,r[11],2);deck_nz(s,r[0],16);
 r[0]=deck_asl5(s,r[0]);r[8]=0x400c4;deck_adjust(s,20);
 v=deck_read(s,r[8]+0x1c+r[0],4);(void)deck_alu(s,r[2],v,1,1);
 if(s->cpu.sr&1u){
  r[9]=r[7];deck_write(s,r[9],4,r[5]);deck_nz(s,r[5],32);
  r[9]=r[6];deck_write(s,r[9],4,r[12]);deck_nz(s,r[12],32);
  deck_write(s,r[14],4,r[13]);deck_nz(s,r[13],32);
 }

 /* Publish signed word offsets whether or not the proposed move succeeded. */
 r[9]=deck_sx16(deck_read(s,0x400ee,2));
 r[9]-=deck_sx16(deck_read(s,r[11]+6,2));
 deck_write(s,0x49b8c,2,r[9]);deck_nz(s,r[9],16);
 r[9]=deck_sx16(deck_read(s,0x400f2,2));
 r[9]-=deck_sx16(deck_read(s,r[11]+10,2));
 deck_write(s,0x49b8e,2,r[9]);deck_nz(s,r[9],16);
 r[9]=deck_sx16(deck_read(s,0x400f6,2));
 r[9]-=deck_sx16(deck_read(s,r[11]+14,2));
 deck_write(s,0x49b90,2,r[9]);deck_nz(s,r[9],16);
 for(unsigned i=0;i<11;i++)r[saved[i]]=deck_pop(s);
 s->cpu.pc=0x11e62;
}
