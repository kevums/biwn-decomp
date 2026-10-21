/* Readable full-CPU entry 17E0E, stopping before outer RTS at17F12.
 * Coordinator reconstruction from the original listing and existing logical C.
 * Mode and completion values are reread at their original access sites.
 */
static void scene17_body(struct biwn_deck_context *s){
 uint32_t *r=s->cpu.registers,v;
 deck_push(s,r[10]);deck_nz(s,r[10],32);
 deck_push(s,r[2]);deck_nz(s,r[2],32);
 r[10]=0x49c60;
 v=deck_read(s,r[10],2);deck_nz(s,v,16);
 if(v){
  scene17_clr_push(s);
  v=deck_read(s,0xbd83c,4);deck_push(s,v);deck_nz(s,v,32);
  deck_call(s,0xe03a,0x17e2c);
  scene17_clr(s,0x49b88);deck_adjust(s,8);
  v=deck_read(s,r[10],2);(void)scene_alu16(s,v,1,1,1);
  if(s->cpu.sr&4u){
   deck_call(s,0xe0a6,0x17e40);deck_call(s,0x170a0,0x17e46);
   v=deck_read(s,0x49b88,4);deck_nz(s,v,32);
   if(v)scene17_completion(s,0x17e56,0x17e5c,0x17e6a);
  }else{
   v=deck_read(s,r[10],2);(void)scene_alu16(s,v,2,1,1);
   if(s->cpu.sr&4u){
    r[9]=deck_sx16(deck_read(s,0x49c76,2));
    deck_write(s,0x49c1c,4,r[9]);deck_nz(s,r[9],32);
    deck_call(s,0xe0f2,0x17e88);
    r[2]&=0xffff0000u;deck_nz(s,0,16);r[8]=0x10d688;
    v=deck_read(s,r[8],4);(void)deck_alu(s,v,0xffffu,1,1);
    if(!(s->cpu.sr&4u)){
     r[10]=r[8];
     for(;;){
      if(!scene17_work(s))return;
      r[0]=(r[0]&0xffff0000u)|(r[2]&65535u);deck_nz(s,r[0],16);
      v=scene_alu16(s,r[0],1,0,0);r[0]=(r[0]&0xffff0000u)|v;
      r[0]=deck_sx16(r[0]);deck_nz(s,r[0],32);
      r[0]=scene_shift(s,r[0],2,1);
      v=deck_read(s,r[10]+r[0],4);deck_nz(s,v,32);
      if(!v)break;
      r[0]=(r[0]&0xffff0000u)|(r[2]&65535u);deck_nz(s,r[0],16);
      r[0]=deck_sx16(r[0]);deck_nz(s,r[0],32);
      r[0]=scene_shift(s,r[0],2,1);
      v=deck_read(s,r[10]+r[0],4);deck_write(s,0x49c1c,4,v);deck_nz(s,v,32);
      deck_call(s,0xe148,0x17ebc);deck_call(s,0x170a0,0x17ec2);
      v=deck_read(s,0x49b88,4);deck_nz(s,v,32);
      if(v)scene17_completion(s,0x17ed0,0x17ed6,0x17ee4);
      v=scene_alu16(s,r[2],2,0,0);r[2]=(r[2]&0xffff0000u)|v;
      r[0]=(r[0]&0xffff0000u)|(r[2]&65535u);deck_nz(s,r[0],16);
      r[0]=deck_sx16(r[0]);deck_nz(s,r[0],32);
      r[0]=scene_shift(s,r[0],2,1);
      v=deck_read(s,r[10]+r[0],4);(void)deck_alu(s,v,0xffffu,1,1);
      if(s->cpu.sr&4u)break;
     }
    }
   }else{
    v=deck_read(s,0x49c60,2);(void)scene_alu16(s,v,3,1,1);
    if(s->cpu.sr&4u)scene17_clr(s,0x49b88);
   }
  }
  deck_call(s,0x17f14,0x17f0e);
 }
 r[2]=deck_pop(s);deck_nz(s,r[2],32);
 r[10]=deck_pop(s); /* MOVEA preserves flags from the D2 restore. */
 s->cpu.pc=0x17f12;
}
