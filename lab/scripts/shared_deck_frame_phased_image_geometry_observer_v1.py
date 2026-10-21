"""Read-only geometry/helper witnesses added to retained five-root/face monitors."""
import shared_deck_frame_phased_image_face_observer_v1 as prior
ROOT = prior.ROOT


def observer_source(build, parent):
    text, source = prior.observer_source(build, parent)
    assert text.count('int32_t observe(uint32_t pc)') == 1
    text = text.replace('int32_t observe(uint32_t pc)', 'static int32_t g4_retained_observe(uint32_t pc)', 1)
    assert text.count('int observer_quiescent(void)') == 1
    text = text.replace('int observer_quiescent(void)', 'static int g4_retained_quiescent(void)', 1)
    symbols = build['shared_Deck_symbols']
    text += r'''
static unsigned g4_pending[101],g4_helper_pending[101];
static struct cpu g4_incoming[101];
static uint32_t g4_return_word[101];
static uint64_t g4_entries,g4_returns,g4_body_steps,g4_errors,g4_parent_returns;
static uint64_t g4_helpers[5],g4_helper_returns[5];
static const uint32_t g4_targets[5]={0x10968u,0x11384u,0x10ba4u,0x1142eu,0x10734u};
static const uint32_t g4_logical_returns[5]={0x11ae6u,0x11b32u,0x11b38u,0x11b3eu,0x11b44u};
static unsigned g4_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=g4_pending[i];return n;}
static void g4_watch(uint32_t pc){
 unsigned relevant=pc>=0x11ad4u&&pc<0x11b4cu;
 relevant|=pc==GEOMETRY_NATIVE_RETURN||pc==GEOMETRY_HELPER_RETURN;
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h])relevant=1;
 if(!relevant)return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==0x11ad4u)g4_errors++;return;}
 unsigned slot=delta/1024u;struct cpu cpu;read_cpu(&cpu);
 if(pc==0x11ad4u){
  g4_entries++;if(g4_pending[slot]){g4_errors++;return;}
  g4_pending[slot]=1;g4_incoming[slot]=cpu;g4_return_word[slot]=rd32(cpu.r[15]);
 }
 if(!g4_pending[slot])return;
 if(pc>0x11ad4u&&pc<0x11b4cu)g4_body_steps++;
 uint32_t helper_sp=g4_incoming[slot].r[15]-16u;
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h]&&cpu.r[15]==helper_sp){
  uint32_t ret=rd32(cpu.r[15]);
  if(ret==GEOMETRY_HELPER_RETURN||ret==g4_logical_returns[h]){
   if(g4_helper_pending[slot])g4_errors++;
   g4_helper_pending[slot]=h+1u;g4_helpers[h]++;
   if(rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
  }
 }
 unsigned tag=g4_helper_pending[slot];
 if(tag&&(pc==GEOMETRY_HELPER_RETURN||pc==g4_logical_returns[tag-1u])){
  g4_helper_returns[tag-1u]++;g4_helper_pending[slot]=0;
  if(cpu.r[15]!=helper_sp+4u)g4_errors++;
 }
 if(pc==0x11b4au||pc==GEOMETRY_NATIVE_RETURN){
  g4_returns++;g4_pending[slot]=0;
  if(g4_helper_pending[slot]||cpu.r[15]!=g4_incoming[slot].r[15]||rd32(cpu.r[15])!=g4_return_word[slot])g4_errors++;
  if(cpu.r[2]!=g4_incoming[slot].r[2]||cpu.r[3]!=g4_incoming[slot].r[3])g4_errors++;
  if(g4_return_word[slot]==0x11ee4u)g4_parent_returns++;else g4_errors++;
 }
}
int32_t observe(uint32_t pc){g4_watch(pc);return g4_retained_observe(pc);}
int observer_quiescent(void){return g4_retained_quiescent()&&!g4_pending_total();}
int geometry_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"entries\":%llu,\"returns\":%llu,\"original_body_steps\":%llu,\"errors\":%llu,\"pending\":%u,\"original_outer_parent_returns\":%llu",(unsigned long long)g4_entries,(unsigned long long)g4_returns,(unsigned long long)g4_body_steps,(unsigned long long)g4_errors,g4_pending_total(),(unsigned long long)g4_parent_returns);
 fprintf(f,",\"helper_entries\":[");for(unsigned h=0;h<5;h++)fprintf(f,"%s%llu",h?",":"",(unsigned long long)g4_helpers[h]);
 fprintf(f,"],\"helper_returns\":[");for(unsigned h=0;h<5;h++)fprintf(f,"%s%llu",h?",":"",(unsigned long long)g4_helper_returns[h]);
 fprintf(f,"]}\n");return fclose(f)!=0;
}
'''
    text = text.replace('GEOMETRY_NATIVE_RETURN', str(symbols['biwn_v4_geometry_return']) + 'u')
    text = text.replace('GEOMETRY_HELPER_RETURN', str(symbols['biwn_v4_geometry_helper_return']) + 'u')
    return text, source
