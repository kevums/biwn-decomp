/* Read-only resource/GPU scratch lifetime and input-call commitments.
 * Context/shadow arrays below are observer-owned, never guest memory. */
static unsigned r39_live,i39_live,r39_helpers_live;
static unsigned r39_mode[102],r39_helper[102],i39_pending[102],i39_route[102];
static struct cpu r39_incoming[102],i39_incoming[102];
static uint32_t r39_word[102],r39_low[102],r39_high[102],i39_entry_sp[102];
static uint8_t r39_shadow[102][224];
static uint64_t r39_public,r39_entries,r39_returns,r39_errors,r39_alias_errors,r39_C_outside,r39_C_observations,r39_guest_observations,r39_parked_checks,r39_helper_entries,r39_helper_returns;
static uint64_t i39_calls,i39_native,i39_original,i39_returns,i39_errors,i39_C_outside,i39_C_observations;
static uint32_t r39_C_low=240u,r39_guest_depth,i39_guest_depth;
static const uint32_t r39_GPU_entries[8]=R39_GPU_ENTRIES;
static const uint32_t r39_switches[4]=R39_SWITCHES;
static const uint32_t r39_helper_rets[4]=R39_HELPER_RETS;
static unsigned r39_pending_total(void){unsigned n=0;for(unsigned i=0;i<102;i++)n+=r39_mode[i]!=0;return n;}
static unsigned r39_helper_total(void){unsigned n=0;for(unsigned i=0;i<102;i++)n+=r39_helper[i]!=0;return n;}
static unsigned i39_pending_total(void){unsigned n=0;for(unsigned i=0;i<102;i++)n+=i39_pending[i]!=0;return n;}
static void r39_watch(uint32_t pc){
 if(!r39_live&&!i39_live&&pc!=0x1af04u&&pc!=0x1a266u&&pc!=R39_ENTRY)return;
 uint32_t task=rd32(0xc0920u);unsigned slot=task_arena_slot(task);struct cpu cpu;read_cpu(&cpu);
 uint32_t base=R39_GPU_ARENA+slot*256u,ctx=base+168u,sp=cpu.r[15];
 if(r39_helpers_live)for(unsigned i=0;i<102;i++)if(r39_helper[i]){
  if(r39_high[i]<=r39_low[i]||r39_high[i]-r39_low[i]>224u)r39_errors++;
  else{r39_parked_checks++;if(memcmp(ram+r39_low[i],r39_shadow[i],r39_high[i]-r39_low[i]))r39_errors++;}
 }
 for(unsigned k=0;k<8;k++)if(pc==r39_GPU_entries[k]&&r39_mode[slot]==1u){r39_alias_errors++;r39_errors++;}
 if(pc==0x1af04u){
  r39_public++;
  if(r39_mode[slot]){r39_alias_errors++;r39_errors++;}
  else{r39_live++;r39_mode[slot]=2u;r39_incoming[slot]=cpu;r39_word[slot]=rd32(sp);}
 }
 if(pc==R39_ENTRY){
  r39_entries++;
  if(r39_mode[slot]!=2u){r39_errors++;if(!r39_mode[slot])r39_live++;}
  if(arena_active[slot]){r39_alias_errors++;r39_errors++;}
  r39_mode[slot]=1u;arena_active[slot]=1u;arena_used[slot]=1u;
 }
 if(r39_mode[slot]==1u){
  if(!(cpu.sr&0x2000u)){
   if(sp>=base+16u&&sp<=base+240u){r39_C_observations++;if(sp-base<r39_C_low)r39_C_low=sp-base;}
   else if(task_id_valid(task)&&sp>=task+64u&&sp<=task+1024u){
    r39_guest_observations++;uint32_t initial=r39_incoming[slot].r[15];
    if(initial>=sp&&initial-sp>r39_guest_depth)r39_guest_depth=initial-sp;
   }else r39_C_outside++;
  }
  for(unsigned k=0;k<4;k++)if(pc==r39_switches[k]){
   if(r39_helper[slot]||cpu.r[8]!=ctx||sp<base+16u||sp>ctx||rd32(ctx+68u)!=sp||rd32(ctx+60u)!=r39_incoming[slot].r[15])r39_errors++;
   else{r39_helper[slot]=k+1u;r39_low[slot]=sp;r39_high[slot]=ctx+72u;memcpy(r39_shadow[slot],ram+sp,ctx+72u-sp);r39_helper_entries++;r39_helpers_live++;}
  }
  for(unsigned k=0;k<4;k++)if(pc==r39_helper_rets[k]){
   if(r39_helper[slot]!=k+1u)r39_errors++;else{static const unsigned bytes[4]={4,4,4,20};if(sp!=r39_incoming[slot].r[15]-24u-bytes[k])r39_errors++;r39_helper[slot]=0;r39_helper_returns++;r39_helpers_live--;}
  }
  if(pc==R39_RETURN){
   static const unsigned saved[6]={2,3,4,5,10,11};
   for(unsigned i=0;i<6;i++)if(cpu.r[saved[i]]!=r39_incoming[slot].r[saved[i]])r39_errors++;
   for(unsigned i=0;i<15;i++){
    unsigned guest_saved=0;for(unsigned j=0;j<6;j++)guest_saved|=i==saved[j];
    if(!guest_saved&&cpu.r[i]!=rd32(ctx+4u*i))r39_errors++;
   }
   if(sp!=r39_incoming[slot].r[15]||rd32(sp)!=r39_word[slot]||rd32(ctx+60u)!=sp||cpu.sr!=rd16(ctx+66u)||r39_helper[slot])r39_errors++;
   r39_returns++;r39_mode[slot]=0;r39_live--;arena_active[slot]=0;arena_check_guards();
  }
 }
 if(pc==0x1a266u){
  if(i39_pending[slot])i39_errors++;else i39_live++;
  i39_pending[slot]=1;i39_route[slot]=0;i39_incoming[slot]=cpu;i39_entry_sp[slot]=sp-4u;i39_calls++;
 }
 if(i39_pending[slot]){
  if(pc==I39_ADMISSION&&(sp!=i39_entry_sp[slot]||rd32(sp)!=0x1a26cu))i39_errors++;
  if(pc==I39_NATIVE_ENTRY){if(i39_route[slot])i39_errors++;i39_route[slot]=1;i39_native++;}
  if(pc==0x191f4u){if(i39_route[slot])i39_errors++;i39_route[slot]=2;i39_original++;}
  if(i39_route[slot]==1u&&pc>=I39_CODE&&pc<I39_END){
   if((cpu.sr&0x2000u)||!task_id_valid(task)||sp<task+64u||sp>task+1024u)i39_C_outside++;
   else{i39_C_observations++;if(i39_entry_sp[slot]>=sp&&i39_entry_sp[slot]-sp>i39_guest_depth)i39_guest_depth=i39_entry_sp[slot]-sp;}
  }
  if(pc==0x1a26cu){
   static const unsigned saved[11]={2,3,4,5,6,7,10,11,12,13,14};
   for(unsigned i=0;i<11;i++)if(cpu.r[saved[i]]!=i39_incoming[slot].r[saved[i]])i39_errors++;
   if(sp!=i39_incoming[slot].r[15]||!i39_route[slot])i39_errors++;
   i39_returns++;i39_pending[slot]=0;i39_live--;
  }
 }
}
int resource_input_dump(const char *path){
 FILE *file=fopen(path,"w");if(!file)return 1;
 fprintf(file,"{\"resource_public\":%llu,\"resource_native_entries\":%llu,\"resource_returns\":%llu,\"resource_errors\":%llu,\"resource_alias_errors\":%llu,\"resource_C_outside\":%llu,\"resource_pending\":%u,\"resource_helper_pending\":%u,\"resource_helper_entries\":%llu,\"resource_helper_returns\":%llu,\"resource_parked_checks\":%llu,\"resource_C_observations\":%llu,\"resource_C_low\":%u,\"resource_guest_depth\":%u,\"input_calls\":%llu,\"input_native\":%llu,\"input_original\":%llu,\"input_returns\":%llu,\"input_errors\":%llu,\"input_C_outside\":%llu,\"input_pending\":%u,\"input_C_observations\":%llu,\"input_guest_depth\":%u}\n",
 (unsigned long long)r39_public,(unsigned long long)r39_entries,(unsigned long long)r39_returns,(unsigned long long)r39_errors,(unsigned long long)r39_alias_errors,(unsigned long long)r39_C_outside,r39_pending_total(),r39_helper_total(),(unsigned long long)r39_helper_entries,(unsigned long long)r39_helper_returns,(unsigned long long)r39_parked_checks,(unsigned long long)r39_C_observations,r39_C_low,r39_guest_depth,(unsigned long long)i39_calls,(unsigned long long)i39_native,(unsigned long long)i39_original,(unsigned long long)i39_returns,(unsigned long long)i39_errors,(unsigned long long)i39_C_outside,i39_pending_total(),(unsigned long long)i39_C_observations,i39_guest_depth);
 fclose(file);return 0;
}
