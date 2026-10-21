/* Read-only four-leaf navigation boundary/context/task observer.
 * Full algorithm equivalence remains the separate original-execution matrix. */
#ifndef BIWN_NAVIGATION_TASK
#define BIWN_NAVIGATION_TASK() rd32(0xc0920u)
#endif
static void array(FILE *,const char *,const uint64_t *,unsigned);
static const uint32_t an_original[4]={0xf368u,0x13f12u,0x13f7cu,0x13feau};
static const uint32_t an_original_end[4]={0xf4d8u,0x13f7cu,0x13feau,0x1404cu};
static const uint32_t an_original_returns[7]={0xf4d6u,0x13f58u,0x13f7au,0x13fc6u,0x13fe8u,0x14028u,0x1404au};
static const unsigned an_return_kind[7]={0,1,1,2,2,3,3};
static const uint32_t an_compiled[4]=__AN_COMPILED__;
static const uint32_t an_return[4]=__AN_RETURN__;
struct an_call{struct cpu incoming;uint32_t task,sp,ret,min_sp,context;unsigned char args[8];unsigned pending,native,kind,context_entered;};
static struct an_call an_calls[256];static unsigned an_slots,an_pending;
static uint64_t an_entries[4],an_native[4],an_returns[4],an_old_steps[4],an_max_depth[4];
static uint64_t an_min_headroom[4]={0xffffffffu,0xffffffffu,0xffffffffu,0xffffffffu};
static uint64_t an_errors,an_context_errors,an_context_entries,an_context_returns,an_stack_outside,an_stack_observations,an_source_steps;
static void watch_actor_navigation(uint32_t pc){
 int entering=-1;
 for(unsigned k=0;k<4;k++){if(pc==an_original[k])entering=(int)k;else if(pc>an_original[k]&&pc<an_original_end[k])an_old_steps[k]++;}
 if(pc>=__AN_START__&&pc<__AN_END__)an_source_steps++;
 if(!an_pending&&entering<0)return;
 struct cpu current;read_cpu(&current);uint32_t task=BIWN_NAVIGATION_TASK();struct an_call*call=NULL;
 for(unsigned i=0;i<an_slots;i++)if(an_calls[i].pending&&an_calls[i].task==task)call=&an_calls[i];
 if(entering>=0){
  if(call){an_errors++;return;}
  for(unsigned i=0;i<an_slots;i++)if(!an_calls[i].pending){call=&an_calls[i];break;}
  if(!call){if(an_slots==256){an_errors++;return;}call=&an_calls[an_slots++];}
  memset(call,0,sizeof(*call));call->incoming=current;call->task=task;call->sp=call->min_sp=current.r[15];call->kind=(unsigned)entering;call->context=call->sp-96u-(entering==0?8u:0u);
  if(call->sp>0x1ffff0u||call->sp<104u){an_errors++;return;}
  call->ret=rd32(call->sp);memcpy(call->args,ram+call->sp+4u,8);call->pending=1;an_pending++;an_entries[call->kind]++;
 }
 if(!call||!call->pending)return;
 unsigned k=call->kind;
 if(pc==an_compiled[k]){call->native=1;an_native[k]++;}
 if((current.sr&0x2000u)==(call->incoming.sr&0x2000u)&&current.r[15]<call->min_sp)call->min_sp=current.r[15];
 if(!(current.sr&0x2000u)){
  an_stack_observations++;uint32_t sp=current.r[15];
  if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)an_stack_outside++;
  else if(sp-task-38u<an_min_headroom[k])an_min_headroom[k]=sp-task-38u;
 }
 if(pc==__AN_BODY__){
  uint32_t ctx=call->context;if(!call->native||call->context_entered||ctx>0x1fffb8u||rd32(current.r[15]+4u)!=ctx){an_context_errors++;return;}
  for(unsigned i=0;i<15;i++)if(rd32(ctx+4u*i)!=call->incoming.r[i])an_context_errors++;
  if(rd32(ctx+60u)!=call->sp||(rd32(ctx+64u)&0xffffu)!=call->incoming.sr||rd32(ctx+68u)!=an_original[k])an_context_errors++;
  call->context_entered=1;an_context_entries++;
 }
 int returning=pc==an_return[k];
 for(unsigned i=0;i<7;i++)if(pc==an_original_returns[i]&&k==an_return_kind[i])returning=1;
 if(returning){
  if(current.r[15]!=call->sp||rd32(call->sp)!=call->ret||memcmp(ram+call->sp+4u,call->args,8))an_errors++;
  for(unsigned i=0;i<15;i++)if((0x7cfcu&(1u<<i))&&current.r[i]!=call->incoming.r[i])an_errors++;
  if(call->native){
   uint32_t ctx=call->context;if(!call->context_entered)an_context_errors++;
   for(unsigned i=0;i<15;i++)if(rd32(ctx+4u*i)!=current.r[i])an_context_errors++;
   if(rd32(ctx+60u)!=call->sp||(rd32(ctx+64u)&0xffffu)!=current.sr||rd32(ctx+68u)!=an_original[k])an_context_errors++;
   an_context_returns++;
  }
  uint32_t depth=call->sp-call->min_sp;if(depth>an_max_depth[k])an_max_depth[k]=depth;
  an_returns[k]++;call->pending=0;an_pending--;
 }
}
static void an_dump(FILE*f){
 array(f,"an_entries",an_entries,4);array(f,"an_native",an_native,4);array(f,"an_returns",an_returns,4);array(f,"an_old_steps",an_old_steps,4);array(f,"an_max_depth",an_max_depth,4);array(f,"an_min_headroom",an_min_headroom,4);
 fprintf(f,",\"an_pending\":%u,\"an_errors\":%llu,\"an_context_errors\":%llu,\"an_context_entries\":%llu,\"an_context_returns\":%llu,\"an_stack_outside\":%llu,\"an_stack_observations\":%llu,\"an_source_steps\":%llu",an_pending,(unsigned long long)an_errors,(unsigned long long)an_context_errors,(unsigned long long)an_context_entries,(unsigned long long)an_context_returns,(unsigned long long)an_stack_outside,(unsigned long long)an_stack_observations,(unsigned long long)an_source_steps);
}
