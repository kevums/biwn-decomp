/* Read-only public-root, shared-context, virtual-C-boundary and task observer.
 * Algorithm outputs are independently checked by the finite native fixtures.
 * Per-task nested public roots are needed for the original movement control. */
#ifndef BIWN_ACTOR_CHAIN_TASK
#define BIWN_ACTOR_CHAIN_TASK() rd32(0xc0920u)
#endif
static void array(FILE *,const char *,const uint64_t *,unsigned);
static const uint32_t ach_original[3]={0x13c9au,0x13b5au,0x13bb0u};
static const uint32_t ach_original_return[3]={0x13f10u,0x13baeu,0x13c98u};
static const uint32_t ach_compiled[3]=__ACH_COMPILED__;
static const uint32_t ach_return[3]=__ACH_RETURN__;
static const uint32_t ach_save[3]={40u,8u,4u},ach_args[3]={8u,10u,10u};
static const uint32_t ach_saved_mask[3]={0x3cfcu,0x404u,0x400u};
static const uint32_t ach_helper_return[10]=__ACH_HELPER_RETURN__;
static const uint32_t ach_helper_target[10]=__ACH_HELPER_TARGET__;
static const uint32_t ach_targets[6]={0x13440u,0xe220u,0x1039cu,0x102c4u,0x1028eu,0x10652u};
struct ach_call{
 uint32_t task,sp,ret,min_sp,context,helper_sp,helper_ret,virtual_sp,virtual_d2,virtual_a2,virtual_kind;
 unsigned pending,native,kind,helper_pending,virtual_pending;
 unsigned char args[10],context_copy[80],virtual_args[10];
 struct cpu incoming;
};
static struct ach_call ach_calls[256];static unsigned ach_slots,ach_pending;
static uint64_t ach_entries[3],ach_native[3],ach_returns[3],ach_old_steps[3],ach_max_depth[3];
static uint64_t ach_min_headroom[3]={0xffffffffu,0xffffffffu,0xffffffffu};
static uint64_t ach_helper_counts[6],ach_virtual_entries[2],ach_virtual_returns[2];
static uint64_t ach_source_steps,ach_errors,ach_context_errors,ach_virtual_errors,ach_stack_outside,ach_stack_observations,ach_context_checks;
static struct ach_call *ach_active(uint32_t task){
 struct ach_call *result=NULL;
 for(unsigned i=0;i<ach_slots;i++)if(ach_calls[i].pending&&ach_calls[i].task==task&&(!result||ach_calls[i].sp<result->sp))result=&ach_calls[i];
 return result;
}
static void watch_actor_chain(uint32_t pc){
 int entering=-1;
 for(unsigned k=0;k<3;k++){
  if(pc==ach_original[k])entering=(int)k;
  uint32_t end=k==0?0x13f12u:k==1?0x13bb0u:0x13c9au;
  if(pc>ach_original[k]&&pc<end)ach_old_steps[k]++;
 }
 if(pc>=__ACH_START__&&pc<__ACH_END__)ach_source_steps++;
 if(!ach_pending&&entering<0)return;
 uint32_t task=BIWN_ACTOR_CHAIN_TASK();struct cpu current;read_cpu(&current);
 if(entering>=0){
  struct ach_call *slot=NULL;
  for(unsigned i=0;i<ach_slots;i++)if(!ach_calls[i].pending){slot=&ach_calls[i];break;}
  if(!slot){if(ach_slots==256){ach_errors++;return;}slot=&ach_calls[ach_slots++];}
  memset(slot,0,sizeof(*slot));slot->incoming=current;slot->task=task;slot->sp=current.r[15];slot->min_sp=slot->sp;slot->ret=rd32(slot->sp);slot->kind=(unsigned)entering;slot->context=slot->sp-ach_save[slot->kind]-320u;
  if(slot->sp>0x1ffff0u){ach_errors++;return;}
  memcpy(slot->args,ram+slot->sp+4u,ach_args[slot->kind]);slot->pending=1;ach_pending++;ach_entries[slot->kind]++;emit(pc);
 }
 struct ach_call *call=ach_active(task);
 if(!call)return;
 for(unsigned k=0;k<3;k++)if(pc==ach_compiled[k]){
  if(call->kind!=k)ach_errors++;
  call->native=1;ach_native[k]++;
 }
 for(unsigned i=0;i<ach_slots;i++){
  struct ach_call *slot=&ach_calls[i];
  if(!slot->pending||slot->task!=task)continue;
  if((current.sr&0x2000u)==(slot->incoming.sr&0x2000u)&&current.r[15]<slot->min_sp)slot->min_sp=current.r[15];
  if(!(current.sr&0x2000u)){
   uint32_t sp=current.r[15];ach_stack_observations++;
   if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)ach_stack_outside++;
   else if(sp-task-38u<ach_min_headroom[slot->kind])ach_min_headroom[slot->kind]=sp-task-38u;
  }
 }
 if(pc==__ACH_VIRTUAL_ENTRY__){
  uint32_t ctx=rd32(current.r[15]+4u),sp=rd32(ctx+60u),entry=rd32(ctx+72u),kind=entry==0x13b5au?0u:1u;
  if(!call->native||call->kind!=0||call->virtual_pending||call->helper_pending||ctx!=call->context||sp!=call->sp-54u||rd32(ctx+76u)!=0x13c9au||(entry!=0x13b5au&&entry!=0x13bb0u))ach_virtual_errors++;
  call->virtual_pending=1;call->virtual_sp=sp;call->virtual_d2=rd32(ctx+8u);call->virtual_a2=rd32(ctx+40u);call->virtual_kind=kind;
  if(sp>0x1ffff2u){ach_virtual_errors++;return;}
  memcpy(call->virtual_args,ram+sp+4u,10);ach_virtual_entries[kind]++;emit(pc);
 }
 if(pc==__ACH_VIRTUAL_RETURN__){
  uint32_t ctx=call->context,sp=call->virtual_sp;
  if(!call->virtual_pending||call->helper_pending||rd32(ctx+60u)!=sp||rd32(ctx+8u)!=call->virtual_d2||rd32(ctx+40u)!=call->virtual_a2||rd32(ctx+76u)!=0x13c9au||sp>0x1ffff2u||memcmp(ram+sp+4u,call->virtual_args,10))ach_virtual_errors++;
  ach_virtual_returns[call->virtual_kind]++;call->virtual_pending=0;emit(pc);
 }
 if(call->native){
  for(unsigned t=0;t<6;t++)if(pc==ach_targets[t]){
   uint32_t ret=rd32(current.r[15]);int capture=-1;
   for(unsigned i=0;i<10;i++)if(ach_helper_return[i]==ret)capture=(int)i;
   if(capture>=0){
    uint32_t ctx=call->context;
    if(call->helper_pending||ach_helper_target[capture]!=pc)ach_errors++;
    for(unsigned i=0;i<15;i++)if(rd32(ctx+4u*i)!=current.r[i])ach_context_errors++;
    if(rd32(ctx+60u)!=current.r[15]+4u||(rd32(ctx+64u)&0xffffu)!=current.sr||rd32(ctx+76u)!=ach_original[call->kind])ach_context_errors++;
    if(ctx>0x1fffb0u){ach_context_errors++;return;}
    memcpy(call->context_copy,ram+ctx,80);call->helper_sp=current.r[15];call->helper_ret=ret;call->helper_pending=1;ach_helper_counts[t]++;
   }
  }
  if(call->helper_pending&&pc==call->helper_ret){
   if(current.r[15]!=call->helper_sp+4u||memcmp(call->context_copy,ram+call->context,80))ach_context_errors++;
   ach_context_checks++;call->helper_pending=0;
  }
 }
 if(pc==ach_return[call->kind]||pc==ach_original_return[call->kind]){
  if(call->helper_pending||call->virtual_pending||current.r[15]!=call->sp||rd32(call->sp)!=call->ret||memcmp(ram+call->sp+4u,call->args,ach_args[call->kind]))ach_errors++;
  for(unsigned i=0;i<15;i++)if((ach_saved_mask[call->kind]&(1u<<i))&&current.r[i]!=call->incoming.r[i])ach_errors++;
  uint32_t depth=call->sp-call->min_sp;if(depth>ach_max_depth[call->kind])ach_max_depth[call->kind]=depth;
  ach_returns[call->kind]++;call->pending=0;ach_pending--;emit(pc);
 }
}
static void ach_dump(FILE *file){
 array(file,"ach_entries",ach_entries,3);array(file,"ach_native",ach_native,3);array(file,"ach_returns",ach_returns,3);array(file,"ach_old_steps",ach_old_steps,3);
 array(file,"ach_max_depth",ach_max_depth,3);array(file,"ach_min_headroom",ach_min_headroom,3);array(file,"ach_helper_counts",ach_helper_counts,6);array(file,"ach_virtual_entries",ach_virtual_entries,2);array(file,"ach_virtual_returns",ach_virtual_returns,2);
 fprintf(file,",\"ach_pending\":%u,\"ach_source_steps\":%llu,\"ach_errors\":%llu,\"ach_context_errors\":%llu,\"ach_virtual_errors\":%llu,\"ach_stack_outside\":%llu,\"ach_stack_observations\":%llu,\"ach_context_checks\":%llu",ach_pending,(unsigned long long)ach_source_steps,(unsigned long long)ach_errors,(unsigned long long)ach_context_errors,(unsigned long long)ach_virtual_errors,(unsigned long long)ach_stack_outside,(unsigned long long)ach_stack_observations,(unsigned long long)ach_context_checks);
}
