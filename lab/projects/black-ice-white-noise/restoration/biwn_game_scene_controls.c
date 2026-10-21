#include "biwn_game_scene_controls.h"
#include "biwn_scene_stream.h"

struct context {struct biwn_world_bus *outer,inner;biwn_input_write8 byte_write;uint32_t scratch,word_scan;};
static int r8(void *p,uint32_t a,uint8_t *v){struct context *s=p;return s->outer->read8(s->outer->context,a,v);}
static int r16(void *p,uint32_t a,uint16_t *v){struct context *s=p;return s->outer->read16(s->outer->context,a,v);}
static int r32(void *p,uint32_t a,uint32_t *v){struct context *s=p;return s->outer->read32(s->outer->context,a,v);}
static int w8(void *p,uint32_t a,uint8_t v){struct context *s=p;return s->byte_write(s->outer->context,a,v);}
static int w16(void *p,uint32_t a,uint16_t v){struct context *s=p;return s->outer->write16(s->outer->context,a,v);}
static int w32(void *p,uint32_t a,uint32_t v){struct context *s=p;return s->outer->write32(s->outer->context,a,v);}
static int call(void *p,uint32_t target,const uint32_t *args,uint32_t count,uint32_t *out)
{
 struct context *s=p;
 if(target==0x20f78u){
  if(count!=1u||!args||!out)return BIWN_DISPATCH_BAD_ARGUMENT;
  return biwn_scene_stream(&s->inner,w8,(uint16_t)args[0],s->scratch,s->word_scan,32768u,*out,out);
 }
 return s->outer->call(s->outer->context,target,args,count,out);
}
enum biwn_dispatch_status biwn_game_scene_controls(struct biwn_world_bus *bus,
 biwn_input_write8 byte_write,uint32_t display_scratch,uint32_t stream_scratch,
 uint32_t word_scan,uint32_t budget,uint32_t incoming,uint32_t *out)
{
 struct context s;
 if(!bus||!out||!byte_write||!display_scratch||!stream_scratch||word_scan>1u||!budget||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_DISPATCH_BAD_ARGUMENT;
 s.outer=bus;s.byte_write=byte_write;s.scratch=stream_scratch;s.word_scan=word_scan;
 s.inner=(struct biwn_world_bus){r8,r16,r32,w16,w32,call,&s,bus->poll_limit};
 return biwn_game_controls_with_scratch(&s.inner,w8,display_scratch,budget,incoming,out);
}
