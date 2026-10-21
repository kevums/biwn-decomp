#ifndef BIWN_DIRECTION_TASK
#define BIWN_DIRECTION_TASK() rd32(0xc0920u)
#endif
int biwn_direction_predict(const unsigned char *,const uint32_t *,uint16_t,uint32_t *,uint16_t *);
struct dir_call {uint32_t task,sp,context,min_sp;unsigned pending,native;struct cpu incoming;uint32_t expected[16];uint16_t expected_sr;unsigned char args[4];};
static struct dir_call dir_calls[256];
static unsigned dir_slots,dir_pending;
static uint64_t dir_entries,dir_native,dir_returns,dir_old_steps,dir_source_steps,dir_errors,dir_context_errors,dir_stack_outside,dir_stack_observations,dir_context_entries,dir_context_returns;
static uint32_t dir_max_depth,dir_min_headroom=0xffffffffu;
static uint32_t dir_u32(uint32_t address){return rd32(address);}
static void watch_direction(uint32_t pc){
 if(!dir_pending&&pc!=0x13440u&&!(pc>=__DIR_START__&&pc<__DIR_END__)&&!(pc>0x13440u&&pc<0x134dcu))return;
 uint32_t task=BIWN_DIRECTION_TASK();struct cpu current;read_cpu(&current);struct dir_call *call=NULL;
 for(unsigned i=0;i<dir_slots;i++)if(dir_calls[i].task==task){call=&dir_calls[i];break;}
 if(pc==0x13440u){
  if(!call){if(dir_slots==256){dir_errors++;return;}call=&dir_calls[dir_slots++];call->task=task;}
  if(call->pending){dir_errors++;return;}
  call->sp=current.r[15];call->incoming=current;call->min_sp=call->sp;call->context=call->sp-124u;call->native=0;
  if(call->sp>0x1ffff8u||biwn_direction_predict(ram,current.r,current.sr,call->expected,&call->expected_sr)){dir_errors++;return;}
  memcpy(call->args,ram+call->sp+4u,4);call->pending=1;dir_pending++;dir_entries++;
 }
 if(pc>0x13440u&&pc<0x134dcu)dir_old_steps++;
 if(pc>=__DIR_START__&&pc<__DIR_END__)dir_source_steps++;
 if(pc==__DIR_COMPILED__){dir_native++;if(!call||!call->pending)dir_errors++;else call->native=1;}
 if(!call||!call->pending)return;
 if(current.r[15]<call->min_sp)call->min_sp=current.r[15];
 if(!(current.sr&0x2000u)){
  dir_stack_observations++;uint32_t sp=current.r[15];
  if(!task||task>0x1ffbfcu||sp<task+38u||sp>task+0x404u)dir_stack_outside++;
  else if(sp-task-38u<dir_min_headroom)dir_min_headroom=sp-task-38u;
 }
 if(pc==__DIR_BODY__){
  dir_context_entries++;uint32_t context=rd32(current.r[15]+4u);
  if(!call->native||context!=call->context)dir_context_errors++;
  else{
   for(unsigned i=0;i<16;i++)if(dir_u32(context+4u*i)!=call->incoming.r[i])dir_context_errors++;
   if(rd32(context+64u)!=(uint32_t)call->incoming.sr||rd32(context+68u)!=0x13440u)dir_context_errors++;
  }
 }
 if(pc==__DIR_RETURN__||pc==0x134dau){
  dir_returns++;
  if(pc==__DIR_RETURN__&&!call->native)dir_errors++;
  for(unsigned i=0;i<16;i++)if(current.r[i]!=call->expected[i])dir_errors++;
  if(current.sr!=call->expected_sr||current.usp!=call->incoming.usp||current.ssp!=call->incoming.ssp||memcmp(ram+call->sp+4u,call->args,4))dir_errors++;
  if(call->native){
   dir_context_returns++;
   for(unsigned i=0;i<16;i++)if(rd32(call->context+4u*i)!=current.r[i])dir_context_errors++;
   if(rd32(call->context+64u)!=(uint32_t)current.sr||rd32(call->context+68u)!=0x13440u)dir_context_errors++;
  }
  if(call->sp-call->min_sp>dir_max_depth)dir_max_depth=call->sp-call->min_sp;
  call->pending=0;dir_pending--;
 }
}
