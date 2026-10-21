#include "biwn_world_cpu.h"
#include <stddef.h>
struct task {struct biwn_world_bus *bus;struct biwn_task_cpu cpu;};
static void bank(struct task*s){if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];else s->cpu.usp=s->cpu.registers[15];}
static int rd16(struct task*s,uint32_t a,uint16_t*v){return s->bus->read16(s->bus->context,a,v)?2:0;}
static int rd32(struct task*s,uint32_t a,uint32_t*v){return s->bus->read32(s->bus->context,a,v)?2:0;}
static int push32(struct task*s,uint32_t v){s->cpu.registers[15]-=4;bank(s);return s->bus->write32(s->bus->context,s->cpu.registers[15],v)?2:0;}
static int pop32(struct task*s,uint32_t*v){int e=rd32(s,s->cpu.registers[15],v);if(e)return e;s->cpu.registers[15]+=4;bank(s);return 0;}
static void cmp16(struct task*s,uint16_t operand,uint16_t immediate){uint16_t r=(uint16_t)(operand-immediate);s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(r&0x8000u?8u:0u)|(r?0u:4u)|(((operand^immediate)&(operand^r)&0x8000u)?2u:0u)|(operand<immediate?1u:0u));}
#define CHECK(e) do{int error=(e);if(error)return error;}while(0)
int biwn_tile_task_cpu_run(struct biwn_world_bus*bus,struct biwn_task_cpu*state,uint32_t budget){struct task s;uint32_t value;uint16_t word;
 if(!bus||!state||!budget||!bus->read16||!bus->read32||!bus->write32)return 1;s.bus=bus;s.cpu=*state;
 while(budget--){switch(s.cpu.pc){
case 0x21D1A:
    CHECK(rd16(&s, 0x49C60, &word));
    cmp16(&s, word, 1);
    s.cpu.pc = 0x21D22;
    break;
case 0x21D22:
    if ((s.cpu.sr & 4) == 0) {
        s.cpu.pc = 0x21D2A;
    } else {
        s.cpu.pc = 0x21D24;
    }
    break;
case 0x21D24:
    CHECK(push32(&s, 0x21D2A));
    s.cpu.pc = 0x212E8;
    break;
case 0x21D2A:
    CHECK(push32(&s, 0x21D30));
    s.cpu.pc = 0xDF60;
    *state = s.cpu;
    return 6;
case 0x21D30:
    s.cpu.pc = 0x21D1A;
    break;
case 0x212E8:
    s.cpu.registers[15] -= 28u;
    bank(&s);
    s.cpu.pc = 0x212EC;
    break;
case 0x212EC:
    for (int i = 0; i < 11; i++) {
        int idx;
        switch (i) {
            case 0: idx = 14; break;
            case 1: idx = 13; break;
            case 2: idx = 12; break;
            case 3: idx = 11; break;
            case 4: idx = 10; break;
            case 5: idx = 7; break;
            case 6: idx = 6; break;
            case 7: idx = 5; break;
            case 8: idx = 4; break;
            case 9: idx = 3; break;
            case 10: idx = 2; break;
        }
        CHECK(push32(&s, s.cpu.registers[idx]));
    }
    s.cpu.pc = 0x212F0;
    break;
case 0x212F0:
    s.cpu.registers[8] = 0x49C8C;
    s.cpu.pc = 0x212F6;
    break;
case 0x212F6:
    CHECK(rd16(&s, s.cpu.registers[8], &word));
    cmp16(&s, word, 12);
    s.cpu.pc = 0x212FA;
    break;
case 0x212FA:
    if ((s.cpu.sr & 4) != 0) {
        s.cpu.pc = 0x21D10;
    } else {
        return 7;
    }
    break;
case 0x21D10:
    for (int i = 0; i < 11; i++) {
        int idx;
        switch (i) {
            case 0: idx = 2; break;
            case 1: idx = 3; break;
            case 2: idx = 4; break;
            case 3: idx = 5; break;
            case 4: idx = 6; break;
            case 5: idx = 7; break;
            case 6: idx = 10; break;
            case 7: idx = 11; break;
            case 8: idx = 12; break;
            case 9: idx = 13; break;
            case 10: idx = 14; break;
        }
        CHECK(pop32(&s, &value));
        s.cpu.registers[idx] = value;
    }
    s.cpu.pc = 0x21D14;
    break;
case 0x21D14:
    s.cpu.registers[15] += 28u;
    bank(&s);
    s.cpu.pc = 0x21D18;
    break;
case 0x21D18:
    CHECK(pop32(&s, &value));
    s.cpu.pc = value;
    break;
default:return 7;}}return 4;}
