/* Coordinator recovered complete 1102A..110D2 body, successful direct RAM.
 * Original CLR memory read-before-write widths and order are preserved.
 * The service caller consumes its outer RTS; no original-code call/decoder.
 */
static inline void native_reset_clr(struct biwn_deck_context *s,uint32_t a,unsigned w){
 volatile void *ptr=(volatile void *)(a&0xffffffu);
 if(s->error)return;
 /* One physical CLR supplies the original dummy read and zero write.
  * A separate volatile read plus compiler CLR would read twice on68000. */
 if(w==2)__asm__ volatile("clr.w (%0)"::"a"(ptr):"memory","cc");
 else __asm__ volatile("clr.l (%0)"::"a"(ptr):"memory","cc");
}
__attribute__((noinline,used))
static void native_scene_reset_context(struct biwn_deck_context *s){
 uint32_t base,value;unsigned i;
 if(s->error)return;
 for(i=0;i<3;i++){
  uint32_t a=0x47b88u+8u*i;
  deeper_write(s,a,2,0x4000u);
  native_reset_clr(s,a+2u,2);
  native_reset_clr(s,a+4u,2);
  native_reset_clr(s,a+6u,2);
 }
 native_reset_clr(s,0x47bdau,2);
 native_reset_clr(s,0x47bdcu,2);
 native_reset_clr(s,0x47bdeu,2);
 base=deeper_read(s,0x400e6u,4);s->cpu.registers[8]=base;
 for(i=0;i<3;i++){
  value=deeper_read(s,base+4u+4u*i,4);
  deeper_write(s,0x400ecu+4u*i,4,value);
 }
 native_reset_clr(s,0x40100u,4);
 native_reset_clr(s,0x400fcu,4);
 native_reset_clr(s,0x400f8u,4);
 native_reset_clr(s,0x40104u,4);
 native_reset_clr(s,0x40406u,4);
 native_reset_clr(s,0x4040au,4);
 native_reset_clr(s,0x40402u,4);
 s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|4u);s->cpu.pc=0x110d2u;
}
