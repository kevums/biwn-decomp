#include "/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/projects/black-ice-white-noise/restoration/experimental/typed-deck-primitives-v1/typed-registers.h"

#include <stddef.h>
static int r8(void *ctx,uint32_t a,uint8_t *v){(void)ctx;*v=*(volatile uint8_t *)(a&0xffffffu);return 0;}
static int r16(void *ctx,uint32_t a,uint16_t *v){(void)ctx;*v=*(volatile uint16_t *)(a&0xffffffu);return 0;}
static int r32(void *ctx,uint32_t a,uint32_t *v){(void)ctx;*v=*(volatile uint32_t *)(a&0xffffffu);return 0;}
static int w8(void *ctx,uint32_t a,uint8_t v){(void)ctx;*(volatile uint8_t *)(a&0xffffffu)=v;return 0;}
static struct biwn_world_bus memory={.context=0,.read8=r8,.read16=r16,.read32=r32};
#include "/Users/kevin/Documents/Codex/2026-10-10/i-now-am-using-the-following/outputs/local-ai-lab/projects/black-ice-white-noise/restoration/experimental/deck-clear-local-typed-v3/clear-records.c"

void *memcpy(void *out,const void *in,size_t n){unsigned char *d=out;const unsigned char *p=in;while(n--)*d++=*p++;return out;}
_Static_assert(sizeof(struct biwn_task_cpu)==78,"CPU layout");
int run(struct biwn_task_cpu *cpu,uint32_t budget){
 struct biwn_deck_context s={0};s.bus=&memory;s.cpu=*cpu;
 clear_records(&s,w8,budget);
 if(s.error)return s.error;
 s.cpu.pc=deck_pop(&s);if(s.error)return s.error;*cpu=s.cpu;return 0;
}
