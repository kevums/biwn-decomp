static const uint32_t shared_root[6]=ROOTS,shared_end[6]=ENDS;
static const uint32_t shared_entry[6]=ENTRIES,shared_return[6]=RETURNS;
static const uint32_t shared_helper_return[6]=HELPER_RETURNS,shared_capture_end[6]=CAPTURE_ENDS;
static const uint32_t shared_fallback[6]=FALLBACKS;
static const uint32_t shared_offset[6]=OFFSETS,shared_low[6]=LOWS,shared_top[6]=TOPS;
static const uint32_t shared_helpers[6][9]=HELPERS;
static uint64_t shared_public[6],shared_attempts[6],shared_entries[6],shared_returns[6],shared_original[6],shared_fallbacks[6],shared_calls[6],shared_helper_returns[6],shared_C_observations[6],shared_errors,shared_C_outside;
static uint32_t shared_min[6]=TOPS;
static unsigned shared_pending[6][101],shared_busy[6][101],shared_rejected[6];
static struct cpu shared_incoming[6][101],shared_busy_CPU[6][101],shared_rejected_CPU[6];
static uint32_t shared_rejected_task[6];
static uint8_t shared_busy_frame[6][101][118],shared_busy_stack[6][101][208];
static unsigned shared_pending_total(void){unsigned n=0;for(unsigned k=0;k<6;k++){n+=shared_rejected[k];for(unsigned i=0;i<101;i++)n+=shared_pending[k][i]+shared_busy[k][i];}return n;}
static unsigned shared_same_CPU(const struct cpu *a,const struct cpu *b){for(unsigned i=0;i<16;i++)if(a->r[i]!=b->r[i])return 0;return a->sr==b->sr;}
static void shared_watch(uint32_t pc){
 unsigned relevant=pc>=CODE_LO&&pc<CODE_HI;
 for(unsigned k=0;k<6;k++){if(pc>=shared_root[k]&&pc<shared_end[k])relevant=1;for(unsigned h=0;h<9;h++)if(pc&&pc==shared_helpers[k][h])relevant=1;}
 if(!relevant)return;
 for(unsigned k=0;k<6;k++){if(pc==shared_root[k])shared_public[k]++;else if(pc>shared_root[k]&&pc<shared_end[k])shared_original[k]++;}
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;struct cpu current;read_cpu(&current);
 if(delta>=0x19400u||(delta&1023u)){
  for(unsigned k=0;k<6;k++){
   if(pc==shared_entry[k]){shared_attempts[k]++;if(shared_rejected[k])shared_errors++;shared_rejected[k]=1;shared_rejected_CPU[k]=current;shared_rejected_task[k]=task;}
   if(pc==shared_fallback[k]){shared_fallbacks[k]++;if(!shared_rejected[k]||shared_rejected_task[k]!=task||!shared_same_CPU(&current,&shared_rejected_CPU[k]))shared_errors++;shared_rejected[k]=0;}
  }
  if(pc>=C_FLOOR&&pc<CODE_HI)shared_C_outside++;
  return;
 }
 unsigned slot=delta/1024u;uint32_t base=ARENA+delta;
 for(unsigned k=0;k<6;k++){
  uint32_t frame=base+shared_offset[k];
  if(pc==shared_entry[k]){
   shared_attempts[k]++;deck_used[slot]=1;
   if(rd32(frame+114u)){
    if(shared_busy[k][slot])shared_errors++;shared_busy[k][slot]=1;shared_busy_CPU[k][slot]=current;
    memcpy(shared_busy_frame[k][slot],memory+frame,118);memcpy(shared_busy_stack[k][slot],memory+base+shared_low[k],shared_top[k]-shared_low[k]);
   }else{
    shared_entries[k]++;if(shared_pending[k][slot])shared_errors++;else shared_incoming[k][slot]=current;shared_pending[k][slot]++;
   }
  }
  if(pc==shared_fallback[k]){
   shared_fallbacks[k]++;
   if(!shared_busy[k][slot]||!shared_same_CPU(&current,&shared_busy_CPU[k][slot])||memcmp(shared_busy_frame[k][slot],memory+frame,118)||memcmp(shared_busy_stack[k][slot],memory+base+shared_low[k],shared_top[k]-shared_low[k]))shared_errors++;
   shared_busy[k][slot]=0;
  }
  if(!shared_pending[k][slot])continue;
  if(pc==shared_return[k]){
   shared_returns[k]++;shared_pending[k][slot]--;
   if(current.r[15]!=shared_incoming[k][slot].r[15]||rd32(frame+114u)||rd32(frame+94u))shared_errors++;
   for(unsigned i=0;i<15;i++){unsigned preserve=k==0?((i>=2&&i<=7)||(i>=10&&i<=14)):k==1?(i==2||i==3):k==2?((i>=2&&i<=4)||(i>=10&&i<=14)):k==3?(i==2||i==10):k==4?(i==2||i==3):(i==2||i==10);if(preserve&&current.r[i]!=shared_incoming[k][slot].r[i])shared_errors++;}
   if(k==5){for(unsigned i=0;i<16;i++)if(current.r[i]!=rd32(frame+4u+4u*i))shared_errors++;if(current.sr!=rd16(frame+80u)||rd32(frame+68u)!=0x17f12u||rd32(frame+(current.sr&0x2000u?76u:72u))!=current.r[15])shared_errors++;}
  }
  if(pc==shared_helper_return[k]){shared_helper_returns[k]++;if(current.r[15]!=rd32(frame+106u)+4u)shared_errors++;}
  for(unsigned h=0;h<9;h++)if(pc&&pc==shared_helpers[k][h]&&current.r[15]==rd32(frame+106u)&&rd32(current.r[15])==shared_helper_return[k])shared_calls[k]++;
  if(pc>=shared_helper_return[k]+12u&&pc<shared_capture_end[k]){uint32_t phase=pc-shared_helper_return[k],off=(phase==12u||phase==16u)?0u:phase==20u?64u:4u;if(current.r[15]!=frame+off)shared_errors++;}
 }
 if(pc>=C_FLOOR&&pc<CODE_HI){
  unsigned matched=0;for(unsigned k=0;k<6;k++)if(shared_pending[k][slot]&&current.r[15]>=base+shared_low[k]&&current.r[15]<=base+shared_top[k]){matched++;shared_C_observations[k]++;uint32_t off=current.r[15]-base;if(off<shared_min[k])shared_min[k]=off;}
  if(matched!=1u)shared_C_outside++;
 }
}
int shared_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"errors\":%llu,\"pending\":%u,\"C_stack_outside\":%llu",(unsigned long long)shared_errors,shared_pending_total(),(unsigned long long)shared_C_outside);
 const uint64_t *arrays[]={shared_public,shared_entries,shared_returns,shared_original,shared_fallbacks,shared_calls,shared_helper_returns,shared_C_observations,shared_attempts};
 const char *keys[]={"public_entries","native_entries","native_returns","original_body_steps","fallback_entries","helper_entries","helper_returns","C_stack_observations","native_entry_attempts"};
 for(unsigned j=0;j<9;j++){fprintf(f,",\"%s\":[",keys[j]);for(unsigned k=0;k<6;k++)fprintf(f,"%s%llu",k?",":"",(unsigned long long)arrays[j][k]);fputc(']',f);}
 fprintf(f,",\"C_stack_low_offsets\":[%u,%u,%u,%u,%u,%u]}\n",shared_min[0],shared_min[1],shared_min[2],shared_min[3],shared_min[4],shared_min[5]);return fclose(f)!=0;
}
