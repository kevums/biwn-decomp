/* Local V6 sole repair, with ten coordinator-added MOVE.L stack flag updates. */
#include "deck-coordinate-contract.h"

void biwn_deck_coordinate_body(struct biwn_deck_context *s)
{
    uint32_t *r = s->cpu.registers;
    uint32_t pushed;

    /* Save D2-D7, A2-A6 to the private stack. */
    deck_push(s, r[14]);
    deck_push(s, r[13]);
    deck_push(s, r[12]);
    deck_push(s, r[11]);
    deck_push(s, r[10]);
    deck_push(s, r[7]);
    deck_push(s, r[6]);
    deck_push(s, r[5]);
    deck_push(s, r[4]);
    deck_push(s, r[3]);
    deck_push(s, r[2]);

    /* Load and mask the three coordinate slots. */
    r[0] = deck_read(s, 0x400f8, 4);
    deck_nz(s, r[0], 32);
    r[0] = deck_alu(s, r[0], deck_read(s, 0x40402, 4), 0, 0);

    r[1] = 0;
    deck_nz(s, r[1], 32);
    r[1] = (r[1] & 0xffffff00u) | (~r[1] & 0xffu);
    deck_nz(s, r[1], 32);
    r[0] = r[0] & r[1];
    deck_nz(s, r[0], 32);
    deck_write(s, 0x400f8, 4, r[0]);

    r[0] = deck_read(s, 0x400fc, 4);
    deck_nz(s, r[0], 32);
    r[0] = deck_alu(s, r[0], deck_read(s, 0x4040a, 4), 0, 0);
    r[0] = r[0] & r[1];
    deck_nz(s, r[0], 32);
    deck_write(s, 0x400fc, 4, r[0]);

    r[0] = deck_read(s, 0x40100, 4);
    deck_nz(s, r[0], 32);
    r[0] = deck_alu(s, r[0], deck_read(s, 0x40406, 4), 0, 0);
    r[0] = r[0] & r[1];
    deck_nz(s, r[0], 32);
    deck_write(s, 0x40100, 4, r[0]);

    /* Push GPU argument slots. */
    pushed = deck_read(s, 0x40104, 4);
    deck_push(s, pushed);
    deck_nz(s, pushed, 32);
    pushed = deck_read(s, 0x40406, 4);
    deck_push(s, pushed);
    deck_nz(s, pushed, 32);
    pushed = deck_read(s, 0x4040a, 4);
    deck_push(s, pushed);
    deck_nz(s, pushed, 32);
    pushed = deck_read(s, 0x40402, 4);
    deck_push(s, pushed);
    deck_nz(s, pushed, 32);
    deck_push(s, 0x47b88);

    /* Call E26C. */
    deck_call(s, 0xe26c, 0x11d82);
    if (s->error) return;

    /* Clear the three coordinate slots. */
    deck_write(s, 0x40406, 4, 0);
    deck_nz(s, 0, 32);
    deck_write(s, 0x4040a, 4, 0);
    deck_nz(s, 0, 32);
    deck_write(s, 0x40402, 4, 0);
    deck_nz(s, 0, 32);

    /* Load base pointers and sign-extend word offsets. */
    r[10] = 0x47b9a;
    r[11] = deck_sx16(deck_read(s, r[10], 2));
    r[12] = deck_sx16(deck_read(s, 0x47b9c, 2));
    r[8] = 0x47b9e;
    r[13] = deck_sx16(deck_read(s, r[8], 2));

    /* Clear the three word offsets. */
    deck_write(s, r[10], 2, 0);
    deck_nz(s, 0, 16);
    deck_write(s, 0x47b9c, 2, 0);
    deck_nz(s, 0, 16);
    deck_write(s, r[8], 2, 0);
    deck_nz(s, 0, 16);

    /* Compute relative coordinates. */
    r[7] = 0x400ec;
    r[5] = r[11];
    r[9] = r[7];
    r[5] = deck_alu(s, r[5], deck_read(s, r[9], 4), 0, 0);

    r[11] = deck_read(s, 0x400e6, 4);
    r[0] = r[5];
    deck_nz(s, r[0], 32);
    r[0] = deck_alu(s, r[0], deck_read(s, r[11] + 4, 4), 1, 0);

    r[6] = 0x400f0;
    r[9] = r[6];
    r[12] = r[12] + deck_read(s, r[9], 4);
    r[3] = r[12];
    deck_nz(s, r[3], 32);
    r[3] = deck_alu(s, r[3], deck_read(s, r[11] + 8, 4), 1, 0);

    r[14] = 0x400f4;
    r[13] = r[13] + deck_read(s, r[14], 4);
    r[4] = r[13];
    deck_nz(s, r[4], 32);
    r[4] = deck_alu(s, r[4], deck_read(s, r[11] + 12, 4), 1, 0);

    /* Call E540 three times to compute squared distances. */
    r[10] = 0xe540;

    deck_push(s, r[0]);
    deck_nz(s, r[0], 32);
    deck_push(s, r[0]);
    deck_nz(s, r[0], 32);
    deck_call(s, r[10], 0x11df6);
    if (s->error) return;
    deck_adjust(s, 8);
    r[2] = r[0];
    deck_nz(s, r[2], 32);

    deck_push(s, r[3]);
    deck_nz(s, r[3], 32);
    deck_push(s, r[3]);
    deck_nz(s, r[3], 32);
    deck_call(s, r[10], 0x11e00);
    if (s->error) return;
    deck_adjust(s, 8);
    r[2] = deck_alu(s, r[2], r[0], 0, 0);

    deck_push(s, r[4]);
    deck_nz(s, r[4], 32);
    deck_push(s, r[4]);
    deck_nz(s, r[4], 32);
    deck_call(s, r[10], 0x11e0a);
    if (s->error) return;
    deck_adjust(s, 8);
    r[2] = deck_alu(s, r[2], r[0], 0, 0);

    /* Reclaim the 20 bytes of GPU argument slots. */
    deck_adjust(s, 0x14);

    /* Compare squared distance against threshold. */
    r[0] = 0;
    deck_nz(s, r[0], 32);
    r[0] = (r[0] & 0xffff0000u) | deck_read(s, r[11], 2);
    deck_nz(s, r[0], 16);
    r[0] = deck_asl5(s, r[0]);
    r[8] = 0x400c4;
    deck_alu(s, r[2], deck_read(s, r[8] + 28 + r[0], 4), 1, 1);

    /* If carry is set (distance < threshold), store the new position. */
    if (s->cpu.sr & 1u) {
        r[9] = r[7];
        deck_write(s, r[9], 4, r[5]);
        deck_nz(s, r[5], 32);
        r[9] = r[6];
        deck_write(s, r[9], 4, r[12]);
        deck_nz(s, r[12], 32);
        deck_write(s, r[14], 4, r[13]);
        deck_nz(s, r[13], 32);
    }

    /* Compute and store the three relative word offsets. */
    r[9] = deck_sx16(deck_read(s, 0x400ee, 2));
    r[9] = r[9] - deck_sx16(deck_read(s, r[11] + 6, 2));
    deck_write(s, 0x49b8c, 2, r[9]);
    deck_nz(s, r[9], 16);

    r[9] = deck_sx16(deck_read(s, 0x400f2, 2));
    r[9] = r[9] - deck_sx16(deck_read(s, r[11] + 10, 2));
    deck_write(s, 0x49b8e, 2, r[9]);
    deck_nz(s, r[9], 16);

    r[9] = deck_sx16(deck_read(s, 0x400f6, 2));
    r[9] = r[9] - deck_sx16(deck_read(s, r[11] + 14, 2));
    deck_write(s, 0x49b90, 2, r[9]);
    deck_nz(s, r[9], 16);

    /* Restore D2-D7, A2-A6 from the private stack. */
    r[2] = deck_pop(s);
    r[3] = deck_pop(s);
    r[4] = deck_pop(s);
    r[5] = deck_pop(s);
    r[6] = deck_pop(s);
    r[7] = deck_pop(s);
    r[10] = deck_pop(s);
    r[11] = deck_pop(s);
    r[12] = deck_pop(s);
    r[13] = deck_pop(s);
    r[14] = deck_pop(s);

    s->cpu.pc = 0x11e62;
}
