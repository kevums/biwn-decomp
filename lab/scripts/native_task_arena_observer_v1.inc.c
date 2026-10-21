/* Read-only task ownership, arena guards, and complete pool-initializer return. */
static unsigned arena_active[102],arena_used[102],arena_ready;
static uint32_t arena_max_depth;
static uint64_t arena_errors,arena_guard_checks,arena_stack_observations,arena_unused_checks,arena_code_checks;
static unsigned task_id_valid(uint32_t task){return task>=0xc0928u&&task<0xd9d28u&&((task-0xc0928u)&0x3ffu)==0;}
static unsigned task_arena_slot(uint32_t task){return task_id_valid(task)?(task-0xc0928u)/1024u:101u;}
static uint32_t task_arena_top(uint32_t task){return __ARENA__+task_arena_slot(task)*256u+240u;}
static unsigned task_original_stack_valid(uint32_t task,uint32_t sp){return task_id_valid(task)&&sp>=task+38u&&sp<=task+0x400u;}
static unsigned task_arena_stack_valid(uint32_t task,uint32_t sp){uint32_t top=task_arena_top(task);return arena_active[task_arena_slot(task)]&&sp>=top-224u&&sp<=top;}
static unsigned task_stack_valid(uint32_t task,uint32_t sp){return task_original_stack_valid(task,sp)||task_arena_stack_valid(task,sp);}
static void arena_check_guards(void){
 if(!arena_ready){arena_errors++;return;}
 for(unsigned i=0;i<102;i++){uint32_t b=__ARENA__+i*256u;arena_guard_checks++;for(unsigned j=0;j<16;j++)if(ram[b+j]!=0xa5u||ram[b+240u+j]!=0xa5u)arena_errors++;}
}
static void arena_finish(void){
 arena_check_guards();arena_code_checks++;
 if(memcmp(ram+0x15edc0u,payload,__CODE_BYTES__))arena_errors++;
 for(unsigned i=0;i<102;i++){
  if(arena_active[i])arena_errors++;
  if(!arena_used[i]){arena_unused_checks++;uint32_t at=__ARENA__+i*256u;if(memcmp(ram+at,payload+at-0x15edc0u,256))arena_errors++;}
 }
}
static struct cpu pool_incoming;
static unsigned pool_pending;
static uint8_t pool_expected[0x19400];
static uint64_t pool_entries,pool_native_entries,pool_returns,pool_errors,pool_old_steps,pool_source_steps;
static void pool_put(unsigned at,uint32_t value,unsigned width){for(unsigned i=0;i<width;i++)pool_expected[at+i]=(uint8_t)(value>>(8u*(width-1u-i)));}
static void watch_pool_arena(uint32_t pc){
 if(pc==0x400au){arena_ready=1;arena_check_guards();}
 if(pc==0xdd40u){
  if(pool_pending)pool_errors++;pool_pending=1;pool_entries++;read_cpu(&pool_incoming);
  if(!(pool_incoming.sr&0x2000u))pool_errors++;
  memcpy(pool_expected,ram+0xc0928u,sizeof(pool_expected));
  for(unsigned i=1;i<=100;i++)pool_put(i*1024u,i==100?0:0xc0928u+(i+1u)*1024u,4);
  pool_put(0,0xc0928u,4);pool_put(4,0xc0928u,4);pool_put(8,0xddccu,4);pool_put(12,0xc0d28u,4);
  pool_put(20,0,2);pool_put(26,0,4);pool_put(22,0,4);pool_put(34,0,4);
 }
 if(pc==__POOL_ENTRY__)pool_native_entries++;
 if(pc>0xdd40u&&pc<0xddccu)pool_old_steps++;
 if(pc>=__POOL_START__&&pc<__POOL_END__)pool_source_steps++;
 if(pc==0xddccu&&pool_pending){
  struct cpu current;read_cpu(&current);pool_returns++;
  uint16_t sr=(uint16_t)(pool_incoming.sr&0xdff0u);
  for(unsigned i=0;i<16;i++){uint32_t want=pool_incoming.r[i];if(i==0)want=(want&0xffff0000u)|sr;else if(i==8)want=0xc0928u;else if(i==9||i==15)want=0xc0d28u;if(current.r[i]!=want)pool_errors++;}
  if(current.sr!=sr||current.usp!=0xc0d28u||current.ssp!=pool_incoming.ssp)pool_errors++;
  if(rd32(0x80)!=0xde08u||rd32(0x88)!=0xdeb6u||rd32(0x8c)!=0xdee2u||rd32(0x90)!=0xdef6u||rd32(0x20)!=0xddfeu||rd32(0xc0920u)!=0xc0928u||rd32(0xc0924u)!=0xc0d28u)pool_errors++;
  if(memcmp(ram+0xc0928u,pool_expected,sizeof(pool_expected)))pool_errors++;
  pool_pending=0;
 }
}
static void arena_dump(FILE *file){
 arena_finish();
 fprintf(file,",\"arena_errors\":%llu,\"arena_guard_checks\":%llu,\"arena_stack_observations\":%llu,\"arena_unused_checks\":%llu,\"arena_code_checks\":%llu,\"arena_max_depth\":%u",(unsigned long long)arena_errors,(unsigned long long)arena_guard_checks,(unsigned long long)arena_stack_observations,(unsigned long long)arena_unused_checks,(unsigned long long)arena_code_checks,arena_max_depth);
 fprintf(file,",\"pool_entries\":%llu,\"pool_native_entries\":%llu,\"pool_returns\":%llu,\"pool_errors\":%llu,\"pool_old_steps\":%llu,\"pool_source_steps\":%llu,\"pool_pending\":%u",(unsigned long long)pool_entries,(unsigned long long)pool_native_entries,(unsigned long long)pool_returns,(unsigned long long)pool_errors,(unsigned long long)pool_old_steps,(unsigned long long)pool_source_steps,pool_pending);
 fputs(",\"arena_used_slots\":[",file);unsigned comma=0;for(unsigned i=0;i<102;i++)if(arena_used[i]){fprintf(file,"%s%u",comma?",":"",i);comma=1;}fputc(']',file);
}
