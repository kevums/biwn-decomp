/* Structured full-CPU E03A..E096, stopping before its outer RTS.
 * MOVEM saves/restores D0 without changing flags. The successful LSR.W poll
 * sets X and C; subsequent MOVEs preserve X, so the final X is one.
 * Native waits are unbounded. Portable host limits are separate behavior.
 * Already recovered reference, now integrated as readable native source.
 */
#ifndef SCENE_CLEAR_BEGIN
#define SCENE_CLEAR_BEGIN(s) ((void)(s))
#define SCENE_CLEAR_END(s) ((void)(s))
#endif
static inline void scene_clear_write(struct biwn_deck_context *s,uint32_t a,uint32_t v){
 if(s->error)return;
#ifdef SCENE_CLEAR_NATIVE_DIRECT
 volatile uint32_t *p=(volatile uint32_t *)(a&0xffffffu);
 /* Force MOVE even for zero: CLR would add an original-unrequested MMIO read. */
 __asm__ volatile("move.l %1,(%0)"::"a"(p),"d"(v):"memory","cc");
#else
 deck_write(s,a,4,v);
#endif
 deck_nz(s,v,32);
}
static inline void scene_clear_wait(struct biwn_deck_context *s){
 uint32_t v;
#ifdef SCENE_CLEAR_NATIVE_DIRECT
 __asm__ volatile("1: move.l 0xf02238,%0\n\tlsr.w #1,%0\n\tbcc.s 1b":"=&d"(v)::"memory","cc");
 s->cpu.registers[0]=v;deck_nz(s,v,16);
 s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|0x11u);
#else
 do{
  if(s->error)return;
  if(!s->budget){s->error=4;return;}s->budget--;
  v=deck_read(s,0xf02238,4);s->cpu.registers[0]=v;deck_nz(s,v,32);
  uint32_t shifted=(v&0xffff0000u)|((v&65535u)>>1);
  s->cpu.registers[0]=shifted;deck_nz(s,shifted,16);
  s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|((v&1u)?0x11u:0u));
 }while(!(s->cpu.sr&1u));
#endif
}
static void scene_clear_body(struct biwn_deck_context *s){
 uint32_t *r=s->cpu.registers,v;
 SCENE_CLEAR_BEGIN(s);
 deck_push(s,r[0]); /* MOVEM, not MOVE: no NZVC update. */
 scene_clear_wait(s);
 r[0]=deck_read(s,r[15]+12u,4);deck_nz(s,r[0],32);
 scene_clear_write(s,0xf02268,r[0]);scene_clear_write(s,0xf0226c,r[0]);
 v=deck_read(s,r[15]+8u,4);scene_clear_write(s,0xf02200,v);
 scene_clear_write(s,0xf02204,0x3e20);scene_clear_write(s,0xf0220c,0);
 scene_clear_write(s,0xf02210,0x1ff20);scene_clear_write(s,0xf0223c,0xb400e0);
 scene_clear_write(s,0xf02238,0x10200);
 r[0]=deck_pop(s); /* MOVEM leaves the last MOVE flags intact. */
 s->cpu.pc=0xe096;
 SCENE_CLEAR_END(s);
}
