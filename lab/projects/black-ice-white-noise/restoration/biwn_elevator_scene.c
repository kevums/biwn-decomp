#include "biwn_elevator_scene.h"
#include "biwn_elevator_input.h"
#include "biwn_transition_cleanup.h"

struct context {struct biwn_world_bus *outer,inner;biwn_actor_write8 write_byte;uint32_t scratch,word_scan,budget;};
static int r8(void *p,uint32_t a,uint8_t *v){struct context *s=p;return s->outer->read8(s->outer->context,a,v);}
static int r16(void *p,uint32_t a,uint16_t *v){struct context *s=p;return s->outer->read16(s->outer->context,a,v);}
static int r32(void *p,uint32_t a,uint32_t *v){struct context *s=p;return s->outer->read32(s->outer->context,a,v);}
static int w8(void *p,uint32_t a,uint8_t v){struct context *s=p;return s->write_byte(s->outer->context,a,v);}
static int w16(void *p,uint32_t a,uint16_t v){struct context *s=p;return s->outer->write16(s->outer->context,a,v);}
static int w32(void *p,uint32_t a,uint32_t v){struct context *s=p;return s->outer->write32(s->outer->context,a,v);}
static int call(void *p,uint32_t target,const uint32_t *args,uint32_t count,uint32_t *out)
{
 struct context *s=p;
 if(!out||(count&&!args))return BIWN_ELEVATOR_BAD_ARGUMENT;
 if(target==0x20f0cu){
  if(count)return BIWN_ELEVATOR_BAD_ARGUMENT;
  return biwn_cleanup_reset_region(&s->inner,*out,s->budget,out);
 }
 if(target==0x20f78u){
  if(count!=1u)return BIWN_ELEVATOR_BAD_ARGUMENT;
  return biwn_scene_stream(&s->inner,w8,(uint16_t)args[0],s->scratch,s->word_scan,s->budget,*out,out);
 }
 return s->outer->call(s->outer->context,target,args,count,out);
}
int biwn_elevator_scene(struct biwn_world_bus *bus,biwn_actor_write8 byte_write,
 uint32_t scratch,uint32_t word_scan,uint32_t budget,uint32_t incoming,uint32_t *out)
{
 struct context s;
 if(!bus||!out||!byte_write||!scratch||!budget||word_scan>1u||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_ELEVATOR_BAD_ARGUMENT;
 s.outer=bus;s.write_byte=byte_write;s.scratch=scratch;s.word_scan=word_scan;s.budget=budget;
 s.inner=(struct biwn_world_bus){r8,r16,r32,w16,w32,call,&s,budget};
 return biwn_elevator_input(&s.inner,incoming,out);
}
