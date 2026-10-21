/* Read-only E220 call-site witness for original and compiled record builders. */
static unsigned mr_pending[101];
static uint32_t mr_sp[101],mr_sr[101];
static uint64_t mr_entries[2],mr_returns[2],mr_errors,mr_ignored;
static unsigned mr_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=mr_pending[i]!=0;return n;}
static void mr_watch(uint32_t pc){
 if(pc!=0xe220u&&pc!=0x172c4u&&pc!=MR_HELPER_RETURN)return;
 struct cpu cpu;read_cpu(&cpu);uint32_t task=rd32(0xc0920u),delta=task-0xc0928u,sp=cpu.r[15]&0xffffffu;
 unsigned valid=delta<0x19400u&&!(delta&1023u);unsigned slot=valid?delta/1024u:0;
 uint32_t f=MR_ARENA+delta+144u;
 if(pc==0xe220u){
  if(sp&1u||sp>0x1fffe8u){mr_errors++;return;}
  uint32_t ret=rd32(sp);unsigned kind=ret==0x172c4u?1u:0u;
  if(valid&&ret==MR_HELPER_RETURN&&rd32(f+110u)==0x172c4u){
   kind=2u;
   if(rd32(f+68u)!=0xe220u||rd32(f+114u)!=1u||rd32(f+94u)||rd32(f+106u)!=cpu.r[15]||rd32(f+102u)!=f+4u){mr_errors++;return;}
  }
  if(!kind){mr_ignored++;return;}
  if(!valid){mr_errors++;return;}
  if(mr_pending[slot])mr_errors++;
  mr_pending[slot]=kind;mr_sp[slot]=cpu.r[15];mr_sr[slot]=cpu.sr;mr_entries[kind-1u]++;
  return;
 }
 if(!valid){if(pc==0x172c4u)mr_errors++;return;}
 unsigned kind=mr_pending[slot];
 if(!kind){
  if(pc==0x172c4u||(pc==MR_HELPER_RETURN&&rd32(f+110u)==0x172c4u&&rd32(f+68u)==0xe220u))mr_errors++;
  return;
 }
 if(pc!=(kind==1u?0x172c4u:MR_HELPER_RETURN))return;
 if(cpu.r[15]!=mr_sp[slot]+4u||(cpu.sr&0xffe0u)!=(mr_sr[slot]&0xffe0u))mr_errors++;
 mr_returns[kind-1u]++;mr_pending[slot]=0;
}
int matrix_route_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"original_entries\":%llu,\"original_returns\":%llu,\"native_entries\":%llu,\"native_returns\":%llu,\"ignored_other_E220_calls\":%llu,\"errors\":%llu,\"pending\":%u}\n",(unsigned long long)mr_entries[0],(unsigned long long)mr_returns[0],(unsigned long long)mr_entries[1],(unsigned long long)mr_returns[1],(unsigned long long)mr_ignored,(unsigned long long)mr_errors,mr_pending_total());return fclose(f)!=0;
}
