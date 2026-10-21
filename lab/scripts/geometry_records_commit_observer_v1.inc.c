/* R33_RECORDS_WATCH_BEGIN: read-only scene record/source/provider boundaries. */
static unsigned r33_pending[101],r33_provider[101];
static struct cpu r33_incoming[101];
static uint32_t r33_guest_sp[101];
static uint8_t r33_frame[101][118],r33_stack[101][208];
static uint64_t r33_entries,r33_returns,r33_errors,r33_original_steps,r33_protected;
static uint64_t r33_provider_entries[2],r33_provider_returns[2];
static unsigned r33_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=r33_pending[i]+r33_provider[i];return n;}
static void r33_read_logical(uint32_t f,struct cpu *cpu){
 for(unsigned i=0;i<16;i++)cpu->r[i]=rd32(f+4u+i*4u);
 cpu->pc=rd32(f+68u);cpu->usp=rd32(f+72u);cpu->ssp=rd32(f+76u);cpu->sr=rd16(f+80u);
}
static void r33_watch(uint32_t pc){
 if(pc!=R33_BEGIN&&pc!=R33_END&&pc!=R33_HELPER_RETURN&&pc!=0xe3e0u&&pc!=0xe220u&&!(pc>=0x170a0u&&pc<0x17326u))return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==R33_BEGIN||pc==R33_END)r33_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=R33_ARENA+delta,f=base+144u;
 if(pc==R33_BEGIN){
  r33_entries++;if(r33_pending[slot]||r33_provider[slot])r33_errors++;
  r33_pending[slot]=1;r33_read_logical(f,&r33_incoming[slot]);
  if(r33_incoming[slot].pc!=0x170a0u||rd32(f+114u)!=1u||rd32(f+94u))r33_errors++;
  if((r33_incoming[slot].sr&0x2000u?r33_incoming[slot].ssp:r33_incoming[slot].usp)!=r33_incoming[slot].r[15])r33_errors++;
 }
 if(!r33_pending[slot]){if(pc==R33_END)r33_errors++;return;}
 if(pc>=0x170a0u&&pc<0x17326u)r33_original_steps++;
 if(pc==0xe3e0u||pc==0xe220u){
  struct cpu physical;read_cpu(&physical);
  if(physical.r[15]==rd32(f+106u)&&rd32(physical.r[15])==R33_HELPER_RETURN){
   unsigned tag=pc==0xe3e0u?1u:2u;uint32_t logical_return=rd32(f+110u);
   if(r33_provider[slot]||rd32(f+102u)!=f+4u||rd32(f+68u)!=pc||rd32(f+64u)!=physical.r[15]||rd32(f+114u)!=1u||rd32(f+94u))r33_errors++;
   if(rd32(f+(rd16(f+80u)&0x2000u?76u:72u))!=physical.r[15])r33_errors++;
   if(tag==1u?(logical_return!=0x170d8u&&logical_return!=0x17166u):logical_return!=0x172c4u)r33_errors++;
   r33_provider[slot]=tag;r33_guest_sp[slot]=physical.r[15];r33_provider_entries[tag-1u]++;
   memcpy(r33_frame[slot],ram+f,118);memcpy(r33_stack[slot],ram+base+608u,208);
  }
 }
 if(pc==R33_HELPER_RETURN){
  unsigned tag=r33_provider[slot];struct cpu physical;read_cpu(&physical);
  if(!tag){r33_errors++;return;}
  if(physical.r[15]!=r33_guest_sp[slot]+4u||memcmp(r33_frame[slot],ram+f,118)||memcmp(r33_stack[slot],ram+base+608u,208))r33_errors++;
  r33_provider_returns[tag-1u]++;r33_protected++;r33_provider[slot]=0;
 }
 if(pc==R33_END){
  struct cpu current;r33_read_logical(f,&current);r33_returns++;
  if(r33_provider[slot]||current.pc!=0x17324u||rd32(f+114u)!=1u||rd32(f+94u)||current.r[15]!=r33_incoming[slot].r[15]||current.usp!=r33_incoming[slot].usp||current.ssp!=r33_incoming[slot].ssp)r33_errors++;
  if((current.sr&0xffe0u)!=(r33_incoming[slot].sr&0xffe0u))r33_errors++;
  for(unsigned i=0;i<16;i++)if(((i>=2&&i<=4)||(i>=10&&i<=13))&&current.r[i]!=r33_incoming[slot].r[i])r33_errors++;
  r33_pending[slot]=0;
 }
}
/* R33_RECORDS_WATCH_END */
int records_dump(const char *path){
 FILE *file=fopen(path,"w");if(!file)return 1;
 fprintf(file,"{\"entries\":%llu,\"returns\":%llu,\"errors\":%llu,\"pending\":%u,\"original_body_steps_while_native\":%llu,\"protected_provider_returns\":%llu,\"copy_entries\":%llu,\"copy_returns\":%llu,\"matrix_entries\":%llu,\"matrix_returns\":%llu}\n",(unsigned long long)r33_entries,(unsigned long long)r33_returns,(unsigned long long)r33_errors,r33_pending_total(),(unsigned long long)r33_original_steps,(unsigned long long)r33_protected,(unsigned long long)r33_provider_entries[0],(unsigned long long)r33_provider_returns[0],(unsigned long long)r33_provider_entries[1],(unsigned long long)r33_provider_returns[1]);
 return fclose(file)!=0;
}
