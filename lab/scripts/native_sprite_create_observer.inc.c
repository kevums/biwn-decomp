/*137E0root/capture/helper/context/task-stack monitor. Read-only; actual sprite
 * algorithm equivalence is a separate full-CPU/ordered-memory fixture proof. */
#ifndef BIWN_SPRITE_CREATE_TASK
#define BIWN_SPRITE_CREATE_TASK() rd32(0xc0920u)
#endif
struct sc_call {uint32_t task,sp,ret,args[5],object,min_sp,helper,allocation_arg;unsigned pending,native,helper_pending;uint32_t context[19];struct cpu incoming;};
static struct sc_call sc_calls[256];static unsigned sc_slots,sc_pending;
static uint64_t sc_entries,sc_native_entries,sc_returns,sc_old_steps,sc_native_steps,sc_errors,sc_helper_entries,sc_helper_returns,sc_context_checks,sc_context_corruptions,sc_stack_observations,sc_stack_outside,sc_position_calls,sc_allocate_calls,sc_decode_calls;
static uint32_t sc_max_depth,sc_min_headroom=0xffffffffu;
static void watch_sprite_create(uint32_t pc){
 if(pc==__SC_ENTRY__)sc_native_entries++;
 if(pc>0x137e0u&&pc<0x13ae0u)sc_old_steps++;
 if(pc>=__SC_START__&&pc<__SC_END__)sc_native_steps++;
 if(!sc_pending&&pc!=0x137e0u)return;
 uint32_t task=BIWN_SPRITE_CREATE_TASK();struct sc_call *call=NULL;struct cpu current;
 for(unsigned i=0;i<sc_slots;i++)if(sc_calls[i].task==task){call=&sc_calls[i];break;}
 if(pc==0x137e0u){
  if(!call){if(sc_slots==256){sc_errors++;return;}call=&sc_calls[sc_slots++];call->task=task;}
  if(call->pending)sc_errors++;
  read_cpu(&call->incoming);call->sp=call->incoming.r[15];call->ret=rd32(call->sp);call->min_sp=call->sp;
  uint32_t s=call->sp;call->args[0]=rd16(s+4);call->args[1]=rd32(s+6);call->args[2]=rd16(s+10);call->args[3]=rd32(s+12);call->args[4]=rd16(s+16);
  call->object=0;for(unsigned i=0;i<40;i++)if(!rd16(0x4bd9cu+i*30u)){call->object=0x4bd9cu+i*30u;break;}
  call->pending=1;call->native=call->helper_pending=0;call->allocation_arg=0;sc_pending++;sc_entries++;emit(pc);
 }
 if(!call||!call->pending)return;
 if(pc==__SC_ENTRY__)call->native=1;
 read_cpu(&current);
 if(!(current.sr&0x2000u)){
  uint32_t sp=current.r[15];sc_stack_observations++;
  if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)sc_stack_outside++;
  else if(sp-task-38u<sc_min_headroom)sc_min_headroom=sp-task-38u;
  if(sp<call->min_sp)call->min_sp=sp;
 }
 if(pc==0x105dau||pc==0x152a2u||pc==0xe2b8u){
  if(call->helper_pending)sc_errors++;call->helper_pending=1;call->helper=pc;sc_helper_entries++;
  uint32_t bytes=pc==0xe2b8u?16u:4u;
  if(current.r[15]!=call->sp-52u-bytes-4u)sc_errors++;
  if(pc==0x105dau){sc_position_calls++;if(!call->object||rd32(current.r[15]+4)!=call->object||current.r[11]+current.r[5]!=call->object)sc_errors++;}
  if(pc==0x152a2u){sc_allocate_calls++;call->allocation_arg=rd32(current.r[15]+4);if(call->allocation_arg!=current.r[9]+16u)sc_errors++;}
  if(pc==0xe2b8u){sc_decode_calls++;if(rd32(current.r[15]+4)!=0x6e6a0u||rd32(current.r[15]+8)!=current.r[9]||rd32(current.r[15]+12)!=current.r[7]||rd32(current.r[15]+16)!=call->allocation_arg)sc_errors++;}
  if(call->native){
   for(unsigned i=0;i<19;i++)call->context[i]=rd32(call->sp-500u+4u*i);
   for(unsigned i=0;i<15;i++)if(call->context[i]!=current.r[i])sc_errors++;
   if(call->context[15]!=call->sp||(call->context[16]&0xffffu)!=current.sr)sc_errors++;
  }
 }
 if((call->helper==0x105dau&&(pc==__SC_POSITION_CHILD_RETURN__||pc==0x13882u))||(call->helper==0x152a2u&&(pc==__SC_ALLOCATE_CHILD_RETURN__||pc==0x13a56u))||(call->helper==0xe2b8u&&(pc==__SC_DECODE_CHILD_RETURN__||pc==0x13ad4u))){
  if(!call->helper_pending)sc_errors++;
  if(call->native){sc_context_checks++;for(unsigned i=0;i<19;i++)if(rd32(call->sp-500u+4u*i)!=call->context[i])sc_context_corruptions++;}
  uint32_t bytes=call->helper==0xe2b8u?16u:4u;
  if(current.r[15]!=call->sp-52u-bytes)sc_errors++;
  call->helper_pending=0;sc_helper_returns++;
 }
 if(pc==__SC_RETURN__||pc==0x13adeu){
  if(call->helper_pending)sc_errors++;
  const unsigned saved[]={2,3,4,5,6,7,10,11,12,13,14};for(unsigned i=0;i<11;i++)if(current.r[saved[i]]!=call->incoming.r[saved[i]])sc_errors++;
  uint32_t s=call->sp;
  if(current.r[15]!=s||rd32(s)!=call->ret||rd16(s+4)!=call->args[0]||rd32(s+6)!=call->args[1]||rd16(s+10)!=call->args[2]||rd32(s+12)!=call->args[3]||rd16(s+16)!=call->args[4])sc_errors++;
  if(s-call->min_sp>sc_max_depth)sc_max_depth=s-call->min_sp;
  sc_pending--;call->pending=0;sc_returns++;emit(pc);
 }
}
