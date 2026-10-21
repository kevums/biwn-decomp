/* Structured recovery of the debug panel caller. The row table describes
 * eight display fields; it is not an instruction decoder or interpreter. */
#include "debug-contract.h"
static void debug_move_long_push(struct biwn_deck_context *s,uint32_t v){deck_push(s,v);deck_nz(s,v,32);}
static void debug_push_word(struct biwn_deck_context *s,uint32_t v,int clear){
 s->cpu.registers[15]-=2;deck_bank(s);
 if(clear)(void)deck_read(s,s->cpu.registers[15],2);
 deck_write(s,s->cpu.registers[15],2,v);deck_nz(s,v,16);
}
void biwn_debug_overlay_body(struct biwn_deck_context *s){
 static const uint32_t mmio[7][2]={{0xf02268,0},{0xf0226c,0},{0xf02200,0xb29d0},{0xf02204,0x1820},{0xf0220c,0},{0xf0223c,0x113b0},{0xf02238,0x10200}};
 static const struct {uint32_t source,format,formatter_return,text_return;uint16_t x,y;} rows[8]={
  {0x400ec,0x106e0,0x107aa,0x107d2,0x14,2},
  {0x400f0,0x106eb,0x107e6,0x10808,0x14,0x0c},
  {0x400f4,0x106f6,0x1081c,0x1083e,0x14,0x16},
  {0x400fc,0x10701,0x10852,0x10874,0x78,2},
  {0x400f8,0x1070c,0x10888,0x108aa,0x78,0x0c},
  {0x40100,0x10717,0x108be,0x108e0,0x78,0x16},
  {0x403d0,0x10722,0x108f6,0x10918,0x14,0x20},
  {0x403ca,0x10730,0x10938,0x1095a,0x14,0x2a}};
 uint32_t *r=s->cpu.registers,v;
 deck_adjust(s,0xffffffc8u);
 deck_push(s,r[12]);deck_push(s,r[11]);deck_push(s,r[10]);
 r[8]=0xf02268;r[1]=0;deck_nz(s,0,32);
 for(unsigned n=0;n<7;n++){
  r[8]=mmio[n][0];deck_write(s,r[8],4,mmio[n][1]);deck_nz(s,mmio[n][1],32);
 }
 v=deck_read(s,0x403cc,2);deck_nz(s,v,16);
 if(!(s->cpu.sr&4u)){
  for(unsigned row=0;row<8;row++){
   if(s->error)return;
   if(row<6){
    v=deck_read(s,rows[row].source,4);
    if(row==0)debug_move_long_push(s,v);
    else{deck_write(s,r[15],4,v);deck_nz(s,v,32);}
   }else if(row==6){
    r[9]=deck_sx16(deck_read(s,rows[row].source,2));debug_move_long_push(s,r[9]);
   }else{
    v=deck_read(s,rows[row].source,2);r[0]=(r[0]&0xffff0000u)|v;deck_nz(s,v,16);
    r[0]=(r[0]&65535u)*24u;deck_nz(s,r[0],32);
    r[0]=deck_alu(s,r[0],0x3fb0c,0,0);debug_move_long_push(s,r[0]);
   }
   deck_push(s,rows[row].format);
   if(row==0)r[10]=r[15]+22u;
   debug_move_long_push(s,r[10]);
   if(row==0)r[12]=0x1b45a;
   deck_call(s,r[12],rows[row].formatter_return);if(s->error)return;
   debug_push_word(s,0,1);debug_push_word(s,3,0);
   deck_push(s,0x4c3e0);deck_push(s,0x3e08);deck_push(s,0xb29d0);
   debug_move_long_push(s,r[10]);debug_push_word(s,rows[row].y,0);debug_push_word(s,rows[row].x,0);
   if(row==0)r[11]=0x149ae;
   deck_call(s,r[11],rows[row].text_return);if(s->error)return;
   deck_adjust(s,row<5?32u:36u);
  }
 }
 r[10]=deck_pop(s);r[11]=deck_pop(s);r[12]=deck_pop(s);deck_adjust(s,56);s->cpu.pc=0x10966;
}
