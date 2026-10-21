#ifndef BIWN_NATIVE_ALU_H
#define BIWN_NATIVE_ALU_H
/* Target-only implementation of the existing software-CPU arithmetic contract.
 * Read physical flags in the same asm block as the operation, then merge only
 * its defined bits into the logical SR. Never load the physical SR from guest
 * state. All structured algorithms and guest bus accesses stay unchanged.
 * MOVE from SR is available in user mode on the Jaguar's original 68000. */
static inline void native_deck_nz(struct biwn_deck_context *s,uint32_t v,unsigned bits){
 uint16_t flags;
 if(bits==32)__asm__("tst.l %1\n\tmove.w %%sr,%0":"=d"(flags):"d"(v):"cc");
 else if(bits==16)__asm__("tst.w %1\n\tmove.w %%sr,%0":"=d"(flags):"d"(v):"cc");
 else {deck_nz(s,v,bits);return;} /* Preserve the portable helper's byte contract. */
 s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(flags&15u));
}
static inline uint32_t native_deck_alu(struct biwn_deck_context *s,uint32_t a,uint32_t b,int sub,int cmp){
 uint16_t flags;unsigned mask=cmp?15u:31u;
 if(sub)__asm__("sub.l %2,%0\n\tmove.w %%sr,%1":"+d"(a),"=d"(flags):"d"(b):"cc");
 else __asm__("add.l %2,%0\n\tmove.w %%sr,%1":"+d"(a),"=d"(flags):"d"(b):"cc");
 s->cpu.sr=(uint16_t)((s->cpu.sr&~mask)|(flags&mask));return a;
}
static inline uint32_t native_scene_alu16(struct biwn_deck_context *s,uint32_t a,uint32_t b,int sub,int cmp){
 uint16_t flags;unsigned mask=cmp?15u:31u;
 if(sub)__asm__("sub.w %2,%0\n\tmove.w %%sr,%1":"+d"(a),"=d"(flags):"d"(b):"cc");
 else __asm__("add.w %2,%0\n\tmove.w %%sr,%1":"+d"(a),"=d"(flags):"d"(b):"cc");
 s->cpu.sr=(uint16_t)((s->cpu.sr&~mask)|(flags&mask));return a&65535u;
}
static inline uint32_t native_scene_shift(struct biwn_deck_context *s,uint32_t v,unsigned count,int left){
 uint16_t flags;
 /* The portable helper clears X for zero count; hardware preserves physical
  * X. Handle this explicitly. Counts above 63 also retain portable semantics. */
 if(!count){native_deck_nz(s,v,32);s->cpu.sr&=(uint16_t)~0x13u;return v;}
 if(count>63)return scene_shift(s,v,count,left);
 if(left)__asm__("asl.l %2,%0\n\tmove.w %%sr,%1":"+d"(v),"=d"(flags):"d"(count):"cc");
 else __asm__("lsr.l %2,%0\n\tmove.w %%sr,%1":"+d"(v),"=d"(flags):"d"(count):"cc");
 s->cpu.sr=(uint16_t)((s->cpu.sr&0xffe0u)|(flags&31u));return v;
}
static inline uint32_t native_deck_asl5(struct biwn_deck_context *s,uint32_t v){return native_scene_shift(s,v,5,1);}
#endif
