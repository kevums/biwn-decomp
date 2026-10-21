#ifndef BIWN_DECK_COORDINATE_CONTRACT_H
#define BIWN_DECK_COORDINATE_CONTRACT_H
#include "../../biwn_world_cpu.h"
/* Coordinator ABI/68000 glue. The authored body is a structured recovery of
 * 11D1A..11E64, with E26C and E540 explicit dependencies. No instruction loop.
 * Services stop at their outer RTS; this glue consumes that return address.
 * Added host errors leave the supplied CPU unchanged, retaining RAM effects.
 * Arbitrary aliases, interrupts, tracing and timing are outside the contract. */
struct biwn_deck_context {
 struct biwn_world_bus *bus;
 struct biwn_task_cpu cpu;
 biwn_world_cpu_service service;
 void *opaque;
 uint32_t budget;
 int error;
};
static inline uint32_t deck_sx16(uint32_t v) {return (v&0x7fffu)-(v&0x8000u);}
static inline void deck_bank(struct biwn_deck_context *s) {
 if(s->cpu.sr&0x2000u)s->cpu.ssp=s->cpu.registers[15];
 else s->cpu.usp=s->cpu.registers[15];
}
static inline uint32_t deck_read(struct biwn_deck_context *s,uint32_t a,unsigned w) {
 uint32_t v=0;uint16_t h=0;
 if(s->error)return 0;
 if(w==2){if(s->bus->read16(s->bus->context,a&0xffffffu,&h))s->error=2;v=h;}
 else if(s->bus->read32(s->bus->context,a&0xffffffu,&v))s->error=2;
 return v;
}
static inline void deck_write(struct biwn_deck_context *s,uint32_t a,unsigned w,uint32_t v) {
 if(s->error)return;
 if(w==2){if(s->bus->write16(s->bus->context,a&0xffffffu,(uint16_t)v))s->error=2;}
 else if(s->bus->write32(s->bus->context,a&0xffffffu,v))s->error=2;
}
static inline void deck_nz(struct biwn_deck_context *s,uint32_t v,unsigned bits) {
 uint32_t mask=bits==32?0xffffffffu:0xffffu;v&=mask;
 s->cpu.sr=(uint16_t)((s->cpu.sr&0xfff0u)|(v?0u:4u)|(v&(1u<<(bits-1))?8u:0u));
}
static inline uint32_t deck_alu(struct biwn_deck_context *s,uint32_t a,uint32_t b,int sub,int cmp) {
 uint32_t v=sub?a-b:a+b;
 unsigned carry=sub?a<b:v<a;
 unsigned overflow=(sub?((a^b)&(a^v)):((~(a^b))&(a^v)))>>31;
 deck_nz(s,v,32);
 s->cpu.sr=(uint16_t)((s->cpu.sr&~(cmp?3u:0x13u))|(carry?(cmp?1u:0x11u):0u)|(overflow?2u:0u));
 return v;
}
static inline uint32_t deck_asl5(struct biwn_deck_context *s,uint32_t v) {
 unsigned carry=0,overflow=0;
 for(unsigned i=0;i<5;i++){uint32_t old=v;carry=v>>31;v<<=1;overflow|=(old^v)>>31;}
 deck_nz(s,v,32);s->cpu.sr=(uint16_t)((s->cpu.sr&~0x13u)|(carry?0x11u:0u)|(overflow?2u:0u));return v;
}
static inline void deck_push(struct biwn_deck_context *s,uint32_t v) {
 s->cpu.registers[15]-=4;deck_bank(s);deck_write(s,s->cpu.registers[15],4,v);
}
static inline uint32_t deck_pop(struct biwn_deck_context *s) {
 uint32_t v=deck_read(s,s->cpu.registers[15],4);s->cpu.registers[15]+=4;deck_bank(s);return v;
}
static inline void deck_adjust(struct biwn_deck_context *s,uint32_t n) {
 s->cpu.registers[15]+=n;deck_bank(s);
}
static inline void deck_call(struct biwn_deck_context *s,uint32_t target,uint32_t ret) {
 uint32_t sp,value;int status;
 if(s->error)return;
 if(!s->budget){s->error=4;return;}s->budget--;
 deck_push(s,ret);s->cpu.pc=target;sp=s->cpu.registers[15];
 if(s->error)return;
 status=s->service(s->opaque,s->bus,&s->cpu,target);
 if(status){s->error=3;return;}
 if(s->cpu.registers[15]!=sp){s->error=5;return;}
 value=deck_pop(s);if(value!=ret){s->error=5;return;}s->cpu.pc=ret;
}
/* Body supplied by the local author, separately from this glue. */
void biwn_deck_coordinate_body(struct biwn_deck_context *);
int biwn_deck_coordinate_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_world_cpu_service,void *,uint32_t);
#endif
