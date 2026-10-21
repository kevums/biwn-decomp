/* Coordinator bus adapter; original readable coordinate controls unchanged. */
#include "biwn_game_controls_coordinate_tasks.h"
#include "biwn_task_gates.h"
#include "biwn_transition_cleanup.h"
struct tasks_context {
 struct biwn_world_bus *outer,inner;
 biwn_input_write8 byte_write;
};
static int read8(void *opaque,uint32_t address,uint8_t *value)
{struct tasks_context *ctx=opaque;return ctx->outer->read8(ctx->outer->context,address,value);}
static int read16(void *opaque,uint32_t address,uint16_t *value)
{struct tasks_context *ctx=opaque;return ctx->outer->read16(ctx->outer->context,address,value);}
static int read32(void *opaque,uint32_t address,uint32_t *value)
{struct tasks_context *ctx=opaque;return ctx->outer->read32(ctx->outer->context,address,value);}
static int write8(void *opaque,uint32_t address,uint8_t value)
{struct tasks_context *ctx=opaque;return ctx->byte_write(ctx->outer->context,address,value);}
static int write16(void *opaque,uint32_t address,uint16_t value)
{struct tasks_context *ctx=opaque;return ctx->outer->write16(ctx->outer->context,address,value);}
static int write32(void *opaque,uint32_t address,uint32_t value)
{struct tasks_context *ctx=opaque;return ctx->outer->write32(ctx->outer->context,address,value);}
static int call(void *opaque,uint32_t target,const uint32_t *args,uint32_t count,uint32_t *out)
{
 struct tasks_context *ctx=opaque;
 if(target==0x20e8cu){
  if(count||!out)return BIWN_CLEANUP_BAD_ARGUMENT;
  return biwn_cleanup_reset_rooms(&ctx->inner,*out,20000u,out);
 }
 if(target==0xdf22u||target==0xdf3eu){
  if(count||!out)return BIWN_TASK_GATES_BAD_ARGUMENT;
  return target==0xdf22u ? biwn_task_pause_others(&ctx->inner,1024u,*out,out)
                         : biwn_task_resume_others(&ctx->inner,1024u,*out,out);
 }
 return ctx->outer->call(ctx->outer->context,target,args,count,out);
}
enum biwn_dispatch_status biwn_game_controls_coordinate_tasks_with_scratch(
 struct biwn_world_bus *bus,biwn_input_write8 byte_write,uint32_t scratch,
 uint32_t budget,uint32_t incoming,uint32_t *out)
{
 struct tasks_context ctx;
 if(!bus||!byte_write||!out||!scratch||!budget||!bus->read8||!bus->read16||
    !bus->read32||!bus->write16||!bus->write32||!bus->call)return BIWN_DISPATCH_BAD_ARGUMENT;
 ctx.outer=bus;ctx.byte_write=byte_write;
 ctx.inner=(struct biwn_world_bus){read8,read16,read32,write16,write32,call,&ctx,bus->poll_limit};
 return biwn_game_controls_coordinate_with_scratch(&ctx.inner,write8,scratch,budget,incoming,out);
}
