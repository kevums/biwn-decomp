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

/* Local Repair body with one coordinator SR-mask correction below. */
static void native_scene_reset_context(struct biwn_deck_context *s)
{
    if (s->error)
        return;

    deeper_write(s, 0x47b88, 2, 0x4000);
    native_reset_clr(s, 0x47b8a, 2);
    native_reset_clr(s, 0x47b8c, 2);
    native_reset_clr(s, 0x47b8e, 2);
    deeper_write(s, 0x47b90, 2, 0x4000);
    native_reset_clr(s, 0x47b92, 2);
    native_reset_clr(s, 0x47b94, 2);
    native_reset_clr(s, 0x47b96, 2);
    deeper_write(s, 0x47b98, 2, 0x4000);
    native_reset_clr(s, 0x47b9a, 2);
    native_reset_clr(s, 0x47b9c, 2);
    native_reset_clr(s, 0x47b9e, 2);
    native_reset_clr(s, 0x47bda, 2);
    native_reset_clr(s, 0x47bdc, 2);
    native_reset_clr(s, 0x47bde, 2);

    uint32_t a0 = deeper_read(s, 0x400e6, 4);
    s->cpu.registers[8] = a0;

    deeper_write(s, 0x400ec, 4, deeper_read(s, a0 + 4, 4));
    deeper_write(s, 0x400f0, 4, deeper_read(s, a0 + 8, 4));
    deeper_write(s, 0x400f4, 4, deeper_read(s, a0 + 0xc, 4));

    native_reset_clr(s, 0x40100, 4);
    native_reset_clr(s, 0x400fc, 4);
    native_reset_clr(s, 0x400f8, 4);
    native_reset_clr(s, 0x40104, 4);
    native_reset_clr(s, 0x40406, 4);
    native_reset_clr(s, 0x4040a, 4);
    native_reset_clr(s, 0x40402, 4);

    s->cpu.sr = (s->cpu.sr & 0xFFF0) | 0x0004;
    s->cpu.pc = 0x110d2;
}
