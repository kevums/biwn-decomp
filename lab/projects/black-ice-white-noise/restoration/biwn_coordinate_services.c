/* Coordinator adapter; linked routine bodies retain their existing sources. */
#include "biwn_coordinate_services.h"
#include "biwn_panel_refresh.h"
#include "biwn_text.h"
#include "biwn_input_poll.h"
#include "biwn_inventory_select.h"
#include "biwn_task_gates.h"
#include "biwn_transition_cleanup.h"
struct service_context {struct biwn_world_bus *outer,inner;};
static int read8(void *opaque,uint32_t address,uint8_t *value)
{struct service_context *s=opaque;return s->outer->read8(s->outer->context,address,value);}
static int read16(void *opaque,uint32_t address,uint16_t *value)
{struct service_context *s=opaque;return s->outer->read16(s->outer->context,address,value);}
static int read32(void *opaque,uint32_t address,uint32_t *value)
{struct service_context *s=opaque;return s->outer->read32(s->outer->context,address,value);}
static int write16(void *opaque,uint32_t address,uint16_t value)
{struct service_context *s=opaque;return s->outer->write16(s->outer->context,address,value);}
static int write32(void *opaque,uint32_t address,uint32_t value)
{struct service_context *s=opaque;return s->outer->write32(s->outer->context,address,value);}
static int call(void *opaque,uint32_t target,const uint32_t *args,uint32_t count,uint32_t *out)
{
 struct service_context *s=opaque;
 if(target==0x149aeu){
  struct biwn_text_bus bus={read8,read16,write32,s,20000u};
  struct biwn_text_args request;
  if(count!=8u||!args||!out)return 1;
  request=(struct biwn_text_args){(uint16_t)args[0],(uint16_t)args[1],args[2],args[3],args[4],args[5],(uint16_t)args[6],(uint16_t)args[7]};
  return biwn_text_draw(&bus,&request,out);
 }
 return s->outer->call(s->outer->context,target,args,count,out);
}
int biwn_coordinate_service_request(struct biwn_world_bus *bus,biwn_coordinate_write8 byte_write,
 const struct biwn_coordinate_request *request,uint32_t *out)
{
 struct service_context s;uint8_t byte=0;uint16_t word=0;uint32_t result;int status;
 if(!bus||!byte_write||!request||!out||!request->context||!request->sequence||
    !bus->read8||!bus->read16||!bus->read32||!bus->write16||!bus->write32||!bus->call)
  return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
 if(request->argument_count>1u||(request->kind!=BIWN_COORDINATE_CALL&&request->argument_count))
  return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
 s.outer=bus;s.inner=(struct biwn_world_bus){read8,read16,read32,write16,write32,call,&s,bus->poll_limit};
 result=request->incoming_d0;
 switch(request->kind){
 case BIWN_COORDINATE_READ8:
  status=bus->read8(bus->context,request->address,&byte);result=byte;break;
 case BIWN_COORDINATE_READ16:
  status=bus->read16(bus->context,request->address,&word);result=word;break;
 case BIWN_COORDINATE_READ32:
  status=bus->read32(bus->context,request->address,&result);break;
 case BIWN_COORDINATE_WRITE8:
  status=byte_write(bus->context,request->address,(uint8_t)request->value);result=0;break;
 case BIWN_COORDINATE_WRITE16:
  status=bus->write16(bus->context,request->address,(uint16_t)request->value);result=0;break;
 case BIWN_COORDINATE_WRITE32:
  status=bus->write32(bus->context,request->address,request->value);result=0;break;
 case BIWN_COORDINATE_CALL:
  switch(request->address){
  case 0x12620u:
   if(request->argument_count!=1u)return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
   status=biwn_panel_refresh(&s.inner,(uint16_t)request->argument,20000u,&result);break;
  case 0x1b718u:
   if(request->argument_count!=1u)return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
   result=biwn_button_digit(request->argument,result);status=0;break;
  case 0xe4c0u:
   if(request->argument_count)return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
   status=biwn_input_poll(&s.inner);break;
  case 0x20e8cu:
   if(request->argument_count)return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
   status=biwn_cleanup_reset_rooms(&s.inner,result,20000u,&result);break;
  case 0xdf22u:
   if(request->argument_count)return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
   status=biwn_task_pause_others(&s.inner,1024u,result,&result);break;
  case 0xdf3eu:
   if(request->argument_count)return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
   status=biwn_task_resume_others(&s.inner,1024u,result,&result);break;
  case 0xdf60u:
   if(request->argument_count)return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
   return BIWN_COORDINATE_SERVICE_EXTERNAL;
  case 0x20f78u:
   if(request->argument_count!=1u)return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
   return BIWN_COORDINATE_SERVICE_EXTERNAL;
  default:return BIWN_COORDINATE_SERVICE_EXTERNAL;
  }
  if(status)return BIWN_COORDINATE_SERVICE_BODY_ERROR;
  *out=result;return BIWN_COORDINATE_SERVICE_COMPLETED;
 default:return BIWN_COORDINATE_SERVICE_BAD_ARGUMENT;
 }
 if(status)return BIWN_COORDINATE_SERVICE_BUS_ERROR;
 *out=result;return BIWN_COORDINATE_SERVICE_COMPLETED;
}
