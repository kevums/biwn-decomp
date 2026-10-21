/* Coordinator variant: original readable controls plus real coordinate entry. */
#include "biwn_game_controls_coordinate.h"
#include "biwn_coordinate_entry.h"
#include "biwn_inventory_select.h"
#include "biwn_attack_effect.h"
#include "biwn_rng.h"
#include "biwn_camera.h"
#include "biwn_animation.h"
#include "biwn_memory.h"
#include "biwn_transition_cleanup.h"
#include "biwn_resources.h"
#include "biwn_elevator_input.h"
#include "biwn_elevator_display.h"
#include "biwn_elevator_formatter.h"
#include "biwn_panel_refresh.h"
#include "biwn_text.h"
#include "biwn_input_poll.h"

struct controls_context {
 struct biwn_world_bus *outer;
 struct biwn_world_bus inner;
 biwn_input_write8 byte_write;
 uint32_t animation_budget;
 uint32_t display_scratch;
};
static int read8(void *opaque,uint32_t address,uint8_t *value)
{
 struct controls_context *ctx=opaque;
 return ctx->outer->read8(ctx->outer->context,address,value);
}
static int read16(void *opaque,uint32_t address,uint16_t *value)
{
 struct controls_context *ctx=opaque;
 return ctx->outer->read16(ctx->outer->context,address,value);
}
static int read32(void *opaque,uint32_t address,uint32_t *value)
{
 struct controls_context *ctx=opaque;
 return ctx->outer->read32(ctx->outer->context,address,value);
}
static int write8(void *opaque,uint32_t address,uint8_t value)
{
 struct controls_context *ctx=opaque;
 return ctx->byte_write(ctx->outer->context,address,value);
}
static int write16(void *opaque,uint32_t address,uint16_t value)
{
 struct controls_context *ctx=opaque;
 return ctx->outer->write16(ctx->outer->context,address,value);
}
static int write32(void *opaque,uint32_t address,uint32_t value)
{
 struct controls_context *ctx=opaque;
 return ctx->outer->write32(ctx->outer->context,address,value);
}
static int call(void *opaque,uint32_t address,const uint32_t *args,
 uint32_t count,uint32_t *result)
{
 struct controls_context *ctx=opaque;
 uint32_t remainder;
 switch(address) {
 case 0x18e92u:
  if(count||!result)return BIWN_COORDINATE_BAD_ARGUMENT;
  return biwn_coordinate_entry_with_result(&ctx->inner,write8,100000u,*result,result);
 case 0x1b718u:
  if(count!=1u||!args||!result)return BIWN_COORDINATE_BAD_ARGUMENT;
  *result=biwn_button_digit(args[0],*result);return 0;
 case 0x20f0cu:
  if(count||!result)return BIWN_CLEANUP_BAD_ARGUMENT;
  return biwn_cleanup_reset_region(&ctx->inner,*result,20000u,result);
 case 0xe4c0u:
  if(count||!result)return BIWN_INPUT_BAD_ARGUMENT;
  /* The source saves/restores D0-D2. Polling does not replace incoming D0. */
  return biwn_input_poll(&ctx->inner);
 case 0x12620u:
  if(count!=1u||!args)return BIWN_PANEL_BAD_ARGUMENT;
  return biwn_panel_refresh(&ctx->inner,(uint16_t)args[0],20000u,result);
 case 0x149aeu: {
  struct biwn_text_bus text_bus={ctx->inner.read8,ctx->inner.read16,ctx->inner.write32,ctx->inner.context,20000u};
  struct biwn_text_args request;
  if(count!=8u||!args)return BIWN_TEXT_BAD_ARGUMENT;
  request=(struct biwn_text_args){(uint16_t)args[0],(uint16_t)args[1],args[2],args[3],args[4],args[5],(uint16_t)args[6],(uint16_t)args[7]};
  return biwn_text_draw(&text_bus,&request,result);
 }
 case 0x1b45au:
  if(!ctx->display_scratch)return ctx->outer->call(ctx->outer->context,address,args,count,result);
  if(count!=3u||!args||args[0]!=ctx->display_scratch)return BIWN_FORMATTER_CPU_BAD_ARGUMENT;
  return biwn_elevator_format(&ctx->inner,write8,args[0],args[1],(uint16_t)args[2],result);
 case 0x190bcu:
  if(!ctx->display_scratch)return ctx->outer->call(ctx->outer->context,address,args,count,result);
  if(count||!result)return BIWN_ELEVATOR_DISPLAY_BAD_ARGUMENT;
  return biwn_elevator_display(&ctx->inner,write8,ctx->display_scratch,1024u,*result,result);
 case 0x1a0f8u:
  if(count||!result)return BIWN_ELEVATOR_BAD_ARGUMENT;
  return biwn_elevator_input(&ctx->inner,*result,result);
 case 0x1af04u:
  if(count!=1u||!args)return BIWN_RESOURCE_BAD_ARGUMENT;
  return biwn_resource_get(&ctx->inner,(uint16_t)args[0],1024u,result);
 case 0x1b002u:
  if(count!=1u||!args)return BIWN_RESOURCE_BAD_ARGUMENT;
  return biwn_resource_release(&ctx->inner,(uint16_t)args[0],1024u,result);
 case 0x152a2u:
  if(count!=1u||!args)return BIWN_MEMORY_BAD_ARGUMENT;
  return biwn_memory_allocate(&ctx->inner,args[0],1024u,result);
 case 0x1545cu:
  if(count!=1u||!args||!result)return BIWN_CLEANUP_BAD_ARGUMENT;
  return biwn_cleanup_free_handle(&ctx->inner,args[0],*result,1024u,result);
 case 0x15200u:
  if(count)return BIWN_MEMORY_BAD_ARGUMENT;
  return biwn_memory_compact(&ctx->inner,1024u,result);
 case 0xe3e0u:case 0xe3eeu:
  if(count!=3u||!args||!result)return BIWN_MEMORY_BAD_ARGUMENT;
  return biwn_memory_copy(&ctx->inner,write8,address,args[0],args[1],args[2],*result,1024u,result);
 case 0xeb04u:
  if(count!=1u||!args||!result)return BIWN_ANIMATION_BAD_ARGUMENT;
  return biwn_animation_update(&ctx->inner,args[0],*result,ctx->animation_budget,result);
 case 0xeac4u:
  if(count!=4u||!args||!result)return BIWN_ANIMATION_BAD_ARGUMENT;
  return biwn_animation_enqueue(&ctx->inner,args[0],args[1],args[2],args[3],*result,result);
 case 0x18df2u:
  if(count)return BIWN_ATTACK_BAD_ARGUMENT;
  return biwn_attack_effect(&ctx->inner,result);
 case 0x1a77cu:
  if(count!=1u||!args)return BIWN_RNG_BAD_ARGUMENT;
  return biwn_rng_indexed(&ctx->inner,(uint16_t)args[0],result);
 case 0xe60au:
  if(count!=2u||!args)return BIWN_RNG_BAD_ARGUMENT;
  return biwn_rng_remainder(args[0],args[1],result);
 case 0xe588u:
  if(count!=2u||!args)return BIWN_RNG_BAD_ARGUMENT;
  return biwn_signed_division(args[0],args[1],result,&remainder);
 case 0xe540u:
  if(count!=2u||!args||!result)return BIWN_RNG_BAD_ARGUMENT;
  *result=biwn_multiply32(args[0],args[1]);return 0;
 default:return ctx->outer->call(ctx->outer->context,address,args,count,result);
 }
}
static enum biwn_dispatch_status run(struct biwn_world_bus *bus,
 biwn_input_write8 byte_write,uint32_t scratch,uint32_t budget,uint32_t incoming,uint32_t *result)
{
 struct controls_context ctx;
 if(!bus||!result||!byte_write||!bus->read8||!bus->read16||!bus->read32||
    !bus->write16||!bus->write32||!bus->call)return BIWN_DISPATCH_BAD_ARGUMENT;
 ctx.outer=bus;ctx.byte_write=byte_write;ctx.animation_budget=1024u;ctx.display_scratch=scratch;
 ctx.inner=(struct biwn_world_bus){read8,read16,read32,write16,write32,call,&ctx,bus->poll_limit};
 return biwn_input_dispatch(&ctx.inner,write8,budget,incoming,result);
}
enum biwn_dispatch_status biwn_game_controls_coordinate(struct biwn_world_bus *bus,
 biwn_input_write8 write_byte,uint32_t budget,uint32_t incoming,uint32_t *result)
{return run(bus,write_byte,0,budget,incoming,result);}
enum biwn_dispatch_status biwn_game_controls_coordinate_with_scratch(struct biwn_world_bus *bus,
 biwn_input_write8 write_byte,uint32_t scratch,uint32_t budget,uint32_t incoming,uint32_t *result)
{
 if(!scratch)return BIWN_DISPATCH_BAD_ARGUMENT;
 return run(bus,write_byte,scratch,budget,incoming,result);
}
