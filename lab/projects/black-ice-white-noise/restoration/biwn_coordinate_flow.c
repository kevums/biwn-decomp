/* Coordinator reconstruction: explicit continuation for every public effect.
 * Original arithmetic and access order match biwn_coordinate_entry.c; the
 * event protocol is a new host interface, not an original CPU ABI claim. */
#include "biwn_coordinate_flow.h"
#define MAGIC 0x43464c31u
enum phase { MODE,INITIAL_POINTER,INITIAL_WRITE,PANEL,RELEASE_HELD,
 RELEASE_POLLED,CLOCK_START,CLOCK_WAIT,KEY_HELD,KEY_POLLED,KEY_FRESH,DIGIT,
 DIGIT_POINTER,DIGIT_WRITE,ACCEPT_TEST,POSITION_X,POSITION_Z,POSITION_FLAG,
 AFTER_CLEANUP,AFTER_YIELD,AFTER_PAUSE,AFTER_SCENE,AFTER_RESUME,
 BACKSPACE_TEST,BACKSPACE_POINTER,BACKSPACE_WRITE,CANCEL_TEST };
static int32_t signed_word(uint16_t word)
{return word<32768u?(int32_t)word:(int32_t)word-65536;}
static int issue(struct biwn_coordinate_flow *s,uint32_t phase,uint32_t kind,
 uint32_t address,uint32_t value,uint32_t count,uint32_t argument)
{
 if(s->pending.sequence==UINT64_MAX){s->terminal=BIWN_COORDINATE_FLOW_ID_EXHAUSTED;return (int)s->terminal;}
 s->phase=phase;s->pending.sequence++;
 s->pending.kind=kind;s->pending.address=address;s->pending.value=value;
 s->pending.argument_count=count;s->pending.argument=argument;s->pending.incoming_d0=s->d0;
 return BIWN_COORDINATE_FLOW_REQUEST;
}
static int read_value(struct biwn_coordinate_flow *s,uint32_t phase,uint32_t kind,uint32_t address)
{return issue(s,phase,kind,address,0,0,0);}
static int write_value(struct biwn_coordinate_flow *s,uint32_t phase,uint32_t kind,uint32_t address,uint32_t value)
{return issue(s,phase,kind,address,value,0,0);}
static int helper(struct biwn_coordinate_flow *s,uint32_t phase,uint32_t address,uint32_t count,uint32_t argument)
{return issue(s,phase,BIWN_COORDINATE_CALL,address,0,count,argument);}
static int panel(struct biwn_coordinate_flow *s)
{return helper(s,PANEL,0x12620u,1,1);}
static int done(struct biwn_coordinate_flow *s)
{s->terminal=BIWN_COORDINATE_FLOW_DONE;return BIWN_COORDINATE_FLOW_DONE;}
int biwn_coordinate_flow_begin(struct biwn_coordinate_flow *s,uint64_t context,uint32_t incoming)
{
 struct biwn_coordinate_flow initial={0};
 if(!s||!context)return BIWN_COORDINATE_FLOW_BAD_ARGUMENT;
 initial.magic=MAGIC;initial.pending.context=context;initial.d0=incoming;initial.cursor=1;
 *s=initial;return read_value(s,MODE,BIWN_COORDINATE_READ16,0x49c60u);
}
static int accept(struct biwn_coordinate_flow *s,uint32_t value)
{
 const uint32_t offsets[7]={0,1,2,3,5,6,7};
 int32_t divided;
 switch(s->phase){
 case MODE:
  if((uint16_t)value!=1u)return done(s);
  return read_value(s,INITIAL_POINTER,BIWN_COORDINATE_READ32,0x40ffcu);
 case INITIAL_POINTER:
  return write_value(s,INITIAL_WRITE,BIWN_COORDINATE_WRITE8,
   value+offsets[s->initial_index],s->initial_index?0x5fu:0x20u);
 case INITIAL_WRITE:
  if(++s->initial_index<7u)return read_value(s,INITIAL_POINTER,BIWN_COORDINATE_READ32,0x40ffcu);
  return panel(s);
 case PANEL:
  s->d0=value;return read_value(s,RELEASE_HELD,BIWN_COORDINATE_READ32,0x49ba4u);
 case RELEASE_HELD:
  if(value)return helper(s,RELEASE_POLLED,0xe4c0u,0,0);
  return read_value(s,CLOCK_START,BIWN_COORDINATE_READ32,0x778ccu);
 case RELEASE_POLLED:
  s->d0=value;return read_value(s,RELEASE_HELD,BIWN_COORDINATE_READ32,0x49ba4u);
 case CLOCK_START:
  s->deadline=value+75u;s->d0=s->deadline;
  return read_value(s,CLOCK_WAIT,BIWN_COORDINATE_READ32,0x778ccu);
 case CLOCK_WAIT:
  if(s->deadline>value)return read_value(s,CLOCK_WAIT,BIWN_COORDINATE_READ32,0x778ccu);
  return read_value(s,KEY_HELD,BIWN_COORDINATE_READ32,0x49ba4u);
 case KEY_HELD:
  if(!value)return helper(s,KEY_POLLED,0xe4c0u,0,0);
  return read_value(s,KEY_FRESH,BIWN_COORDINATE_READ32,0x49ba4u);
 case KEY_POLLED:
  s->d0=value;return read_value(s,KEY_HELD,BIWN_COORDINATE_READ32,0x49ba4u);
 case KEY_FRESH:
  return helper(s,DIGIT,0x1b718u,1,value);
 case DIGIT:
  s->d0=value;s->digit=(uint16_t)value;
  if(!(s->digit&0x8000u)){
   if(s->cursor<=7u)return read_value(s,DIGIT_POINTER,BIWN_COORDINATE_READ32,0x40ffcu);
   return panel(s);
  }
  return read_value(s,ACCEPT_TEST,BIWN_COORDINATE_READ8,0x49ba4u);
 case DIGIT_POINTER:
  return write_value(s,DIGIT_WRITE,BIWN_COORDINATE_WRITE8,value+s->cursor,(uint8_t)(s->digit+0x30u));
 case DIGIT_WRITE:
  s->d0=(s->d0&0xffff0000u)|(uint16_t)((uint32_t)(s->cursor<=3u?s->x:s->z)*10u);
  if(s->cursor<=3u)s->x=(uint16_t)(s->d0+s->digit);
  else s->z=(uint16_t)(s->d0+s->digit);
  s->cursor++;if(s->cursor==4u)s->cursor=5u;
  return panel(s);
 case ACCEPT_TEST:
  if(((uint8_t)value&0x20u)&&s->cursor==8u&&signed_word(s->x)<=966&&
     signed_word(s->z)<=719&&signed_word(s->x)>31&&signed_word(s->z)>31)
   return write_value(s,POSITION_X,BIWN_COORDINATE_WRITE32,0x49c50u,((uint32_t)signed_word(s->x)<<6)|0x20u);
  return read_value(s,BACKSPACE_TEST,BIWN_COORDINATE_READ8,0x49ba4u);
 case POSITION_X:
  return write_value(s,POSITION_Z,BIWN_COORDINATE_WRITE32,0x49c56u,((uint32_t)signed_word(s->z)<<6)|0x20u);
 case POSITION_Z:
  return write_value(s,POSITION_FLAG,BIWN_COORDINATE_WRITE16,0x45d98u,1);
 case POSITION_FLAG:
  s->d0=(uint32_t)signed_word(s->z)<<6;return helper(s,AFTER_CLEANUP,0x20e8cu,0,0);
 case AFTER_CLEANUP:
  s->d0=value;return helper(s,AFTER_YIELD,0xdf60u,0,0);
 case AFTER_YIELD:
  s->d0=value;return helper(s,AFTER_PAUSE,0xdf22u,0,0);
 case AFTER_PAUSE:
  s->d0=value;return helper(s,AFTER_SCENE,0x20f78u,1,1);
 case AFTER_SCENE:
  s->d0=value;return helper(s,AFTER_RESUME,0xdf3eu,0,0);
 case AFTER_RESUME:
  s->d0=value;return done(s);
 case BACKSPACE_TEST:
  if((uint8_t)value&2u){
   if(s->cursor>1u)s->cursor--;
   if(s->cursor==4u)s->cursor=3u;
   return read_value(s,BACKSPACE_POINTER,BIWN_COORDINATE_READ32,0x40ffcu);
  }
  return read_value(s,CANCEL_TEST,BIWN_COORDINATE_READ8,0x49ba6u);
 case BACKSPACE_POINTER:
  return write_value(s,BACKSPACE_WRITE,BIWN_COORDINATE_WRITE8,value+s->cursor,0x5fu);
 case BACKSPACE_WRITE:
  divided=signed_word(s->cursor<=3u?s->x:s->z);
  s->d0=(uint16_t)(divided/10-(divided<0));
  if(s->cursor<=3u)s->x=(uint16_t)(divided/10);else s->z=(uint16_t)(divided/10);
  return read_value(s,CANCEL_TEST,BIWN_COORDINATE_READ8,0x49ba6u);
 case CANCEL_TEST:
  if((uint8_t)value&0x20u)return done(s);
  return panel(s);
 default:s->terminal=BIWN_COORDINATE_FLOW_BAD_ARGUMENT;return (int)s->terminal;
 }
}
int biwn_coordinate_flow_advance(struct biwn_coordinate_flow *s,
 const struct biwn_coordinate_completion *reply,struct biwn_coordinate_request *request)
{
 int status;
 if(!s||!request||s->magic!=MAGIC)return BIWN_COORDINATE_FLOW_BAD_ARGUMENT;
 if(s->terminal)return (int)s->terminal;
 if(!reply){*request=s->pending;return BIWN_COORDINATE_FLOW_REQUEST;}
 if(reply->context!=s->pending.context||reply->sequence!=s->pending.sequence)
  return BIWN_COORDINATE_FLOW_BAD_REPLY;
 if(reply->status){s->callback_status=(uint32_t)reply->status;s->terminal=BIWN_COORDINATE_FLOW_FAILED;return (int)s->terminal;}
 status=accept(s,reply->value);
 if(status==BIWN_COORDINATE_FLOW_REQUEST)*request=s->pending;
 return status;
}
int biwn_coordinate_flow_result(const struct biwn_coordinate_flow *s,uint32_t *out)
{
 if(!s||!out||s->magic!=MAGIC)return BIWN_COORDINATE_FLOW_BAD_ARGUMENT;
 if(s->terminal==BIWN_COORDINATE_FLOW_DONE)*out=s->d0;
 return (int)s->terminal;
}
