"""Extend the retained read-only monitor with natural original-face witnesses."""
import shared_deck_scene17_wait_base_observer_v1 as prior
ROOT=prior.ROOT
def observer_source(build,parent):
 text,source=prior.observer_source(build,parent)
 assert text.count('int32_t observe(uint32_t pc) {')==1
 text=text.replace('int32_t observe(uint32_t pc) {','static int32_t face_retained_observe(uint32_t pc) {',1)
 assert text.count('int observer_quiescent(void){')==1
 text=text.replace('int observer_quiescent(void){','static int face_retained_quiescent(void){',1)
 ret=build['shared_Deck_symbols']['biwn_v4_scan_helper_return'];arena=build['deck_arena_address'];face_return=build['shared_Deck_symbols']['biwn_v4_face_return']
 text+=r'''
static unsigned face_pending[101];
static struct cpu face_incoming[101];
static uint32_t face_return_word[101];
static uint8_t face_parent_frame[101][118],face_parent_stack[101][176];
static unsigned face_parent_active[101];
static uint64_t face_entries,face_returns,face_body_steps,face_helpers,face_errors,face_positive_speed,face_native_parent_returns,face_original_parent_returns,face_parent_checks;
static unsigned face_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=face_pending[i];return n;}
static void face_watch(uint32_t pc){
 if(!((pc>=0x1186au&&pc<0x11ad4u)||pc==NATIVE_FACE_RETURN||pc==0x10c6eu||pc==0x10cb6u))return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==0x1186au)face_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=FACE_ARENA+delta;struct cpu cpu;
 if(pc==0x1186au){
  face_entries++;if(face_pending[slot]){face_errors++;return;}
  face_pending[slot]=1;read_cpu(&cpu);face_incoming[slot]=cpu;face_return_word[slot]=rd32(cpu.r[15]);
  if((int32_t)rd32(0x40104u)>0)face_positive_speed++;
  face_parent_active[slot]=rd32(base+272u+114u)!=0;
  if(face_parent_active[slot]){memcpy(face_parent_frame[slot],ram+base+272u,118);memcpy(face_parent_stack[slot],ram+base+416u,176);}
 }
 if(!face_pending[slot])return;
 if(pc>=0x1186au&&pc<0x11ad4u)face_body_steps++;
 if(pc==0x10c6eu||pc==0x10cb6u)face_helpers++;
 if(pc==0x11ad2u||pc==NATIVE_FACE_RETURN){
  face_returns++;read_cpu(&cpu);face_pending[slot]=0;
  if(cpu.r[15]!=face_incoming[slot].r[15]||rd32(cpu.r[15])!=face_return_word[slot])face_errors++;
  for(unsigned i=0;i<15;i++)if((i==2u||i==3u||i==4u||i>=10u)&&cpu.r[i]!=face_incoming[slot].r[i])face_errors++;
  if(face_return_word[slot]==FACE_NATIVE_RETURN)face_native_parent_returns++;
  else if(face_return_word[slot]==0x11856u)face_original_parent_returns++;
  else face_errors++;
  if(face_parent_active[slot]){face_parent_checks++;if(memcmp(face_parent_frame[slot],ram+base+272u,118)||memcmp(face_parent_stack[slot],ram+base+416u,176))face_errors++;}
 }
}
int32_t observe(uint32_t pc){face_watch(pc);return face_retained_observe(pc);}
int observer_quiescent(void){return face_retained_quiescent()&&!face_pending_total();}
int face_dump(const char *path){
 FILE *file=fopen(path,"w");if(!file)return 1;
 fprintf(file,"{\"entries\":%llu,\"returns\":%llu,\"body_steps\":%llu,\"helpers\":%llu,\"errors\":%llu,\"pending\":%u,\"positive_speed_entries\":%llu,\"native_parent_returns\":%llu,\"original_parent_returns\":%llu,\"suspended_native_parent_checks\":%llu}\n",(unsigned long long)face_entries,(unsigned long long)face_returns,(unsigned long long)face_body_steps,(unsigned long long)face_helpers,(unsigned long long)face_errors,face_pending_total(),(unsigned long long)face_positive_speed,(unsigned long long)face_native_parent_returns,(unsigned long long)face_original_parent_returns,(unsigned long long)face_parent_checks);
 return fclose(file)!=0;
}
'''
 text=text.replace('FACE_ARENA',str(arena)+'u').replace('FACE_NATIVE_RETURN',str(ret)+'u').replace('NATIVE_FACE_RETURN',str(face_return)+'u')
 return text,source
