/* In-place context matches the existing native Deck frame's first98bytes.
 * Avoid a second CPU/context copy on the physical C stack. */
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
int run(struct biwn_deck_context *s,int body){
 s->bus=&memory;s->service=native_service;s->opaque=0;s->budget=128;s->error=0;
 scene17_body(s);if(s->error)return s->error;
 if(!body){uint32_t ret=deck_pop(s);if(s->error)return s->error;s->cpu.pc=ret;}
 return 0;
}
