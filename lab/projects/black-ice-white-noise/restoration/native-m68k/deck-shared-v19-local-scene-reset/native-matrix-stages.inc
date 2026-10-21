/* Coordinator native factoring at original110D4call. Qualified source SHA256:8072d70470f078900117b5c555f3f5ba95ef72a511b257d848d4a60f0d8e1b6c
 * Exact pre/post statements retained; C frames return before the real helper call. */
__attribute__((noinline)) static void native_matrix_before(struct biwn_deck_context *s){
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

}
__attribute__((noinline)) static void native_matrix_after(struct biwn_deck_context *s){
 uint32_t *r=s->cpu.registers,v;
 r[0]=deck_read(s,0x49b88,4);deck_nz(s,r[0],32);r[0]=scene_shift(s,r[0],6,1);
 deck_write(s,r[10]+r[0]+32,2,7);deck_nz(s,7,16);
 v=deck_read(s,0x400c4,4);deck_write(s,r[10]+r[0]+60,4,v);deck_nz(s,v,32);
 r[0]=deck_read(s,0x49b88,4);deck_nz(s,r[0],32);r[0]=deck_alu(s,r[0],1,1,0);r[0]=scene_shift(s,r[0],6,1);
 v=deck_read(s,0x49b8a,2);deck_write(s,r[10]+r[0]+24,2,v);deck_nz(s,v,16);
 deck_adjust(s,10);r[10]=deck_pop(s);s->cpu.pc=0x1142c;

}
