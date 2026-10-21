/* Read-only geometry witness. Compiled helper completion is the actual
 * service_geometry C return, before deck_call consumes its logical RTS.
 * Original helpers use their actual logical RTS boundary. */
static unsigned g4_pending[101],g4_helper_pending[101],g4_native[101],g4_marker_seen[101],g4_order[101];
static struct cpu g4_incoming[101];
static uint32_t g4_return_word[101],g4_service_sp[101],g4_service_ret[101];
static uint64_t g4_entries,g4_returns,g4_body_steps,g4_errors,g4_parent_returns;
static uint64_t g4_helpers[5],g4_helper_returns[5],g4_compiled[5],g4_markers[5],g4_transform_entries,g4_transform_returns;
static unsigned g4_transform_pending[101];
static const uint32_t g4_targets[5]={0x10968u,0x11384u,0x10ba4u,0x1142eu,0x10734u};
static const uint32_t g4_logical_returns[5]={0x11ae6u,0x11b32u,0x11b38u,0x11b3eu,0x11b44u};
static unsigned g4_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=g4_pending[i]+g4_helper_pending[i]+g4_transform_pending[i];return n;}
static void g4_watch(uint32_t pc){
 unsigned relevant=(pc>=0x11ad4u&&pc<0x11b4cu)||pc==G4_NATIVE_ENTRY||pc==G4_NATIVE_RETURN||pc==G4_HELPER_RETURN||pc==G4_SERVICE||pc==G4_MARKER||pc==0x110d4u;
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h])relevant=1;
 for(unsigned i=0;i<101;i++)if(g4_native[i]&&g4_helper_pending[i]&&pc==g4_service_ret[i])relevant=1;
 if(!relevant)return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==0x11ad4u||pc==G4_NATIVE_ENTRY)g4_errors++;return;}
 unsigned slot=delta/1024u;struct cpu cpu;read_cpu(&cpu);uint32_t f=G4_DECK+delta+16u;
 if(pc==0x11ad4u){
  g4_entries++;if(g4_pending[slot]){g4_errors++;return;}
  g4_pending[slot]=1;g4_incoming[slot]=cpu;g4_return_word[slot]=rd32(cpu.r[15]);g4_order[slot]=0;
 }
 if(!g4_pending[slot])return;
 if(pc==G4_NATIVE_ENTRY)g4_native[slot]=1;
 if(pc>0x11ad4u&&pc<0x11b4cu)g4_body_steps++;
 uint32_t helper_sp=g4_incoming[slot].r[15]-16u;
 if(pc==G4_SERVICE){
  unsigned target=rd32(cpu.r[15]+16u),h=target==0x10968u?0u:target==0x11384u?1u:target==0x10ba4u?2u:5u;
  if(h<3){
   if(!g4_native[slot]||g4_helper_pending[slot]||g4_order[slot]!=h||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(f+114u)!=1u)g4_errors++;
   if(cpu.r[15]<G4_DECK+delta+832u||cpu.r[15]+20u>G4_DECK+delta+1008u||rd32(cpu.r[15])<G4_CODE||rd32(cpu.r[15])>=G4_END)g4_errors++;
   if(rd32(f+68u)!=target||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[h]||rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
   g4_service_sp[slot]=cpu.r[15];g4_service_ret[slot]=rd32(cpu.r[15]);g4_helper_pending[slot]=h+1u;g4_marker_seen[slot]=0;g4_helpers[h]++;g4_compiled[h]++;
  }
 }
 if(pc==G4_MARKER){
  uint32_t target=rd32(cpu.r[15]+8u);unsigned tag=g4_helper_pending[slot];
  if(!tag||tag>3u||rd32(cpu.r[15]+4u)!=f||g4_targets[tag-1u]!=target||g4_marker_seen[slot])g4_errors++;
  else {g4_marker_seen[slot]=1;g4_markers[tag-1u]++;}
 }
 if(pc==0x110d4u&&g4_native[slot]){
  if(g4_helper_pending[slot]!=2u||g4_transform_pending[slot]||rd32(cpu.r[15])!=G4_HELPER_RETURN||rd32(f+106u)!=cpu.r[15]||rd32(f+110u)!=0x113feu)g4_errors++;
  g4_transform_pending[slot]=1;g4_transform_entries++;
 }
 if(pc==G4_HELPER_RETURN&&g4_transform_pending[slot]){
  if(cpu.r[15]!=rd32(f+106u)+4u)g4_errors++;
  g4_transform_returns++;g4_transform_pending[slot]=0;
 }
 unsigned tag=g4_helper_pending[slot];
 if(g4_native[slot]&&tag&&tag<=3u&&pc==g4_service_ret[slot]){
  if(cpu.r[15]!=g4_service_sp[slot]+4u||!g4_marker_seen[slot]||g4_transform_pending[slot]||rd32(f+94u)||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[tag-1u])g4_errors++;
  g4_helper_returns[tag-1u]++;g4_helper_pending[slot]=0;g4_order[slot]++;
 }
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h]&&cpu.r[15]==helper_sp){
  uint32_t ret=rd32(helper_sp);
  if(ret==G4_HELPER_RETURN||ret==g4_logical_returns[h]){
   if(g4_helper_pending[slot]||g4_order[slot]!=h||(g4_native[slot]&&h<3u))g4_errors++;
   g4_helper_pending[slot]=h+1u;g4_helpers[h]++;
   if(rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
  }
 }
 tag=g4_helper_pending[slot];
 if(tag&&(!g4_native[slot]||tag>3u)&&(pc==G4_HELPER_RETURN||pc==g4_logical_returns[tag-1u])){
  g4_helper_returns[tag-1u]++;g4_helper_pending[slot]=0;g4_order[slot]++;
  if(cpu.r[15]!=helper_sp+4u)g4_errors++;
 }
 if(pc==0x11b4au||pc==G4_NATIVE_RETURN){
  g4_returns++;g4_pending[slot]=0;
  if(g4_helper_pending[slot]||g4_transform_pending[slot]||g4_order[slot]!=5u||cpu.r[15]!=g4_incoming[slot].r[15]||rd32(cpu.r[15])!=g4_return_word[slot])g4_errors++;
  if(cpu.r[2]!=g4_incoming[slot].r[2]||cpu.r[3]!=g4_incoming[slot].r[3])g4_errors++;
  if(g4_return_word[slot]==0x11ee4u||(g4_return_word[slot]==G4_OUTER_RETURN&&rd32(G4_OUTER_ARENA+slot*384u+122u)==g4_incoming[slot].r[15]&&rd32(G4_OUTER_ARENA+slot*384u+126u)==0x11ee4u))g4_parent_returns++;else g4_errors++;
  g4_native[slot]=0;
 }
}
static int32_t o6_retained_observe(uint32_t pc){g4_watch(pc);return g4_retained_observe(pc);}
static int o6_retained_quiescent(void){return g4_retained_quiescent()&&!g4_pending_total();}
int geometry_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"entries\":%llu,\"returns\":%llu,\"original_body_steps\":%llu,\"errors\":%llu,\"pending\":%u,\"matched_outer_parent_returns\":%llu,\"transform_entries\":%llu,\"transform_returns\":%llu",(unsigned long long)g4_entries,(unsigned long long)g4_returns,(unsigned long long)g4_body_steps,(unsigned long long)g4_errors,g4_pending_total(),(unsigned long long)g4_parent_returns,(unsigned long long)g4_transform_entries,(unsigned long long)g4_transform_returns);
 const uint64_t *arrays[]={g4_helpers,g4_helper_returns,g4_compiled,g4_markers};const char *keys[]={"helper_entries","helper_returns","compiled_helper_services","compiled_helper_markers"};
 for(unsigned j=0;j<4;j++){fprintf(f,",\"%s\":[",keys[j]);for(unsigned h=0;h<5;h++)fprintf(f,"%s%llu",h?",":"",(unsigned long long)arrays[j][h]);fputc(']',f);}
 fputs("}\n",f);return fclose(f)!=0;
}
