/* Read-only geometry witness. Compiled helper completion is the actual
 * service_geometry C return, before deck_call consumes its logical RTS.
 * Original helpers use their actual logical RTS boundary. */
static unsigned g5_gpu_pending[101];
static uint32_t g5_gpu_sp[101];
static uint64_t g5_native_gpu_entries,g5_native_gpu_returns,g5_original_gpu_entries,g5_original_gpu_returns,g5_original_faces_steps;
static unsigned g4_pending[101],g4_helper_pending[101],g4_native[101],g4_marker_seen[101],g4_order[101];
static struct cpu g4_incoming[101];
static uint32_t g4_return_word[101],g4_service_sp[101],g4_service_ret[101];
static uint64_t g4_entries,g4_returns,g4_body_steps,g4_errors,g4_parent_returns;
static uint64_t g4_helpers[5],g4_helper_returns[5],g4_compiled[5],g4_markers[5],g4_transform_entries,g4_transform_returns;
static unsigned g4_transform_pending[101];
static uint32_t g4_plane_sp[101],g4_plane_ret[101],g4_plane_guest_sp[101];
static uint64_t g4_original_plane_entries,g4_original_plane_returns,g4_original_plane_steps;
static const uint32_t g4_targets[5]={0x10968u,0x11384u,0x10ba4u,0x1142eu,0x10734u};
static const uint32_t g4_logical_returns[5]={0x11ae6u,0x11b32u,0x11b38u,0x11b3eu,0x11b44u};
static unsigned g4_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=g4_pending[i]+g4_helper_pending[i]+g4_transform_pending[i]+g5_gpu_pending[i];return n;}
static void g4_watch(uint32_t pc){
 unsigned relevant=(pc>=0x11ad4u&&pc<0x11b4cu)||pc==G4_NATIVE_ENTRY||pc==G4_NATIVE_RETURN||pc==G4_HELPER_RETURN||pc==G4_SERVICE||pc==G4_MARKER||pc==G4_PLANE_SERVICE||pc==G5_FACES_SERVICE||pc==0xe26cu||pc==0x11684u||(pc>=0x1142eu&&pc<0x11762u)||pc==0x113feu||(pc>=0x110d4u&&pc<0x11384u);
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h])relevant=1;
 for(unsigned i=0;i<101;i++)if((g4_native[i]&&g4_helper_pending[i]&&pc==g4_service_ret[i])||(g4_transform_pending[i]==1u&&pc==g4_plane_ret[i]))relevant=1;
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
 if(pc==G5_FACES_SERVICE){
  unsigned h=3u;
  if(!g4_native[slot]||g4_helper_pending[slot]||g4_order[slot]!=h||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(cpu.r[15]+16u)!=0x1142eu||rd32(f+114u)!=1u)g4_errors++;
  if(cpu.r[15]<G4_DECK+delta+832u||cpu.r[15]+20u>G4_DECK+delta+1008u||rd32(cpu.r[15])<G4_CODE||rd32(cpu.r[15])>=G4_END)g4_errors++;
  if(rd32(f+68u)!=0x1142eu||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[h]||rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
  g4_service_sp[slot]=cpu.r[15];g4_service_ret[slot]=rd32(cpu.r[15]);g4_helper_pending[slot]=4u;g4_marker_seen[slot]=1u;g4_helpers[h]++;g4_compiled[h]++;g4_markers[h]++;
 }
 if(g4_helper_pending[slot]==4u&&!g4_native[slot]&&pc>=0x1142eu&&pc<0x11762u)g5_original_faces_steps++;
 if(pc==0xe26cu&&g4_helper_pending[slot]==4u){
  uint32_t sp=cpu.r[15],expected=helper_sp-58u;
  if(g5_gpu_pending[slot]||sp!=expected||rd16(sp+20u)!=0u)g4_errors++;
  if(g4_native[slot]){
   uint32_t csp=rd32(f+98u);
   if(rd32(sp)!=G4_HELPER_RETURN||rd32(f+106u)!=sp||rd32(f+110u)!=0x11684u||rd32(f+64u)!=sp||rd32(f+68u)!=0xe26cu||rd32(f+102u)!=f+4u||rd32(f+114u)!=1u)g4_errors++;
   if(csp<G4_DECK+delta+832u||csp+44u>G4_DECK+delta+1008u)g4_errors++;
   g5_gpu_pending[slot]=1u;g5_native_gpu_entries++;
  }else{
   if(rd32(sp)!=0x11684u)g4_errors++;
   g5_gpu_pending[slot]=2u;g5_original_gpu_entries++;
  }
  g5_gpu_sp[slot]=sp;
 }
 if(g5_gpu_pending[slot]&&((g5_gpu_pending[slot]==1u&&pc==G4_HELPER_RETURN)||(g5_gpu_pending[slot]==2u&&pc==0x11684u))){
  if(cpu.r[15]!=g5_gpu_sp[slot]+4u)g4_errors++;
  if(g5_gpu_pending[slot]==1u)g5_native_gpu_returns++;else g5_original_gpu_returns++;
  g5_gpu_pending[slot]=0;
 }
 if(pc==G4_MARKER){
  uint32_t target=rd32(cpu.r[15]+8u);unsigned tag=g4_helper_pending[slot];
  if(!tag||tag>3u||rd32(cpu.r[15]+4u)!=f||g4_targets[tag-1u]!=target||g4_marker_seen[slot])g4_errors++;
  else {g4_marker_seen[slot]=1;g4_markers[tag-1u]++;}
 }
 if(pc==G4_PLANE_SERVICE){
  if(!g4_native[slot]||g4_helper_pending[slot]!=2u||g4_transform_pending[slot]||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(cpu.r[15]+16u)!=0x110d4u)g4_errors++;
  if(cpu.r[15]<G4_DECK+delta+832u||cpu.r[15]+20u>G4_DECK+delta+1008u||rd32(cpu.r[15])<G4_CODE||rd32(cpu.r[15])>=G4_END)g4_errors++;
  if(rd32(f+68u)!=0x110d4u||rd32(f+64u)!=helper_sp-18u||rd32(helper_sp-18u)!=0x113feu||rd32(f+114u)!=1u)g4_errors++;
  g4_transform_pending[slot]=1;g4_transform_entries++;g4_plane_sp[slot]=cpu.r[15];g4_plane_ret[slot]=rd32(cpu.r[15]);g4_plane_guest_sp[slot]=rd32(f+64u);
 }
 if(g4_transform_pending[slot]==1u&&pc==g4_plane_ret[slot]){
  uint32_t logical=rd32(f+68u);
  if(cpu.r[15]!=g4_plane_sp[slot]+4u||rd32(f+64u)!=g4_plane_guest_sp[slot]||rd32(g4_plane_guest_sp[slot])!=0x113feu||rd32(f+94u)||(logical!=0x11178u&&logical!=0x111e2u&&logical!=0x1124cu&&logical!=0x11382u))g4_errors++;
  g4_transform_returns++;g4_transform_pending[slot]=0;
 }
 if(pc==0x110d4u&&g4_helper_pending[slot]==2u){
  if(g4_native[slot]||g4_transform_pending[slot]||cpu.r[15]!=helper_sp-18u||rd32(cpu.r[15])!=0x113feu)g4_errors++;
  g4_transform_pending[slot]=2;g4_original_plane_entries++;
 }
 if(g4_transform_pending[slot]==2u&&pc>=0x110d4u&&pc<0x11384u)g4_original_plane_steps++;
 if(g4_transform_pending[slot]==2u&&pc==0x113feu){
  if(cpu.r[15]!=helper_sp-14u)g4_errors++;
  g4_original_plane_returns++;g4_transform_pending[slot]=0;
 }
 unsigned tag=g4_helper_pending[slot];
 if(g4_native[slot]&&tag&&tag<=4u&&pc==g4_service_ret[slot]){
  uint32_t logical=rd32(f+68u);
  if((tag==1u&&logical!=0x1098eu)||(tag==2u&&logical!=0x1142cu)||(tag==3u&&logical!=0x10bb2u&&logical!=0x10c16u)||(tag==4u&&logical!=0x11760u))g4_errors++;
  if(cpu.r[15]!=g4_service_sp[slot]+4u||!g4_marker_seen[slot]||g4_transform_pending[slot]||g5_gpu_pending[slot]||rd32(f+94u)||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[tag-1u])g4_errors++;
  g4_helper_returns[tag-1u]++;g4_helper_pending[slot]=0;g4_order[slot]++;
 }
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h]&&cpu.r[15]==helper_sp){
  uint32_t ret=rd32(helper_sp);
  if(ret==G4_HELPER_RETURN||ret==g4_logical_returns[h]){
   if(g4_helper_pending[slot]||g4_order[slot]!=h||(g4_native[slot]&&h<4u))g4_errors++;
   g4_helper_pending[slot]=h+1u;g4_helpers[h]++;
   if(rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
  }
 }
 tag=g4_helper_pending[slot];
 if(tag&&(!g4_native[slot]||tag>4u)&&(pc==G4_HELPER_RETURN||pc==g4_logical_returns[tag-1u])){
  g4_helper_returns[tag-1u]++;g4_helper_pending[slot]=0;g4_order[slot]++;
  if(cpu.r[15]!=helper_sp+4u)g4_errors++;
 }
 if(pc==0x11b4au||pc==G4_NATIVE_RETURN){
  g4_returns++;g4_pending[slot]=0;
  if(g4_helper_pending[slot]||g4_transform_pending[slot]||g5_gpu_pending[slot]||g4_order[slot]!=5u||cpu.r[15]!=g4_incoming[slot].r[15]||rd32(cpu.r[15])!=g4_return_word[slot])g4_errors++;
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
 fprintf(f,",\"original_transform_entries\":%llu,\"original_transform_returns\":%llu,\"original_transform_steps\":%llu",(unsigned long long)g4_original_plane_entries,(unsigned long long)g4_original_plane_returns,(unsigned long long)g4_original_plane_steps);
 fprintf(f,",\"native_GPU_entries\":%llu,\"native_GPU_returns\":%llu,\"original_GPU_entries\":%llu,\"original_GPU_returns\":%llu,\"original_faces_body_steps\":%llu",(unsigned long long)g5_native_gpu_entries,(unsigned long long)g5_native_gpu_returns,(unsigned long long)g5_original_gpu_entries,(unsigned long long)g5_original_gpu_returns,(unsigned long long)g5_original_faces_steps);
 const uint64_t *arrays[]={g4_helpers,g4_helper_returns,g4_compiled,g4_markers};const char *keys[]={"helper_entries","helper_returns","compiled_helper_services","compiled_helper_markers"};
 for(unsigned j=0;j<4;j++){fprintf(f,",\"%s\":[",keys[j]);for(unsigned h=0;h<5;h++)fprintf(f,"%s%llu",h?",":"",(unsigned long long)arrays[j][h]);fputc(']',f);}
 fputs("}\n",f);return fclose(f)!=0;
}
