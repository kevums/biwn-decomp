/* Coordinator implementation; not local-model output. */
static inline int gr_next_native(struct biwn_deck_context *s){
 uint32_t index=s->cpu.registers[3];uint16_t flags;uint8_t take;
 __asm__ volatile("addq.w #1,%0\n\tcmpi.w #39,%0\n\tmove.w %%sr,%1\n\tsle %2"
  : "+d"(index),"=d"(flags),"=d"(take)::"cc");
 s->cpu.registers[3]=index;s->cpu.sr=(uint16_t)((s->cpu.sr&0xffe0u)|(flags&31u));
 return take!=0;
}
