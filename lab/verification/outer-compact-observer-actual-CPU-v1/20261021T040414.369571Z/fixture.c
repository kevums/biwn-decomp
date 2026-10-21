
#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static struct cpu current;static uint8_t memory[0x200000];
static uint32_t rd32(uint32_t a){return ((uint32_t)memory[a]<<24)|((uint32_t)memory[a+1]<<16)|((uint32_t)memory[a+2]<<8)|memory[a+3];}
static uint16_t rd16(uint32_t a){return ((uint16_t)memory[a]<<8)|memory[a+1];}
static void read_cpu(struct cpu *o){*o=current;}
static unsigned g6_pending[101],g6_calls[101],g6_active[101];
static uint32_t g6_sp[101];
static uint64_t g6_native_calls,g6_native_returns,g6_original_calls,g6_original_returns,g6_original_body_steps,g6_active_entries,g6_inactive_entries;
static const uint32_t g6_targets[2]={0x1b45au,0x149aeu};
static const uint32_t g6_returns[16]={0x107aau,0x107d2u,0x107e6u,0x10808u,0x1081cu,0x1083eu,0x10852u,0x10874u,0x10888u,0x108aau,0x108beu,0x108e0u,0x108f6u,0x10918u,0x10938u,0x1095au};
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
static unsigned g4_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=g4_pending[i]+g4_helper_pending[i]+g4_transform_pending[i]+g5_gpu_pending[i]+g6_pending[i];return n;}
static void g4_watch(uint32_t pc){
 unsigned relevant=(pc>=0x11ad4u&&pc<0x11b4cu)||pc==1499132u||pc==1499320u||pc==1500630u||pc==1539864u||pc==1537420u||pc==1513462u||pc==1537430u||pc==1537852u||pc==0x1b45au||pc==0x149aeu||(pc>=0x10734u&&pc<0x10968u)||pc==0xe26cu||pc==0x11684u||(pc>=0x1142eu&&pc<0x11762u)||pc==0x113feu||(pc>=0x110d4u&&pc<0x11384u);
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h])relevant=1;
 for(unsigned j=0;j<16;j++)if(pc==g6_returns[j])relevant=1;
 for(unsigned i=0;i<101;i++)if((g4_native[i]&&g4_helper_pending[i]&&pc==g4_service_ret[i])||(g4_transform_pending[i]==1u&&pc==g4_plane_ret[i]))relevant=1;
 if(!relevant)return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==0x11ad4u||pc==1499132u)g4_errors++;return;}
 unsigned slot=delta/1024u;struct cpu cpu;read_cpu(&cpu);uint32_t f=1553344u+delta+16u;
 if(pc==0x11ad4u){
  g4_entries++;if(g4_pending[slot]){g4_errors++;return;}
  g4_pending[slot]=1;g4_incoming[slot]=cpu;g4_return_word[slot]=rd32(cpu.r[15]);g4_order[slot]=0;
 }
 if(!g4_pending[slot])return;
 if(pc==1499132u)g4_native[slot]=1;
 if(pc>0x11ad4u&&pc<0x11b4cu)g4_body_steps++;
 uint32_t helper_sp=g4_incoming[slot].r[15]-16u;
 if(pc==1539864u){
  unsigned target=rd32(cpu.r[15]+16u),h=target==0x10968u?0u:target==0x11384u?1u:target==0x10ba4u?2u:5u;
  if(h<3){
   if(!g4_native[slot]||g4_helper_pending[slot]||g4_order[slot]!=h||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(f+114u)!=1u)g4_errors++;
   if(cpu.r[15]<1553344u+delta+832u||cpu.r[15]+20u>1553344u+delta+1008u||rd32(cpu.r[15])<1498112u||rd32(cpu.r[15])>=1546850u)g4_errors++;
   if(rd32(f+68u)!=target||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[h]||rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
   g4_service_sp[slot]=cpu.r[15];g4_service_ret[slot]=rd32(cpu.r[15]);g4_helper_pending[slot]=h+1u;g4_marker_seen[slot]=0;g4_helpers[h]++;g4_compiled[h]++;
  }
 }
 if(pc==1537430u){
  unsigned h=3u;
  if(!g4_native[slot]||g4_helper_pending[slot]||g4_order[slot]!=h||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(cpu.r[15]+16u)!=0x1142eu||rd32(f+114u)!=1u)g4_errors++;
  if(cpu.r[15]<1553344u+delta+832u||cpu.r[15]+20u>1553344u+delta+1008u||rd32(cpu.r[15])<1498112u||rd32(cpu.r[15])>=1546850u)g4_errors++;
  if(rd32(f+68u)!=0x1142eu||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[h]||rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
  g4_service_sp[slot]=cpu.r[15];g4_service_ret[slot]=rd32(cpu.r[15]);g4_helper_pending[slot]=4u;g4_marker_seen[slot]=1u;g4_helpers[h]++;g4_compiled[h]++;g4_markers[h]++;
 }
 if(pc==1537852u){
  unsigned h=4u;
  if(!g4_native[slot]||g4_helper_pending[slot]||g4_order[slot]!=h||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(cpu.r[15]+16u)!=0x10734u||rd32(f+114u)!=1u)g4_errors++;
  if(cpu.r[15]<1553344u+delta+832u||cpu.r[15]+20u>1553344u+delta+1008u||rd32(cpu.r[15])<1498112u||rd32(cpu.r[15])>=1546850u)g4_errors++;
  if(rd32(f+68u)!=0x10734u||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[h]||rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
  if(rd32(f+90u)!=2u||rd32(f+82u)!=1539864u||rd32(f+86u)!=f||g6_pending[slot])g4_errors++;
  g4_service_sp[slot]=cpu.r[15];g4_service_ret[slot]=rd32(cpu.r[15]);g4_helper_pending[slot]=5u;g4_marker_seen[slot]=1u;g4_helpers[h]++;g4_compiled[h]++;g4_markers[h]++;
  g6_calls[slot]=0;g6_active[slot]=rd16(0x403ccu)!=0u;if(g6_active[slot])g6_active_entries++;else g6_inactive_entries++;
 }
 if(g4_helper_pending[slot]==5u){
  if(!g4_native[slot]&&pc>=0x10734u&&pc<0x10968u)g6_original_body_steps++;
  if(pc==0x1b45au||pc==0x149aeu){
   unsigned j=g6_calls[slot];uint32_t sp=cpu.r[15],want=helper_sp-((j&1u)?108u:84u);
   if(j>=16u||!g6_active[slot]||g6_pending[slot]||sp!=want||pc!=g6_targets[j&1u])g4_errors++;
   if(g4_native[slot]){
    uint32_t csp=rd32(f+98u);
    if(j>=16u||rd32(f+90u)!=15u-j||rd32(f+82u)!=1514146u||rd32(f+86u)!=f||rd32(f+114u)!=1u)g4_errors++;
    if(rd32(sp)!=1500630u||rd32(f+106u)!=sp||j>=16u||rd32(f+110u)!=g6_returns[j%16u]||rd32(f+64u)!=sp||rd32(f+68u)!=pc||rd32(f+102u)!=f+4u)g4_errors++;
    if(csp<1553344u+delta+832u||csp+44u>1553344u+delta+1008u)g4_errors++;
    g6_pending[slot]=1u;g6_native_calls++;
   }else{
    if(j>=16u||rd32(sp)!=g6_returns[j%16u])g4_errors++;
    g6_pending[slot]=2u;g6_original_calls++;
   }
   g6_sp[slot]=sp;
  }
  if(g6_pending[slot]&&((g6_pending[slot]==1u&&pc==1500630u)||(g6_pending[slot]==2u&&pc==g6_returns[g6_calls[slot]%16u]))){
   if(cpu.r[15]!=g6_sp[slot]+4u)g4_errors++;
   if(g6_pending[slot]==1u)g6_native_returns++;else g6_original_returns++;
   g6_calls[slot]++;g6_pending[slot]=0;
  }
 }
 if(g4_helper_pending[slot]==4u&&!g4_native[slot]&&pc>=0x1142eu&&pc<0x11762u)g5_original_faces_steps++;
 if(pc==0xe26cu&&g4_helper_pending[slot]==4u){
  uint32_t sp=cpu.r[15],expected=helper_sp-58u;
  if(g5_gpu_pending[slot]||sp!=expected||rd16(sp+20u)!=0u)g4_errors++;
  if(g4_native[slot]){
   uint32_t csp=rd32(f+98u);
   if(rd32(sp)!=1500630u||rd32(f+106u)!=sp||rd32(f+110u)!=0x11684u||rd32(f+64u)!=sp||rd32(f+68u)!=0xe26cu||rd32(f+102u)!=f+4u||rd32(f+114u)!=1u)g4_errors++;
   if(csp<1553344u+delta+832u||csp+44u>1553344u+delta+1008u)g4_errors++;
   g5_gpu_pending[slot]=1u;g5_native_gpu_entries++;
  }else{
   if(rd32(sp)!=0x11684u)g4_errors++;
   g5_gpu_pending[slot]=2u;g5_original_gpu_entries++;
  }
  g5_gpu_sp[slot]=sp;
 }
 if(g5_gpu_pending[slot]&&((g5_gpu_pending[slot]==1u&&pc==1500630u)||(g5_gpu_pending[slot]==2u&&pc==0x11684u))){
  if(cpu.r[15]!=g5_gpu_sp[slot]+4u)g4_errors++;
  if(g5_gpu_pending[slot]==1u)g5_native_gpu_returns++;else g5_original_gpu_returns++;
  g5_gpu_pending[slot]=0;
 }
 if(pc==1537420u){
  uint32_t target=rd32(cpu.r[15]+8u);unsigned tag=g4_helper_pending[slot];
  if(!tag||tag>3u||rd32(cpu.r[15]+4u)!=f||g4_targets[tag-1u]!=target||g4_marker_seen[slot])g4_errors++;
  else {g4_marker_seen[slot]=1;g4_markers[tag-1u]++;}
 }
 if(pc==1513462u){
  if(!g4_native[slot]||g4_helper_pending[slot]!=2u||g4_transform_pending[slot]||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(cpu.r[15]+16u)!=0x110d4u)g4_errors++;
  if(cpu.r[15]<1553344u+delta+832u||cpu.r[15]+20u>1553344u+delta+1008u||rd32(cpu.r[15])<1498112u||rd32(cpu.r[15])>=1546850u)g4_errors++;
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
 if(g4_native[slot]&&tag&&tag<=5u&&pc==g4_service_ret[slot]){
  uint32_t logical=rd32(f+68u);
  if((tag==1u&&logical!=0x1098eu)||(tag==2u&&logical!=0x1142cu)||(tag==3u&&logical!=0x10bb2u&&logical!=0x10c16u)||(tag==4u&&logical!=0x11760u)||(tag==5u&&logical!=0x10966u))g4_errors++;
  if(cpu.r[15]!=g4_service_sp[slot]+4u||!g4_marker_seen[slot]||g4_transform_pending[slot]||g5_gpu_pending[slot]||rd32(f+94u)||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[tag-1u])g4_errors++;
  if(tag==5u&&(g6_pending[slot]||g6_calls[slot]!=(g6_active[slot]?16u:0u)||rd32(f+90u)!=2u||rd32(f+82u)!=1539864u||rd32(f+86u)!=f))g4_errors++;
  g4_helper_returns[tag-1u]++;g4_helper_pending[slot]=0;g4_order[slot]++;
 }
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h]&&cpu.r[15]==helper_sp){
  uint32_t ret=rd32(helper_sp);
  if(ret==1500630u||ret==g4_logical_returns[h]){
   if(g4_helper_pending[slot]||g4_order[slot]!=h||g4_native[slot])g4_errors++;
   g4_helper_pending[slot]=h+1u;g4_helpers[h]++;
   if(h==4u){g6_calls[slot]=0;g6_active[slot]=rd16(0x403ccu)!=0u;if(g6_active[slot])g6_active_entries++;else g6_inactive_entries++;}
   if(rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
  }
 }
 tag=g4_helper_pending[slot];
 if(tag&&!g4_native[slot]&&(pc==1500630u||pc==g4_logical_returns[tag-1u])){
  if(tag==5u&&(g6_pending[slot]||g6_calls[slot]!=(g6_active[slot]?16u:0u)))g4_errors++;
  g4_helper_returns[tag-1u]++;g4_helper_pending[slot]=0;g4_order[slot]++;
  if(cpu.r[15]!=helper_sp+4u)g4_errors++;
 }
 if(pc==0x11b4au||pc==1499320u){
  g4_returns++;g4_pending[slot]=0;
  if(g4_helper_pending[slot]||g4_transform_pending[slot]||g5_gpu_pending[slot]||g4_order[slot]!=5u||cpu.r[15]!=g4_incoming[slot].r[15]||rd32(cpu.r[15])!=g4_return_word[slot])g4_errors++;
  if(cpu.r[2]!=g4_incoming[slot].r[2]||cpu.r[3]!=g4_incoming[slot].r[3])g4_errors++;
  if(g4_return_word[slot]==0x11ee4u||(g4_return_word[slot]==1547882u&&rd32(1656768u+slot*384u+122u)==g4_incoming[slot].r[15]&&rd32(1656768u+slot*384u+126u)==0x11ee4u))g4_parent_returns++;else g4_errors++;
  g4_native[slot]=0;
 }
}
int geometry_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"entries\":%llu,\"returns\":%llu,\"original_body_steps\":%llu,\"errors\":%llu,\"pending\":%u,\"matched_outer_parent_returns\":%llu,\"transform_entries\":%llu,\"transform_returns\":%llu",(unsigned long long)g4_entries,(unsigned long long)g4_returns,(unsigned long long)g4_body_steps,(unsigned long long)g4_errors,g4_pending_total(),(unsigned long long)g4_parent_returns,(unsigned long long)g4_transform_entries,(unsigned long long)g4_transform_returns);
 fprintf(f,",\"original_transform_entries\":%llu,\"original_transform_returns\":%llu,\"original_transform_steps\":%llu",(unsigned long long)g4_original_plane_entries,(unsigned long long)g4_original_plane_returns,(unsigned long long)g4_original_plane_steps);
 fprintf(f,",\"native_GPU_entries\":%llu,\"native_GPU_returns\":%llu,\"original_GPU_entries\":%llu,\"original_GPU_returns\":%llu,\"original_faces_body_steps\":%llu",(unsigned long long)g5_native_gpu_entries,(unsigned long long)g5_native_gpu_returns,(unsigned long long)g5_original_gpu_entries,(unsigned long long)g5_original_gpu_returns,(unsigned long long)g5_original_faces_steps);
 fprintf(f,",\"native_debug_dependency_entries\":%llu,\"native_debug_dependency_returns\":%llu,\"original_debug_dependency_entries\":%llu,\"original_debug_dependency_returns\":%llu,\"original_debug_body_steps\":%llu,\"debug_active_entries\":%llu,\"debug_inactive_entries\":%llu",(unsigned long long)g6_native_calls,(unsigned long long)g6_native_returns,(unsigned long long)g6_original_calls,(unsigned long long)g6_original_returns,(unsigned long long)g6_original_body_steps,(unsigned long long)g6_active_entries,(unsigned long long)g6_inactive_entries);
 const uint64_t *arrays[]={g4_helpers,g4_helper_returns,g4_compiled,g4_markers};const char *keys[]={"helper_entries","helper_returns","compiled_helper_services","compiled_helper_markers"};
 for(unsigned j=0;j<4;j++){fprintf(f,",\"%s\":[",keys[j]);for(unsigned h=0;h<5;h++)fprintf(f,"%s%llu",h?",":"",(unsigned long long)arrays[j][h]);fputc(']',f);}
 fputs("}\n",f);return fclose(f)!=0;
}


