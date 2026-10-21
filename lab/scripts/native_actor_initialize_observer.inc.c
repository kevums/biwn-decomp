/* Original-facing134DC adapter and helper transparency, read-only.
 * Full algorithm/public-store equivalence is the separate component proof. */
#ifndef BIWN_ACTOR_INITIALIZE_TASK
#define BIWN_ACTOR_INITIALIZE_TASK() rd32(0xc0920u)
#endif
struct ai_call {uint32_t task,sp,ret,args[6],object,callback,min_sp,helper;unsigned pending,native,helper_pending;uint32_t context[19];struct cpu incoming;};
static struct ai_call ai_calls[256];static unsigned ai_slots,ai_pending;
static uint64_t ai_entries,ai_native_entries,ai_returns,ai_old_steps,ai_native_steps,ai_errors,ai_helper_entries,ai_helper_returns,ai_context_checks,ai_context_corruptions,ai_stack_observations,ai_stack_outside;
static uint32_t ai_max_depth,ai_min_headroom=0xffffffffu;
static uint32_t ai_sx(uint16_t x){return(uint32_t)(x&0x7fffu)-(uint32_t)(x&0x8000u);}
static uint32_t ai_callback(uint32_t target){switch(target){
case 0x13706:return 0xf4d8;case 0x13714:return 0xedc4;case 0x13722:return 0xfcc2;case 0x13730:return 0x17f80;case 0x1373e:return 0x178e0;case 0x1374a:return 0xf720;case 0x13756:return 0x21d40;case 0x13762:return 0x15080;case 0x1376e:return 0x14fc0;case 0x1377a:return 0xf888;case 0x13786:return 0x15140;case 0x13792:return 0x14100;case 0x1379e:return 0x11f80;case 0x137aa:return 0x128a0;case 0x137b6:return 0x15a80;default:return 0;}}
static void watch_actor_initialize(uint32_t pc){
 if(pc==__AI_ENTRY__)ai_native_entries++;
 if(pc>0x134dcu&&pc<0x137e0u)ai_old_steps++;
 if(pc>=__AI_START__&&pc<__AI_END__)ai_native_steps++;
 if(!ai_pending&&pc!=0x134dcu)return;
 uint32_t task=BIWN_ACTOR_INITIALIZE_TASK();struct ai_call *call=NULL;struct cpu current;
 for(unsigned i=0;i<ai_slots;i++)if(ai_calls[i].task==task){call=&ai_calls[i];break;}
 if(pc==0x134dcu){
  if(!call){if(ai_slots==256){ai_errors++;return;}call=&ai_calls[ai_slots++];call->task=task;}
  if(call->pending)ai_errors++;
  read_cpu(&call->incoming);call->sp=call->incoming.r[15];call->ret=rd32(call->sp);call->min_sp=call->sp;
  uint32_t s=call->sp;call->args[0]=rd16(s+4);call->args[1]=rd16(s+6);call->args[2]=rd32(s+8);call->args[3]=rd16(s+12);call->args[4]=rd32(s+14);call->args[5]=rd16(s+18);
  call->object=0x49d6cu+206u*ai_sx((uint16_t)call->args[1]);call->callback=0;
  uint16_t index=(uint16_t)(call->args[0]-4u);
  if(index<=114u){uint16_t offset=(uint16_t)rd16(0x13620u+2u*index);call->callback=ai_callback(0x13620u+ai_sx(offset));}
  call->pending=1;call->native=call->helper_pending=0;ai_pending++;ai_entries++;emit(pc);
 }
 if(!call||!call->pending)return;
 if(pc==__AI_ENTRY__)call->native=1;
 read_cpu(&current);
 if(!(current.sr&0x2000u)){
  uint32_t sp=current.r[15];ai_stack_observations++;
  if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)ai_stack_outside++;
  else if(sp-task-38u<ai_min_headroom)ai_min_headroom=sp-task-38u;
  if(sp<call->min_sp)call->min_sp=sp;
 }
 if(pc==0x102c4u||pc==0x10520u||pc==0xdf6cu){
  if(call->helper_pending)ai_errors++;call->helper_pending=1;call->helper=pc;ai_helper_entries++;
  uint32_t bytes=pc==0xdf6cu?8u:4u;
  if(current.r[15]!=call->sp-32u-bytes-4u)ai_errors++;
  if(pc==0xdf6cu){
   uint32_t slot=ai_sx((uint16_t)call->args[1]);
   if(!call->callback||rd32(current.r[15]+4)!=call->callback||rd32(current.r[15]+8)!=slot||current.r[11]!=slot)ai_errors++;
   if((current.sr&31u)!=((slot==0?4u:0u)|((slot&0x80000000u)?8u:0u)))ai_errors++;
  }else if(rd32(current.r[15]+4)!=call->object||current.r[8]!=call->object)ai_errors++;
  if(call->native){
   for(unsigned i=0;i<19;i++)call->context[i]=rd32(call->sp-480u+4u*i);
   for(unsigned i=0;i<15;i++)if(call->context[i]!=current.r[i])ai_errors++;
   if(call->context[15]!=call->sp||(call->context[16]&0xffffu)!=current.sr)ai_errors++;
  }
 }
 if((call->helper==0x102c4u&&(pc==__AI_OUTSIDE_CHILD_RETURN__||pc==0x135f0u))||(call->helper==0x10520u&&(pc==__AI_INSIDE_CHILD_RETURN__||pc==0x13602u))||(call->helper==0xdf6cu&&(pc==__AI_TASK_CHILD_RETURN__||pc==0x137c6u))){
  if(!call->helper_pending)ai_errors++;
  if(call->native){ai_context_checks++;for(unsigned i=0;i<19;i++)if(rd32(call->sp-480u+4u*i)!=call->context[i])ai_context_corruptions++;}
  uint32_t bytes=call->helper==0xdf6cu?8u:4u;
  if(current.r[15]!=call->sp-32u-bytes)ai_errors++;
  call->helper_pending=0;ai_helper_returns++;
 }
 if(pc==__AI_RETURN__||pc==0x137deu){
  if(call->helper_pending)ai_errors++;
  const unsigned saved[]={2,3,4,5,6,7,10,11};for(unsigned i=0;i<8;i++)if(current.r[saved[i]]!=call->incoming.r[saved[i]])ai_errors++;
  uint32_t s=call->sp;
  if(current.r[15]!=s||rd32(s)!=call->ret||rd16(s+4)!=call->args[0]||rd16(s+6)!=call->args[1]||rd32(s+8)!=call->args[2]||rd16(s+12)!=call->args[3]||rd32(s+14)!=call->args[4]||rd16(s+18)!=call->args[5])ai_errors++;
  if(s-call->min_sp>ai_max_depth)ai_max_depth=s-call->min_sp;
  ai_pending--;call->pending=0;ai_returns++;emit(pc);
 }
}
