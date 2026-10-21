static inline int gr_next_native(struct biwn_deck_context *s)
{
    uint32_t d3 = s->cpu.registers[3];
    uint16_t sr = s->cpu.sr;
    uint16_t d3w = (uint16_t)d3;
    uint16_t new_d3w;
    uint16_t cmp_val = 39;
    uint16_t new_sr;
    int taken;

    __asm__ __volatile__ (
        "addq.w #1, %0\n\t"
        "cmpi.w %1, %0\n\t"
        "ble %2\n\t"
        "clr.b %2\n\t"
        : "=&w" (new_d3w), "=r" (taken)
        : "i" (cmp_val)
        : "cc"
    );

    /* Read physical SR to get the low 5 condition bits */
    uint16_t phys_sr;
    __asm__ __volatile__ (
        "movec sr, %0\n\t"
        : "=w" (phys_sr)
        :
        :
    );

    uint16_t cond_bits = (uint16_t)(phys_sr & 0x001F);
    new_sr = (uint16_t)((sr & 0xFFE0) | cond_bits);

    s->cpu.registers[3] = (d3 & 0xFFFF0000u) | (uint32_t)new_d3w;
    s->cpu.sr = new_sr;

    return taken;
}
