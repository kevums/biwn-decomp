#ifndef BIWN_MAILBOX_TASK
#define BIWN_MAILBOX_TASK() rd32(0xc0920u)
#endif
struct mb_call{uint32_t task,sp,context,minimum,kind,args[5];unsigned pending,native,helpers,wait_active;struct cpu incoming;};
static struct mb_call mb_calls[256];
static unsigned mb_slots,mb_pending;
static uint64_t mb_entries[2],mb_native[2],mb_returns[2],mb_old_steps,mb_source_steps,mb_errors,mb_context_errors,mb_helpers,mb_context_entries,mb_context_returns,mb_stack_outside,mb_stack_observations;
static uint32_t mb_max_depth,mb_min_headroom=0xffffffffu;
static void watch_mailbox(uint32_t pc){
 if(!mb_pending&&pc!=0xe220u&&pc!=0xe2b8u&&!(pc>=__MB_START__&&pc<__MB_END__))return;
 uint32_t task=BIWN_MAILBOX_TASK();struct cpu current;read_cpu(&current);struct mb_call*call=NULL;
 for(unsigned i=0;i<mb_slots;i++)if(mb_calls[i].task==task){call=&mb_calls[i];break;}
 if(pc==0xe220u||pc==0xe2b8u){
  if(!call){if(mb_slots==256){mb_errors++;return;}call=&mb_calls[mb_slots++];call->task=task;}
  if(call->pending){mb_errors++;return;}
  unsigned kind=pc==0xe220u?0u:1u;call->sp=current.r[15];call->context=call->sp-96u;call->minimum=call->sp;call->kind=kind;call->native=call->helpers=call->wait_active=0;call->incoming=current;
  if(call->sp>0x1fffe8u||call->sp<96u){mb_errors++;return;}
  for(unsigned i=0;i<(kind?3u:5u);i++)call->args[i]=rd32(call->sp+4u+4u*i);
  call->pending=1;mb_pending++;mb_entries[kind]++;
 }
 if((pc>0xe220u&&pc<0xe26cu)||(pc>0xe2b8u&&pc<0xe2f4u))mb_old_steps++;
 if(pc>=__MB_START__&&pc<__MB_END__)mb_source_steps++;
 if(pc==__MB_4320__||pc==__MB_4B00__){
  if(!call||!call->pending)mb_errors++;
  else{unsigned kind=pc==__MB_4320__?0u:1u;if(kind!=call->kind)mb_errors++;call->native=1;mb_native[kind]++;}
 }
 if(!call||!call->pending)return;
 if(current.r[15]<call->minimum)call->minimum=current.r[15];
 if(!(current.sr&0x2000u)){
  mb_stack_observations++;uint32_t sp=current.r[15];
  if(!task||task>0x1ffbfcu||sp<task+38u||sp>task+0x404u)mb_stack_outside++;
  else if(sp-task-38u<mb_min_headroom)mb_min_headroom=sp-task-38u;
 }
 if(pc==__MB_BODY__){
  mb_context_entries++;uint32_t context=rd32(current.r[15]+4u);
  if(!call->native||context!=call->context)mb_context_errors++;
  else{for(unsigned i=0;i<16;i++)if(rd32(context+4u*i)!=call->incoming.r[i])mb_context_errors++;
   if(rd32(context+64u)!=(uint32_t)call->incoming.sr||rd32(context+68u)!=(call->kind?0xe2b8u:0xe220u))mb_context_errors++;}
 }
 if(pc==0xe0a4u||pc==0x162720u)call->wait_active=0;
 if(pc==0xe098u&&!call->wait_active){
  call->wait_active=1;
  mb_helpers++;if(call->helpers>=2)mb_errors++;
  for(unsigned i=0;i<15;i++)if(current.r[i]!=call->incoming.r[i])mb_errors++;
  if(current.r[15]!=call->sp-4u)mb_errors++;
  if(!call->helpers){if(current.sr!=call->incoming.sr)mb_errors++;}
  else if((current.sr&0xfff0u)!=(call->incoming.sr&0xfff0u)||(current.sr&4u))mb_errors++;
  call->helpers++;
 }
 if(pc==__MB_RETURN_4320__||pc==__MB_RETURN_4B00__||pc==0xe26au||pc==0xe2f2u){
  unsigned kind=(pc==__MB_RETURN_4B00__||pc==0xe2f2u)?1u:0u;mb_returns[kind]++;
  if(kind!=call->kind||call->helpers!=2)mb_errors++;
  if((pc==__MB_RETURN_4320__||pc==__MB_RETURN_4B00__)&&!call->native)mb_errors++;
  for(unsigned i=0;i<16;i++)if(current.r[i]!=call->incoming.r[i])mb_errors++;
  if(current.sr!=((call->incoming.sr&0xfff0u)|4u)||current.usp!=call->incoming.usp||current.ssp!=call->incoming.ssp)mb_errors++;
  for(unsigned i=0;i<(kind?3u:5u);i++)if(rd32(call->sp+4u+4u*i)!=call->args[i])mb_errors++;
  if(call->native){mb_context_returns++;for(unsigned i=0;i<16;i++)if(rd32(call->context+4u*i)!=current.r[i])mb_context_errors++;
   if(rd32(call->context+64u)!=(uint32_t)current.sr||rd32(call->context+68u)!=(kind?0xe2b8u:0xe220u))mb_context_errors++;}
  if(call->sp-call->minimum>mb_max_depth)mb_max_depth=call->sp-call->minimum;
  call->pending=0;mb_pending--;
 }
}
