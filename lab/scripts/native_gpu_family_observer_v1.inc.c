/* Read-only eight-root return/context oracle. Mailbox peek is a plain GPU RAM read. */
struct mb_call{uint32_t task,sp,context,minimum,kind,args[5],ack;unsigned pending,native,helpers,wait_active,ack_seen;struct cpu incoming;};
static struct mb_call mb_calls[256];
static unsigned mb_slots,mb_pending;
static uint64_t mb_entries[8],mb_native[8],mb_returns[8],mb_old_steps,mb_source_steps,mb_errors,mb_context_errors,mb_helpers,mb_context_entries,mb_context_returns,mb_stack_outside,mb_stack_observations,mb_ack_checks;
static uint32_t mb_max_depth,mb_min_headroom=0xffffffffu;
static const uint32_t mb_original[8]={__ORIGINAL__},mb_end[8]={__ENDS__},mb_code[8]={__NATIVE__},mb_return[8]={__RETURNS__},mb_command[8]={__COMMANDS__},mb_args[8]={__ARGS__};
static const uint32_t mb_poll[16]={__POLLS__};
static uint32_t(*mb_gpu_read)(uint32_t,uint32_t);
void mb_set_gpu_reader(void*fn){mb_gpu_read=(uint32_t(*)(uint32_t,uint32_t))fn;}
static uint16_t mb_upper(const struct mb_call*call){uint16_t sr=(uint16_t)(call->incoming.sr&0xfff0u);return call->kind==3?(uint16_t)(sr&0xffefu):sr;}
static uint16_t mb_cmp_sr(const struct mb_call*call){uint32_t a=call->ack,b=mb_command[call->kind],v=a-b;return(uint16_t)(mb_upper(call)|(v?0u:4u)|((v&0x80000000u)?8u:0u)|((((a^b)&(a^v))&0x80000000u)?2u:0u)|(a<b?1u:0u));}
static void watch_mailbox(uint32_t pc){
 int entry=-1,native=-1,ret=-1,original_ret=-1;
 for(unsigned k=0;k<8;k++){if(pc==mb_original[k])entry=(int)k;if(pc==mb_code[k])native=(int)k;if(pc==mb_return[k])ret=(int)k;if(pc==mb_end[k]-2u)original_ret=(int)k;}
 if(!mb_pending&&entry<0&&!(pc>=__MB_START__&&pc<__MB_END__))return;
 uint32_t task=rd32(0xc0920u);struct cpu current;read_cpu(&current);struct mb_call*call=NULL;
 for(unsigned i=0;i<mb_slots;i++)if(mb_calls[i].task==task){call=&mb_calls[i];break;}
 if(entry>=0){
  if(!call){if(mb_slots==256){mb_errors++;return;}call=&mb_calls[mb_slots++];call->task=task;}
  if(call->pending){mb_errors++;return;}
  call->sp=current.r[15];call->context=task_arena_top(task)-124u;call->minimum=call->sp;call->kind=(unsigned)entry;call->native=call->helpers=call->wait_active=call->ack_seen=0;call->incoming=current;
  if(call->sp>0x1fffe8u||call->sp<96u){mb_errors++;return;}
  for(unsigned i=0;i<mb_args[entry];i++)call->args[i]=rd32(call->sp+4u+4u*i);
  call->pending=1;mb_pending++;mb_entries[entry]++;
 }
 for(unsigned k=0;k<8;k++)if(pc>mb_original[k]&&pc<mb_end[k])mb_old_steps++;
 if(pc>=__MB_START__&&pc<__MB_END__)mb_source_steps++;
 if(native>=0){
  if(!call||!call->pending)mb_errors++;
  else{if((unsigned)native!=call->kind)mb_errors++;call->native=1;arena_active[task_arena_slot(task)]=1;arena_used[task_arena_slot(task)]=1;mb_native[native]++;}
 }
 if(!call||!call->pending)return;
 for(unsigned i=0;i<16;i++)if(pc==mb_poll[i]){if(!mb_gpu_read){mb_errors++;return;}call->ack=mb_gpu_read(0xf03204u,0);call->ack_seen=1;mb_ack_checks++;}
 if(current.r[15]<call->minimum&&task_original_stack_valid(task,current.r[15]))call->minimum=current.r[15];
 if(call->native&&task_arena_stack_valid(task,current.r[15])){uint32_t depth=task_arena_top(task)-current.r[15];if(depth>arena_max_depth)arena_max_depth=depth;arena_stack_observations++;}
 if(!(current.sr&0x2000u)){uint32_t sp=current.r[15];mb_stack_observations++;if(!task_stack_valid(task,sp))mb_stack_outside++;else if(task_original_stack_valid(task,sp)&&sp-task-38u<mb_min_headroom)mb_min_headroom=sp-task-38u;}
 if(pc==__MB_BODY__){
  mb_context_entries++;uint32_t context=rd32(current.r[15]+4u);
  if(!call->native||context!=call->context)mb_context_errors++;
  else{for(unsigned i=0;i<16;i++)if(rd32(context+4u*i)!=call->incoming.r[i])mb_context_errors++;
   if(rd32(context+64u)!=(uint32_t)call->incoming.sr||rd32(context+68u)!=mb_original[call->kind])mb_context_errors++;}
 }
 if(pc==0xe0a4u||pc==0x162720u)call->wait_active=0;
 if(pc==0xe098u&&!call->wait_active){
  call->wait_active=1;mb_helpers++;
  if(call->helpers>=(call->kind==4?1u:2u))mb_errors++;
  for(unsigned i=0;i<15;i++){uint32_t want=call->incoming.r[i];if(call->helpers&&call->kind==3&&i==0)want=0x47bc8u;if(current.r[i]!=want)mb_errors++;}
  if(current.r[15]!=call->sp-4u)mb_errors++;
  if(!call->helpers){if(current.sr!=call->incoming.sr)mb_errors++;}
  else if(!call->ack_seen||current.sr!=mb_cmp_sr(call))mb_errors++;
  call->helpers++;
 }
 if(ret>=0||original_ret>=0){
  unsigned kind=(unsigned)(ret>=0?ret:original_ret);mb_returns[kind]++;
  if(kind!=call->kind||call->helpers!=(kind==4?1u:2u)||!call->ack_seen)mb_errors++;
  if(ret>=0&&!call->native)mb_errors++;
  for(unsigned i=0;i<16;i++){uint32_t want=call->incoming.r[i];if(kind==3&&i==0)want=0x47bc8u;if(current.r[i]!=want)mb_errors++;}
  uint16_t sr=kind==4?mb_cmp_sr(call):(uint16_t)(mb_upper(call)|4u);
  if(current.sr!=sr||current.usp!=call->incoming.usp||current.ssp!=call->incoming.ssp)mb_errors++;
  for(unsigned i=0;i<mb_args[kind];i++)if(rd32(call->sp+4u+4u*i)!=call->args[i])mb_errors++;
  if(call->native){mb_context_returns++;for(unsigned i=0;i<16;i++)if(rd32(call->context+4u*i)!=current.r[i])mb_context_errors++;
   if(rd32(call->context+64u)!=(uint32_t)current.sr||rd32(call->context+68u)!=mb_original[kind])mb_context_errors++;}
  if(call->sp-call->minimum>mb_max_depth)mb_max_depth=call->sp-call->minimum;
  if(call->native){arena_check_guards();arena_active[task_arena_slot(task)]=0;}
  call->pending=0;mb_pending--;
 }
}
static void mb_dump(FILE*file){
 const uint64_t*arrays[]={mb_entries,mb_native,mb_returns};const char*names[]={"mb_entries","mb_native","mb_returns"};
 for(unsigned j=0;j<3;j++){fprintf(file,",\"%s\":[",names[j]);for(unsigned k=0;k<8;k++)fprintf(file,"%s%llu",k?",":"",(unsigned long long)arrays[j][k]);fputc(']',file);}
 fprintf(file,",\"mb_old_steps\":%llu,\"mb_source_steps\":%llu,\"mb_errors\":%llu,\"mb_context_errors\":%llu,\"mb_helpers\":%llu,\"mb_context_entries\":%llu,\"mb_context_returns\":%llu,\"mb_pending\":%u,\"mb_stack_outside\":%llu,\"mb_stack_observations\":%llu,\"mb_max_depth\":%u,\"mb_min_headroom\":%u,\"mb_ack_checks\":%llu",(unsigned long long)mb_old_steps,(unsigned long long)mb_source_steps,(unsigned long long)mb_errors,(unsigned long long)mb_context_errors,(unsigned long long)mb_helpers,(unsigned long long)mb_context_entries,(unsigned long long)mb_context_returns,mb_pending,(unsigned long long)mb_stack_outside,(unsigned long long)mb_stack_observations,mb_max_depth,mb_min_headroom,(unsigned long long)mb_ack_checks);
}
