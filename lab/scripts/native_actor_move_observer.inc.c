/*13C9A read-only root/capture/helper/task monitor. Algorithm equivalence is
 * checked separately. r15 is original workingSP; the saved context is below it. */
#ifndef BIWN_ACTOR_MOVE_TASK
#define BIWN_ACTOR_MOVE_TASK() rd32(0xc0920u)
#endif
struct am_call {uint32_t task,sp,ret,args[2],min_sp,helper;unsigned pending,native,helper_pending;uint32_t context[18];struct cpu incoming;};
static struct am_call am_calls[256];static unsigned am_slots,am_pending;
static uint64_t am_entries,am_native_entries,am_returns,am_old_steps,am_native_steps,am_errors,am_helper_entries,am_helper_returns,am_context_checks,am_context_corruptions,am_stack_observations,am_stack_outside,am_direction_calls,am_submit_calls,am_outdoor_calls,am_indoor_calls;
static uint32_t am_max_depth,am_min_headroom=0xffffffffu;
static uint32_t am_arg_bytes(uint32_t target){return target==0x13440u?4u:target==0xe220u?20u:10u;}
static void watch_actor_move(uint32_t pc){
 if(pc==__AM_ENTRY__)am_native_entries++;
 if(pc>0x13c9au&&pc<0x13f12u)am_old_steps++;
 if(pc>=__AM_START__&&pc<__AM_END__)am_native_steps++;
 if(!am_pending&&pc!=0x13c9au)return;
 uint32_t task=BIWN_ACTOR_MOVE_TASK();struct am_call *call=NULL;struct cpu current;
 for(unsigned i=0;i<am_slots;i++)if(am_calls[i].task==task){call=&am_calls[i];break;}
 if(pc==0x13c9au){
  if(!call){if(am_slots==256){am_errors++;return;}call=&am_calls[am_slots++];call->task=task;}
  if(call->pending)am_errors++;
  read_cpu(&call->incoming);call->sp=call->incoming.r[15];call->ret=rd32(call->sp);call->min_sp=call->sp;call->args[0]=rd32(call->sp+4);call->args[1]=rd32(call->sp+8);call->helper=0;call->pending=1;call->native=call->helper_pending=0;am_pending++;am_entries++;emit(pc);
 }
 if(!call||!call->pending)return;
 if(pc==__AM_ENTRY__)call->native=1;
 read_cpu(&current);
 if(!(current.sr&0x2000u)){
  uint32_t sp=current.r[15];am_stack_observations++;
  if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)am_stack_outside++;
  else if(sp-task-38u<am_min_headroom)am_min_headroom=sp-task-38u;
  if(sp<call->min_sp)call->min_sp=sp;
 }
 if(pc==0x13440u||pc==0xe220u||pc==0x13b5au||pc==0x13bb0u){
  if(call->helper_pending)am_errors++;call->helper_pending=1;call->helper=pc;am_helper_entries++;
  if(current.r[15]!=call->sp-40u-am_arg_bytes(pc)-4u)am_errors++;
  if(pc==0x13440u)am_direction_calls++;
  if(pc==0xe220u){am_submit_calls++;if(rd32(current.r[15]+4)!=call->args[0]+128u)am_errors++;}
  if(pc==0x13b5au){am_outdoor_calls++;if(rd32(current.r[15]+4)!=call->args[0])am_errors++;}
  if(pc==0x13bb0u){am_indoor_calls++;if(rd32(current.r[15]+4)!=call->args[0])am_errors++;}
  if(call->native){
   for(unsigned i=0;i<18;i++)call->context[i]=rd32(call->sp-488u+4u*i);
   for(unsigned i=0;i<15;i++)if(call->context[i]!=current.r[i])am_errors++;
   if(call->context[15]!=current.r[15]+4u||(call->context[16]&0xffffu)!=current.sr)am_errors++;
  }
 }
 if((call->helper==0x13440u&&(pc==__AM_DIRECTION_CHILD_RETURN__||pc==0x13cceu))||(call->helper==0xe220u&&(pc==__AM_SUBMIT_CHILD_RETURN__||pc==0x13d7au))||(call->helper==0x13b5au&&(pc==__AM_OUTDOOR_CHILD_RETURN__||pc==0x13e8au))||(call->helper==0x13bb0u&&(pc==__AM_INDOOR_CHILD_RETURN__||pc==0x13ee6u))){
  if(!call->helper_pending)am_errors++;
  if(call->native){am_context_checks++;for(unsigned i=0;i<18;i++)if(rd32(call->sp-488u+4u*i)!=call->context[i])am_context_corruptions++;}
  if(current.r[15]!=call->sp-40u-am_arg_bytes(call->helper))am_errors++;
  call->helper_pending=0;am_helper_returns++;
 }
 if(pc==__AM_RETURN__||pc==0x13f10u){
  if(call->helper_pending)am_errors++;
  const unsigned saved[]={2,3,4,5,6,7,10,11,12,13};for(unsigned i=0;i<10;i++)if(current.r[saved[i]]!=call->incoming.r[saved[i]])am_errors++;
  uint32_t s=call->sp;if(current.r[15]!=s||rd32(s)!=call->ret||rd32(s+4)!=call->args[0]||rd32(s+8)!=call->args[1])am_errors++;
  if(s-call->min_sp>am_max_depth)am_max_depth=s-call->min_sp;
  am_pending--;call->pending=0;am_returns++;emit(pc);
 }
}
