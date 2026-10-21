/* Parent geometry arithmetic frames end before any nested service. */
__attribute__((noinline)) static void native_geometry_begin(struct biwn_deck_context *s){
 uint32_t *r=s->cpu.registers;
 deck_push(s,r[3]);deck_nz(s,r[3],32);
 deck_push(s,r[2]);deck_nz(s,r[2],32);
 scene_push_word(s,7);deck_nz(s,7,16);scene_push_word(s,1);deck_nz(s,1,16);
}
__attribute__((noinline)) static void native_geometry_angles(struct biwn_deck_context *s){
 uint32_t *r=s->cpu.registers,v;
 deck_write(s,0x49b88,4,0);deck_nz(s,0,32);
 r[1]=32;deck_nz(s,r[1],32);
 r[1]=deck_alu(s,r[1],deck_read(s,0x40100,4),0,0);
 r[3]=0;deck_nz(s,0,32);r[3]=255;deck_nz(s,255,8);
 r[1]&=r[3];deck_nz(s,r[1],32);
 r[2]=32;deck_nz(s,r[2],32);
 r[2]=deck_alu(s,r[2],deck_read(s,0x400f8,4),0,0);
 r[2]&=r[3];deck_nz(s,r[2],32);
 r[0]=32;deck_nz(s,r[0],32);
 r[0]=deck_alu(s,r[0],deck_read(s,0x400fc,4),0,0);
 r[0]&=r[3];deck_nz(s,r[0],32);
 /* Round wrapped 8-bit angles to four sectors, then select the original
  * orientation word using strides 32,8,2 in the 64-entry lookup table. */
 r[1]=scene_shift(s,r[1],6,0);r[1]=scene_shift(s,r[1],5,1);
 r[0]=scene_shift(s,r[0],6,0);r[0]=scene_shift(s,r[0],3,1);
 r[1]=deck_alu(s,r[1],0x3d7a2,0,0);
 r[2]=scene_shift(s,r[2],6,0);r[2]=deck_alu(s,r[2],r[2],0,0);
 r[8]=r[0];r[8]+=r[1];
 v=deck_read(s,r[8]+r[2],2);deck_write(s,0x403ce,2,v);deck_nz(s,v,16);
}
__attribute__((noinline)) static void native_geometry_end(struct biwn_deck_context *s){
 uint32_t *r=s->cpu.registers;
 deck_adjust(s,4);
 r[2]=deck_pop(s);deck_nz(s,r[2],32);
 r[3]=deck_pop(s);deck_nz(s,r[3],32);s->cpu.pc=0x11b4a;
}