void reset(void){memset(memory,0,sizeof(memory));memset(&current,0,sizeof(current));
memset(g6_pending,0,sizeof(g6_pending));memset(g6_calls,0,sizeof(g6_calls));memset(g6_active,0,sizeof(g6_active));g6_native_calls=g6_native_returns=g6_original_calls=g6_original_returns=g6_original_body_steps=g6_active_entries=g6_inactive_entries=0;
memset(g5_gpu_pending,0,sizeof(g5_gpu_pending));memset(g5_gpu_sp,0,sizeof(g5_gpu_sp));g5_native_gpu_entries=g5_native_gpu_returns=g5_original_gpu_entries=g5_original_gpu_returns=g5_original_faces_steps=0;
memset(g4_pending,0,sizeof(g4_pending));memset(g4_helper_pending,0,sizeof(g4_helper_pending));memset(g4_native,0,sizeof(g4_native));memset(g4_marker_seen,0,sizeof(g4_marker_seen));memset(g4_order,0,sizeof(g4_order));memset(g4_transform_pending,0,sizeof(g4_transform_pending));
memset(g4_helpers,0,sizeof(g4_helpers));memset(g4_helper_returns,0,sizeof(g4_helper_returns));memset(g4_compiled,0,sizeof(g4_compiled));memset(g4_markers,0,sizeof(g4_markers));
g4_entries=g4_returns=g4_body_steps=g4_errors=g4_parent_returns=g4_transform_entries=g4_transform_returns=g4_original_plane_entries=g4_original_plane_returns=g4_original_plane_steps=0;}
void reg(unsigned i,uint32_t v){if(i<16)current.r[i]=v;}
void put(uint32_t a,uint32_t v){memory[a]=(uint8_t)(v>>24);memory[a+1]=(uint8_t)(v>>16);memory[a+2]=(uint8_t)(v>>8);memory[a+3]=(uint8_t)v;}
void word(uint32_t a,uint16_t v){memory[a]=(uint8_t)(v>>8);memory[a+1]=(uint8_t)v;}
void pc(uint32_t a){g4_watch(a);}

void snapshot(const void *raw,const struct cpu *cpu){memcpy(memory,raw,sizeof(memory));current=*cpu;}
int wants(uint32_t pc){ unsigned relevant=(pc>=0x11ad4u&&pc<0x11b4cu)||pc==1499132u||pc==1499320u||pc==1500630u||pc==1539864u||pc==1537420u||pc==1513462u||pc==1537430u||pc==1537852u||pc==0x1b45au||pc==0x149aeu||(pc>=0x10734u&&pc<0x10968u)||pc==0xe26cu||pc==0x11684u||(pc>=0x1142eu&&pc<0x11762u)||pc==0x113feu||(pc>=0x110d4u&&pc<0x11384u);
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h])relevant=1;
 for(unsigned j=0;j<16;j++)if(pc==g6_returns[j])relevant=1;
 for(unsigned i=0;i<101;i++)if((g4_native[i]&&g4_helper_pending[i]&&pc==g4_service_ret[i])||(g4_transform_pending[i]==1u&&pc==g4_plane_ret[i]))relevant=1;
return relevant!=0;}
