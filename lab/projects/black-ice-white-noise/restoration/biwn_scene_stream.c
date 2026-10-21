#include "biwn_scene_stream.h"
#include "biwn_scene_loading.h"
#include "biwn_texture_cache.h"
#include "biwn_resources.h"
#include "biwn_memory.h"
#include "biwn_transition_cleanup.h"
#include "biwn_cd_math.h"
#include "biwn_cd_wrappers.h"
#include "biwn_signed_division.h"
#include "biwn_task_create.h"
#include "biwn_gpu_commands.h"
#include "biwn_geometry.h"

struct context {
 struct biwn_world_bus *outer,inner;
 biwn_actor_write8 write_byte;
 uint32_t scratch,word_scan,budget;
 struct biwn_scene_alignment_fault fault;
 struct biwn_scene_texture_queue *queue;
};
/* M68000 physical address decoding. Keep tag bits in stored pointer values
 * and logical arguments; only the address presented to the bus is24bits. */
static int r8(void *p,uint32_t a,uint8_t *v){struct context *s=p;return s->outer->read8(s->outer->context,a&0xffffffu,v);}
static int alignment(struct context *s,uint32_t a,uint32_t width,uint32_t write)
{
 if(!(a&1u))return 0;
 if(!s->fault.width)s->fault=(struct biwn_scene_alignment_fault){a,a&0xffffffu,width,write};
 return 1;
}
static int r16(void *p,uint32_t a,uint16_t *v){struct context *s=p;if(alignment(s,a,2,0))return 1;return s->outer->read16(s->outer->context,a&0xffffffu,v);}
static int r32(void *p,uint32_t a,uint32_t *v){struct context *s=p;if(alignment(s,a,4,0))return 1;return s->outer->read32(s->outer->context,a&0xffffffu,v);}
static int w8(void *p,uint32_t a,uint8_t v){struct context *s=p;return s->write_byte(s->outer->context,a&0xffffffu,v);}
static int w16(void *p,uint32_t a,uint16_t v){struct context *s=p;if(alignment(s,a,2,1))return 1;return s->outer->write16(s->outer->context,a&0xffffffu,v);}
static int w32(void *p,uint32_t a,uint32_t v){struct context *s=p;if(alignment(s,a,4,1))return 1;return s->outer->write32(s->outer->context,a&0xffffffu,v);}
static int call(void *opaque,uint32_t target,const uint32_t *args,uint32_t n,uint32_t *out)
{
 struct context *s=opaque;uint32_t a[3]={0,0,0},q,r;unsigned i;
 if(!out||(n&&!args))return BIWN_SCENE_BAD_ARGUMENT;
 switch(target){
 case 0x20aa0u:case 0x20b2au:case 0x20c16u:case 0x20cf8u:case 0x20d7cu:
  if(n!=((target==0x20b2au||target==0x20cf8u)?3u:0u))return BIWN_SCENE_BAD_ARGUMENT;
  for(i=0;i<n;i++)a[i]=args[i];
  return biwn_scene_loading_with_queue(&s->inner,target,a[0],a[1],(uint16_t)a[2],*out,s->budget,out,s->queue);
 case 0x1b044u:
  if(n!=5u)return BIWN_RESOURCE_BAD_ARGUMENT;
  if(s->word_scan)return biwn_resource_load_word_scan(&s->inner,args[0],args[1],args[2],args[3],args[4],s->budget,out);
  return biwn_resource_load(&s->inner,args[0],args[1],args[2],args[3],args[4],s->budget,out);
 case 0x1ac68u:
  if(n!=1u)return BIWN_TEXTURE_BAD_ARGUMENT;
  return biwn_texture_acquire(&s->inner,(uint16_t)args[0],s->scratch,*out,s->budget,out);
 case 0x1ac3cu:
  if(n!=1u)return BIWN_TEXTURE_BAD_ARGUMENT;
  return biwn_texture_lookup(&s->inner,(uint16_t)args[0],s->budget,out);
 case 0x13ae0u:case 0x134dcu:case 0x137e0u:case 0x10520u:case 0x105dau:
  return biwn_actor_service(&s->inner,w8,target,args,n,*out,s->budget,out);
 case 0xdf6cu:
  if(n!=2u)return BIWN_CREATE_BAD_ARGUMENT;
  return biwn_task_create_logical(&s->inner,args[0],args[1],s->scratch,out);
 case 0x102c4u:
  if(n!=1u)return BIWN_GEOMETRY_BAD_ARGUMENT;
  return biwn_geometry_find_tile(&s->inner,args[0],s->budget,out);
 case 0xe2b8u: {
  struct biwn_gpu_bus gpu={s->inner.read32,s->inner.write32,s->inner.context,s->budget};
  if(n!=3u)return BIWN_SCENE_BAD_ARGUMENT;
  /* Source E2B8 leaves D0 unchanged. The host device executes4B00 and
   * supplies its acknowledgement; no decoded pixels are a call fixture. */
  return biwn_gpu_submit_4b00(&gpu,args[0],args[1],args[2]);
 }
 case 0x152a2u:
  if(n!=1u)return BIWN_MEMORY_BAD_ARGUMENT;
  return biwn_memory_allocate(&s->inner,args[0],s->budget,out);
 case 0x15200u:
  if(n)return BIWN_MEMORY_BAD_ARGUMENT;
  return biwn_memory_compact(&s->inner,s->budget,out);
 case 0xe3e0u:case 0xe3eeu:
  if(n!=3u)return BIWN_MEMORY_BAD_ARGUMENT;
  return biwn_memory_copy(&s->inner,w8,target,args[0],args[1],args[2],*out,s->budget,out);
 case 0x1545cu:
  if(n!=1u)return BIWN_CLEANUP_BAD_ARGUMENT;
  return biwn_cleanup_free_handle(&s->inner,args[0],*out,s->budget,out);
 case 0xd206u: {
  uint8_t toc[256];uint16_t v;struct biwn_cd_position position;int status;
  if(n!=2u)return BIWN_SCENE_BAD_ARGUMENT;
  for(i=0;i<256;i+=2){if(r16(s,0x2c00u+i,&v))return BIWN_SCENE_BUS_ERROR;toc[i]=(uint8_t)(v>>8);toc[i+1]=(uint8_t)v;}
  status=biwn_cd_offset_msf(args[0],args[1],toc,sizeof(toc),&position);
  if(!status)*out=position.packed_binary_msf;
  return status;
 }
 case 0xd2f0u:
  if(n!=3u)return BIWN_SCENE_BAD_ARGUMENT;
  return biwn_cd_read_wrapper(&s->inner,args[0],args[1],args[2],out);
 case 0xd306u:
  if(n)return BIWN_SCENE_BAD_ARGUMENT;
  return biwn_cd_stop_wrapper(&s->inner,*out,out);
 case 0xe588u:case 0xe60au:
  if(n!=2u)return BIWN_SCENE_BAD_ARGUMENT;
  if(biwn_signed_division(args[0],args[1],&q,&r))return BIWN_SCENE_DEPENDENCY_ERROR;
  *out=target==0xe588u?q:r;return 0;
 default:return s->outer->call(s->outer->context,target,args,n,out);
 }
}
int biwn_scene_stream(struct biwn_world_bus *bus,biwn_actor_write8 write_byte,
 uint16_t mode,uint32_t scratch,uint32_t word_scan,uint32_t budget,uint32_t incoming,uint32_t *out)
{return biwn_scene_stream_with_fault(bus,write_byte,mode,scratch,word_scan,budget,incoming,out,0);}
static int run_stream(struct biwn_world_bus *bus,biwn_actor_write8 write_byte,
 uint16_t mode,uint32_t scratch,uint32_t word_scan,uint32_t budget,uint32_t incoming,uint32_t *out,
 struct biwn_scene_alignment_fault *fault,struct biwn_scene_texture_queue *queue)
{
 struct context s;uint32_t result=incoming;int status;
 if(fault)*fault=(struct biwn_scene_alignment_fault){0};
 if(!bus||!out||!write_byte||!scratch||!budget||word_scan>1u||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_SCENE_BAD_ARGUMENT;
 s.outer=bus;s.write_byte=write_byte;s.scratch=scratch;s.word_scan=word_scan;s.budget=budget;s.queue=queue;
 s.fault=(struct biwn_scene_alignment_fault){0};
 s.inner=(struct biwn_world_bus){r8,r16,r32,w16,w32,call,&s,budget};
 if(queue){uint16_t pending;if(r16(&s,0x15ece0u,&pending))return BIWN_SCENE_BUS_ERROR;if(pending)return BIWN_SCENE_BAD_ARGUMENT;}
 status=biwn_scene_loading_with_queue(&s.inner,0x20f78u,mode,0,0,result,budget,&result,queue);
 if(fault)*fault=s.fault;
 if(!status)*out=result;
 return status;
}
int biwn_scene_stream_with_fault(struct biwn_world_bus *bus,biwn_actor_write8 write_byte,
 uint16_t mode,uint32_t scratch,uint32_t word_scan,uint32_t budget,uint32_t incoming,uint32_t *out,
 struct biwn_scene_alignment_fault *fault)
{return run_stream(bus,write_byte,mode,scratch,word_scan,budget,incoming,out,fault,0);}
int biwn_scene_stream_repaired_queue(struct biwn_world_bus *bus,biwn_actor_write8 write_byte,
 uint16_t mode,uint32_t scratch,uint32_t word_scan,uint32_t budget,uint32_t incoming,uint32_t *out,
 struct biwn_scene_alignment_fault *fault,uint16_t *ids,uint32_t capacity,uint32_t *peak)
{
 struct biwn_scene_texture_queue queue={ids,capacity,0};int status;
 if(peak)*peak=0;
 if(fault)*fault=(struct biwn_scene_alignment_fault){0};
 if(!ids||capacity<50u||capacity>0x7fffu)return BIWN_SCENE_BAD_ARGUMENT;
 status=run_stream(bus,write_byte,mode,scratch,word_scan,budget,incoming,out,fault,&queue);
 if(peak)*peak=queue.high_water;
 return status;
}
int biwn_scene_stream_textures(struct biwn_world_bus *bus,biwn_actor_write8 write_byte,
 uint16_t mode,uint32_t scratch,uint32_t word_scan,uint32_t budget,uint32_t *out)
{
 struct context s;
 if(!bus||!out||!write_byte||!scratch||!budget||word_scan>1u||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_SCENE_BAD_ARGUMENT;
 s.outer=bus;s.write_byte=write_byte;s.scratch=scratch;s.word_scan=word_scan;s.budget=budget;s.queue=0;
 s.fault=(struct biwn_scene_alignment_fault){0};
 s.inner=(struct biwn_world_bus){r8,r16,r32,w16,w32,call,&s,budget};
 return biwn_resource_textures(&s.inner,mode,scratch,out);
}
