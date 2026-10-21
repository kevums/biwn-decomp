#include "biwn_input_dispatch_cpu.h"
#include <stdint.h>

static uint32_t sx_word(uint16_t v) { return (uint32_t)(v & 0x7fffu) - (uint32_t)(v & 0x8000u); }
static void bank(struct biwn_task_cpu *s) { if(s->sr & 0x2000u) s->ssp=s->registers[15]; else s->usp=s->registers[15]; }
static void nz(struct biwn_task_cpu *s,uint32_t v,unsigned bits) { uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u, sign=1u<<(bits-1); v &= mask; s->sr=(uint16_t)((s->sr&0xfff0u)|(v?0u:4u)|(v&sign?8u:0u)); }
static uint32_t alu(struct biwn_task_cpu *s,uint32_t a,uint32_t b,unsigned bits,int subtract,int compare) { uint32_t mask=bits==32?0xffffffffu:(1u<<bits)-1u,sign=1u<<(bits-1),r; unsigned carry,overflow; a &= mask; b &= mask; r=(subtract?a-b:a+b)&mask; carry=subtract?a<b:r<a; overflow=subtract?((a^b)&(a^r)&sign)!=0:((~(a^b))&(a^r)&sign)!=0; nz(s,r,bits); s->sr=(uint16_t)((s->sr&~(compare?3u:0x13u))|(carry?(compare?1u:0x11u):0u)|(overflow?2u:0u)); return r; }

