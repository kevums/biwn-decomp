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

/* Unedited supplied candidate body. */
static void scene_clear_body(struct biwn_deck_context *s)
{
    if (s->error != 0) {
        return;
    }

    SCENE_CLEAR_BEGIN(s);

    uint32_t saved_d0 = s->cpu.registers[0];
    deck_push(s, saved_d0);

    scene_clear_wait(s);

    uint32_t arg_c = deck_read(s, s->cpu.registers[15] + 0xCu, 4);
    s->cpu.registers[0] = arg_c;

    scene_clear_write(s, 0xF02268u, arg_c);
    scene_clear_write(s, 0xF0226Cu, arg_c);

    uint32_t arg_8 = deck_read(s, s->cpu.registers[15] + 0x8u, 4);
    scene_clear_write(s, 0xF02200u, arg_8);

    scene_clear_write(s, 0xF02204u, 0x3E20u);
    scene_clear_write(s, 0xF0220Cu, 0x0u);
    scene_clear_write(s, 0xF02210u, 0x1FF20u);
    scene_clear_write(s, 0xF0223Cu, 0xB400E0u);
    scene_clear_write(s, 0xF02238u, 0x10200u);

    s->cpu.registers[0] = deck_pop(s);

    s->cpu.pc = 0xE096u;

    SCENE_CLEAR_END(s);
}
