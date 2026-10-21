#include "biwn_scene_render_pipeline.h"
#include "biwn_gpu_render_commands.h"
#include "biwn_geometry_records_cpu.h"
#include "biwn_memory.h"
#include "biwn_display_list.h"
struct render_context {
 struct biwn_world_bus *outer,inner;
 biwn_input_write8 write_byte;
 uint32_t scratch,*links,capacity,budget;
};
static int r8(void *p,uint32_t a,uint8_t *v){struct render_context *s=p;return s->outer->read8(s->outer->context,a&0xffffffu,v);}
static int r16(void *p,uint32_t a,uint16_t *v){struct render_context *s=p;return(a&1u)?1:s->outer->read16(s->outer->context,a&0xffffffu,v);}
static int r32(void *p,uint32_t a,uint32_t *v){struct render_context *s=p;return(a&1u)?1:s->outer->read32(s->outer->context,a&0xffffffu,v);}
static int w8(void *p,uint32_t a,uint8_t v){struct render_context *s=p;return s->write_byte(s->outer->context,a&0xffffffu,v);}
static int w16(void *p,uint32_t a,uint16_t v){struct render_context *s=p;return(a&1u)?1:s->outer->write16(s->outer->context,a&0xffffffu,v);}
static int w32(void *p,uint32_t a,uint32_t v){struct render_context *s=p;return(a&1u)?1:s->outer->write32(s->outer->context,a&0xffffffu,v);}
static int record_service(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target)
{
 struct render_context *s=opaque;uint32_t args[3],d0=cpu->registers[0];unsigned i;int status;
 if(target==0xe220u||target==0xe098u)return biwn_geometry_records_cpu_body(bus,cpu,w8,record_service,s,s->budget,0);
 if(target!=0xe3e0u)return BIWN_RENDER_DEPENDENCY_ERROR;
 for(i=0;i<3;i++)if(r32(s,cpu->registers[15]+4u+i*4u,&args[i]))return BIWN_RENDER_BUS_ERROR;
 status=biwn_memory_copy(bus,w8,target,args[0],args[1],args[2],d0,s->budget,&d0);
 if(!status)cpu->registers[0]=d0;
 return status;
}
static int call(void *opaque,uint32_t target,const uint32_t *args,uint32_t n,uint32_t *out)
{
 struct render_context *s=opaque;
 struct biwn_gpu_bus gpu={r32,w32,s,s->budget};
 if(!out||(n&&!args))return BIWN_RENDER_BAD_ARGUMENT;
 switch(target){
 case 0xe03au:
  if(n!=2u)return BIWN_RENDER_BAD_ARGUMENT;
  return biwn_render_clear(&s->inner,args[0],args[1],s->budget);
 case 0x17f14u:
  if(n)return BIWN_RENDER_BAD_ARGUMENT;
  return biwn_render_rotate(&s->inner,*out,out);
 case 0xe0a6u:
  if(n)return BIWN_RENDER_BAD_ARGUMENT;
  return biwn_gpu_submit_4d80(&gpu);
 case 0xe0f2u:
  if(n)return BIWN_RENDER_BAD_ARGUMENT;
  return biwn_gpu_submit_6ae0(&gpu);
 case 0xe19eu:
  if(n)return BIWN_RENDER_BAD_ARGUMENT;
  return biwn_gpu_submit_52e0(&gpu,out);
 case 0xe202u:
  if(n)return BIWN_RENDER_BAD_ARGUMENT;
  return biwn_gpu_submit_57a0(&gpu);
 case 0xe098u:
  if(n)return BIWN_RENDER_BAD_ARGUMENT;
  return biwn_gpu_wait_idle(&gpu);
 case 0x170a0u: {
  struct biwn_task_cpu cpu={0};int status;
  if(n)return BIWN_RENDER_BAD_ARGUMENT;
  cpu.pc=target;cpu.sr=0x2000;cpu.registers[0]=*out;
  cpu.registers[15]=s->scratch;cpu.ssp=s->scratch;
  status=biwn_geometry_records_cpu_body(&s->inner,&cpu,w8,record_service,s,s->budget,0);
  if(!status)*out=cpu.registers[0];
  return status;
 }
 case 0x185b2u:
  if(n!=2u)return BIWN_RENDER_BAD_ARGUMENT;
  return biwn_display_list(&s->inner,args[0],args[1],s->links,s->capacity,s->budget,out);
 default:return s->outer->call(s->outer->context,target,args,n,out);
 }
}
int biwn_scene_render_pipeline(struct biwn_world_bus *bus,biwn_input_write8 write_byte,
 uint32_t scratch,uint32_t *links,uint32_t capacity,uint32_t budget,uint32_t incoming,uint32_t *out)
{
 struct render_context s;uint32_t result=incoming;int status;
 if(!bus||!write_byte||scratch<256u||(scratch&1u)||!links||!capacity||!budget||!out||!bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_RENDER_BAD_ARGUMENT;
 s.outer=bus;s.write_byte=write_byte;s.scratch=scratch;s.links=links;s.capacity=capacity;s.budget=budget;
 s.inner=(struct biwn_world_bus){r8,r16,r32,w16,w32,call,&s,budget};
 status=biwn_render_scene(&s.inner,budget,result,&result);
 if(!status)*out=result;
 return status;
}