int biwn_attack_CPU_step(struct biwn_world_bus *bus, struct biwn_task_cpu *state) {
    if (!bus || !state) return 1;
    if (!bus->read16 || !bus->read32 || !bus->write16 || !bus->write32) return 1;

    struct biwn_task_cpu s = *state;
    uint32_t pc = s.pc;

    switch (pc) {
        case 0x18DF2: {
            uint32_t a7 = s.registers[15];
            a7 -= 4;
            uint32_t val = s.registers[10];
            if (bus->write32(bus->context, a7, val) != 0) return 2;
            s.registers[15] = a7;
            bank(&s);
            nz(&s, val, 32);
            s.pc = 0x18DF4;
            *state = s;
            return 0;
        }
        case 0x18DF4: {
            uint16_t val;
            if (bus->read16(bus->context, 0x49d5e, &val) != 0) return 2;
            nz(&s, val, 16);
            s.pc = 0x18DFA;
            *state = s;
            return 0;
        }
        case 0x18DFA: {
            if ((s.sr & 0x0004) != 0) {
                s.pc = 0x18E66;
            } else {
                s.pc = 0x18DFC;
            }
            *state = s;
            return 0;
        }
        case 0x18DFC: {
            uint16_t val;
            if (bus->read16(bus->context, 0x49d5c, &val) != 0) return 2;
            nz(&s, val, 16);
            s.pc = 0x18E02;
            *state = s;
            return 0;
        }
        case 0x18E02: {
            if ((s.sr & 0x0004) != 0) {
                s.pc = 0x18E66;
            } else {
                s.pc = 0x18E04;
            }
            *state = s;
            return 0;
        }
        case 0x18E04: {
            uint16_t val;
            if (bus->read16(bus->context, 0x49d62, &val) != 0) return 2;
            nz(&s, val, 16);
            s.pc = 0x18E0A;
            *state = s;
            return 0;
        }
        case 0x18E0A: {
            int z = (s.sr & 0x0004) != 0;
            int n = (s.sr & 0x0008) != 0;
            int v = (s.sr & 0x0002) != 0;
            if (!z && (n == v)) {
                s.pc = 0x18E66;
            } else {
                s.pc = 0x18E0C;
            }
            *state = s;
            return 0;
        }
        case 0x18E0C: {
            uint16_t val;
            if (bus->read16(bus->context, 0x49d66, &val) != 0) return 2;
            s.registers[0] = (s.registers[0] & 0xffff0000u) | val;
            nz(&s, val, 16);
            s.pc = 0x18E12;
            *state = s;
            return 0;
        }
        case 0x18E12: {
            uint32_t d0 = s.registers[0];
            uint16_t w = (uint16_t)(d0 & 0xffffu);
            uint32_t old_sign = (w >> 15) & 1u;
            uint32_t new_w = (uint32_t)(w << 1) & 0xffffu;
            uint32_t new_sign = (new_w >> 15) & 1u;
            uint32_t c = old_sign;
            uint32_t v = (old_sign ^ new_sign);
            s.registers[0] = (d0 & 0xffff0000u) | new_w;
            nz(&s, new_w, 16);
            s.sr = (uint16_t)((s.sr & ~(0x0011u)) | (c ? 0x0011u : 0u) | (v ? 2u : 0u));
            s.pc = 0x18E14;
            *state = s;
            return 0;
        }
        case 0x18E14: {
            uint16_t val;
            if (bus->read16(bus->context, 0x49d12, &val) != 0) return 2;
            uint32_t d0 = s.registers[0];
            uint16_t w = (uint16_t)(d0 & 0xffffu);
            uint32_t r = alu(&s, w, val, 16, 0, 0);
            s.registers[0] = (d0 & 0xffff0000u) | r;
            s.pc = 0x18E1A;
            *state = s;
            return 0;
        }
        case 0x18E1A: {
            uint32_t d0 = s.registers[0];
            uint16_t w = (uint16_t)(d0 & 0xffffu);
            uint32_t r = alu(&s, w, 0xc8u, 16, 0, 0);
            s.registers[0] = (d0 & 0xffff0000u) | r;
            s.pc = 0x18E1E;
            *state = s;
            return 0;
        }
        case 0x18E1E: {
            uint32_t d0 = s.registers[0];
            uint16_t w = (uint16_t)(d0 & 0xffffu);
            s.registers[10] = sx_word(w);
            s.pc = 0x18E20;
            *state = s;
            return 0;
        }
        case 0x18E20: {
            uint32_t a7 = s.registers[15];
            a7 -= 2;
            if (bus->write16(bus->context, a7, 0x0064) != 0) return 2;
            nz(&s, 0x0064u, 16);
            s.registers[15] = a7;
            bank(&s);
            s.pc = 0x18E24;
            *state = s;
            return 0;
        }
        case 0x18E24: {
            uint32_t a7 = s.registers[15];
            a7 -= 4;
            if (bus->write32(bus->context, a7, 0x18E2A) != 0) return 2;
            s.registers[15] = a7;
            bank(&s);
            s.pc = 0x1A77C;
            *state = s;
            return 0;
        }
        case 0x18E2A: {
            uint32_t d0 = s.registers[0] & 0x3ffu;
            s.registers[0] = d0;
            nz(&s, d0, 32);
            s.pc = 0x18E30;
            *state = s;
            return 0;
        }
        case 0x18E30: {
            uint32_t a7 = s.registers[15] + 2;
            s.registers[15] = a7;
            bank(&s);
            s.pc = 0x18E32;
            *state = s;
            return 0;
        }
        case 0x18E32: {
            uint32_t a2 = s.registers[10];
            uint32_t d0 = s.registers[0];
            alu(&s, d0, a2, 32, 1, 1);
            s.pc = 0x18E34;
            *state = s;
            return 0;
        }
        case 0x18E34: {
            int n = (s.sr & 0x0008) != 0;
            int v = (s.sr & 0x0002) != 0;
            if (n == v) {
                s.pc = 0x18E5E;
            } else {
                s.pc = 0x18E36;
            }
            *state = s;
            return 0;
        }
        case 0x18E36: {
            uint16_t val;
            if (bus->read16(bus->context, 0x49d60, &val) != 0) return 2;
            s.registers[0] = (s.registers[0] & 0xffff0000u) | val;
            nz(&s, val, 16);
            s.pc = 0x18E3C;
            *state = s;
            return 0;
        }
        case 0x18E3C: {
            uint32_t d0 = s.registers[0];
            uint16_t w = (uint16_t)(d0 & 0xffffu);
            int32_t sw = (int32_t)(w & 0x7fffu) - (int32_t)(w & 0x8000u);
            int32_t r = sw * 206;
            s.registers[0] = (uint32_t)r;
            nz(&s, (uint32_t)r, 32);
            s.sr = (uint16_t)((s.sr & ~0x0003u));
            s.pc = 0x18E40;
            *state = s;
            return 0;
        }
        case 0x18E40: {
            s.registers[9] = s.registers[0];
            s.pc = 0x18E42;
            *state = s;
            return 0;
        }
        case 0x18E42: {
            s.registers[9] += 0x49e34u;
            s.pc = 0x18E48;
            *state = s;
            return 0;
        }
        case 0x18E48: {
            uint16_t val;
            if (bus->read16(bus->context, 0x49d5a, &val) != 0) return 2;
            s.registers[0] = (s.registers[0] & 0xffff0000u) | val;
            nz(&s, val, 16);
            s.pc = 0x18E4E;
            *state = s;
            return 0;
        }
        case 0x18E4E: {
            uint32_t d0 = s.registers[0];
            uint16_t w = (uint16_t)(d0 & 0xffffu);
            uint32_t ext = sx_word(w);
            s.registers[0] = ext;
            nz(&s, ext, 32);
            s.pc = 0x18E50;
            *state = s;
            return 0;
        }
        case 0x18E50: {
            s.registers[8] = 0x461b4u;
            s.pc = 0x18E56;
            *state = s;
            return 0;
        }
        case 0x18E56: {
            uint32_t value = s.registers[0];
            s.registers[0] = alu(&s, value, value, 32, 0, 0);
            s.pc = 0x18E58;
            *state = s;
            return 0;
        }
        case 0x18E58: {
            uint32_t a0 = s.registers[8];
            uint32_t d0 = s.registers[0];
            uint32_t addr = a0 + d0;
            uint16_t val;
            if (bus->read16(bus->context, addr, &val) != 0) return 2;
            s.registers[0] = (s.registers[0] & 0xffff0000u) | val;
            nz(&s, val, 16);
            s.pc = 0x18E5C;
            *state = s;
            return 0;
        }
        case 0x18E5C: {
            uint32_t a1 = s.registers[9];
            uint16_t mem;
            if (bus->read16(bus->context, a1, &mem) != 0) return 2;
            uint32_t d0 = s.registers[0];
            uint16_t w = (uint16_t)(d0 & 0xffffu);
            uint32_t r = alu(&s, mem, w, 16, 1, 0);
            if (bus->write16(bus->context, a1, (uint16_t)r) != 0) return 2;
            s.pc = 0x18E5E;
            *state = s;
            return 0;
        }
        case 0x18E5E: {
            if (bus->write16(bus->context, 0x49d62, 0x012c) != 0) return 2;
            nz(&s, 0x012cu, 16);
            s.pc = 0x18E66;
            *state = s;
            return 0;
        }
        case 0x18E66: {
            uint32_t val;
            if (bus->read32(bus->context, 0x49c50, &val) != 0) return 2;
            s.registers[0] = val;
            nz(&s, val, 32);
            s.pc = 0x18E6C;
            *state = s;
            return 0;
        }
        case 0x18E6C: {
            uint32_t d0 = s.registers[0];
            uint32_t c = (d0 >> 5) & 1u;
            uint32_t r;
            if (d0 & 0x80000000u) {
                r = (d0 >> 6) | 0xFC000000u;
            } else {
                r = d0 >> 6;
            }
            s.registers[0] = r;
            nz(&s, r, 32);
            s.sr = (uint16_t)((s.sr & ~0x0013u) | (c ? 0x0011u : 0u));
            s.pc = 0x18E6E;
            *state = s;
            return 0;
        }
        case 0x18E6E: {
            uint32_t d0 = s.registers[0];
            alu(&s, d0, 0xbfu, 32, 1, 1);
            s.pc = 0x18E74;
            *state = s;
            return 0;
        }
        case 0x18E74: {
            if ((s.sr & 0x0004) != 0) {
                s.pc = 0x18E76;
            } else {
                s.pc = 0x18E8E;
            }
            *state = s;
            return 0;
        }
        case 0x18E76: {
            uint32_t val;
            if (bus->read32(bus->context, 0x49c56, &val) != 0) return 2;
            s.registers[0] = val;
            nz(&s, val, 32);
            s.pc = 0x18E7C;
            *state = s;
            return 0;
        }
        case 0x18E7C: {
            uint32_t d0 = s.registers[0];
            uint32_t c = (d0 >> 5) & 1u;
            uint32_t r;
            if (d0 & 0x80000000u) {
                r = (d0 >> 6) | 0xFC000000u;
            } else {
                r = d0 >> 6;
            }
            s.registers[0] = r;
            nz(&s, r, 32);
            s.sr = (uint16_t)((s.sr & ~0x0013u) | (c ? 0x0011u : 0u));
            s.pc = 0x18E7E;
            *state = s;
            return 0;
        }
        case 0x18E7E: {
            uint32_t d0 = s.registers[0];
            alu(&s, d0, 0x22fu, 32, 1, 1);
            s.pc = 0x18E84;
            *state = s;
            return 0;
        }
        case 0x18E84: {
            if ((s.sr & 0x0004) != 0) {
                s.pc = 0x18E86;
            } else {
                s.pc = 0x18E8E;
            }
            *state = s;
            return 0;
        }
        case 0x18E86: {
            if (bus->write16(bus->context, 0x43d98, 0x0001) != 0) return 2;
            nz(&s, 0x0001u, 16);
            s.pc = 0x18E8E;
            *state = s;
            return 0;
        }
        case 0x18E8E: {
            uint32_t a7 = s.registers[15];
            uint32_t val;
            if (bus->read32(bus->context, a7, &val) != 0) return 2;
            s.registers[10] = val;
            a7 += 4;
            s.registers[15] = a7;
            bank(&s);
            s.pc = 0x18E90;
            *state = s;
            return 0;
        }
        case 0x18E90: {
            uint32_t a7 = s.registers[15];
            uint32_t ret;
            if (bus->read32(bus->context, a7, &ret) != 0) return 2;
            s.registers[15] = a7 + 4;
            bank(&s);
            s.pc = ret;
            *state = s;
            return 0;
        }
        default:
            return 7;
    }
}
