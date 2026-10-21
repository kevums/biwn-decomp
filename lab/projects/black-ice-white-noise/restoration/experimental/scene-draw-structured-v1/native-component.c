/* Target component proof. Bus/services are external test-provider entries.
 * This is not a console ABI shim or a standalone game. */
#include "scene-context.h"
#ifndef SCENE17_BODY_FILE
#define SCENE17_BODY_FILE "coordinator-reference.inc"
#endif
#include SCENE17_BODY_FILE
extern int native_read8(void *,uint32_t,uint8_t *);
extern int native_read16(void *,uint32_t,uint16_t *);
extern int native_read32(void *,uint32_t,uint32_t *);
extern int native_write16(void *,uint32_t,uint16_t);
extern int native_write32(void *,uint32_t,uint32_t);
extern int native_service(void *,struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
static struct biwn_world_bus memory={native_read8,native_read16,native_read32,native_write16,native_write32,0,0,0};
int run(struct biwn_task_cpu *cpu,int body){
 struct biwn_deck_context s={&memory,*cpu,native_service,0,128,0};
 scene17_body(&s);if(s.error)return s.error;
 if(!body){uint32_t ret=deck_pop(&s);if(s.error)return s.error;s.cpu.pc=ret;}
 *cpu=s.cpu;return 0;
}
void *memcpy(void *out,const void *in,unsigned long n){
 unsigned char *d=out;const unsigned char *p=in;while(n--)*d++=*p++;return out;
}
