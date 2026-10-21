static void clear_records(struct biwn_deck_context *s, biwn_deck_write8 w8, uint32_t budget)
{
    /* 0x10968: move.w $4(a7), d0 */
    uint32_t a7 = s->cpu.registers[15];
    uint32_t val = deck_read(s, a7 + 4, 2);
    if (s->error) {
        s->cpu.pc = 0x1098e;
        return;
    }
    deck_cpu_move_w_d(s, 0, val);

    /* 0x1096c: ext.l d0 */
    deck_cpu_ext_l_d(s, 0);

    /* 0x1096e: asl.l #$6, d0 */
    deck_cpu_asl6_l_d(s, 0);

    /* 0x10970: movea.l d0, a1 */
    deck_cpu_move_l_d_a(s, 0, 1);

    /* 0x10972: adda.l #$47b88, a1 */
    deck_cpu_adda_l(s, 1, 0x47b88);

    /* 0x10978: clr.w d1 */
    deck_cpu_clr_w_d(s, 1);

    /* 0x1097a: move.w $6(a7), d0 */
    val = deck_read(s, a7 + 6, 2);
    if (s->error) {
        s->cpu.pc = 0x1098e;
        return;
    }
    deck_cpu_move_w_d(s, 0, val);

    /* 0x1097e: ext.l d0 */
    deck_cpu_ext_l_d(s, 0);

    /* 0x10980: asl.l #$6, d0 */
    deck_cpu_asl6_l_d(s, 0);

    /* 0x10982: beq.b $1098e */
    if ((s->cpu.sr & 4u) != 0) {
        s->cpu.pc = 0x1098e;
        return;
    }

    /* Loop: 0x10984..0x1098c */
    for (;;) {
        /* Check error before each CLR byte loop iteration */
        if (s->error) {
            s->cpu.pc = 0x1098e;
            return;
        }

        /* Budget check before each byte operation */
        if (budget == 0) {
            s->error = 4;
            s->cpu.pc = 0x1098e;
            return;
        }
        budget--;

        /* 0x10984: clr.b (a1)+ */
        uint32_t a1 = s->cpu.registers[9];
        helper_clr8(s, w8, a1);
        if (s->error) {
            s->cpu.pc = 0x1098e;
            return;
        }
        deck_cpu_adda_l(s, 1, 1);

        /* 0x10986: addq.w #$1, d1 */
        deck_cpu_addq1_w_d(s, 1);

        /* 0x10988: movea.w d1, a0 */
        deck_cpu_movea_w_d_a(s, 1, 0);

        /* 0x1098a: cmp.l a0, d0 */
        deck_cpu_cmp_l_a_d(s, 0, 0);

        /* 0x1098c: bhi.b $10984 */
        if (!deck_cpu_bhi(s)) {
            break;
        }
    }

    /* Set final logical PC to the RTS address */
    s->cpu.pc = 0x1098e;
}
