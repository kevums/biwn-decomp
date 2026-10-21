"""Read-only three-root observer, retaining the prior game/GPU monitors."""
from pathlib import Path
import re
import task_arena_observer_source_v2 as regions
import check_native_deck_shared_v2 as kernel
ROOT=kernel.ROOT

def observer_source(build,parent):
 source=ROOT/'verification/native-Deck-coordinate-v2-route/20261019T182433.767570Z-candidate-1851/frame-acquire-observer.c';text=source.read_text()
 old=regions.checker(parent);assert text.count(old)==1
 checker=regions.checker(build);anchor='  if(!used[i]&&memcmp';assert anchor in checker
 guard=''.join(f'  if(memcmp(memory+p+{lo}u,expected+p+{lo}u-{build["resident_address"]}u,{hi-lo}u))errors++;\n'for lo,hi in kernel.FENCES[1:-1])
 text=text.replace(old,checker.replace(anchor,guard+anchor));text=text.replace(str(parent['heap_start'])+'u',str(build['heap_start'])+'u')
 symbols=build['shared_Deck_symbols'];names=list(kernel.LAYOUT);roots=[kernel.LAYOUT[n][0]for n in names]
 def array(values):return '{'+','.join(str(v)+'u'for v in values)+'}'
 helpers=[[0xe26c,0xe540],[0xe4c0,0x10c6e,0x10e72,0x10cb6,0x1102a],[0x11b4c,0x1186a,0x11d1a]]
 data=f'''
static const uint32_t shared_root[3]={array(roots)},shared_end[3]={array([0x11e64,0x11d1a,0x1186a])};
static const uint32_t shared_entry[3]={array([symbols['biwn_v2_'+n]for n in names])},shared_return[3]={array([symbols['biwn_v2_'+n+'_return']for n in names])};
static const uint32_t shared_helper_return[3]={array([symbols['biwn_v2_'+n+'_helper_return']for n in names])},shared_capture_end[3]={array([symbols['biwn_v2_'+n+'_capture_end']for n in names])};
static const uint32_t shared_fallback[3]={array([symbols['biwn_v2_'+n+'_original_fallback']for n in names])};
static const uint32_t shared_offset[3]={array([kernel.LAYOUT[n][1]for n in names])},shared_low[3]={array([kernel.LAYOUT[n][2]for n in names])},shared_top[3]={array([kernel.LAYOUT[n][3]for n in names])};
static const uint32_t shared_helpers[3][5]={{{','.join(array(h+[0]*(5-len(h)))for h in helpers)}}};
static uint64_t shared_public[3],shared_entries[3],shared_returns[3],shared_original[3],shared_fallbacks[3],shared_calls[3],shared_helper_returns[3],shared_C_observations[3],shared_errors,shared_C_outside;
static uint32_t shared_min[3]={array([kernel.LAYOUT[n][3]for n in names])};
static unsigned shared_pending[3][101];static struct cpu shared_incoming[3][101];
static unsigned shared_pending_total(void){{unsigned n=0;for(unsigned k=0;k<3;k++)for(unsigned i=0;i<101;i++)n+=shared_pending[k][i];return n;}}
static void shared_watch(uint32_t pc){{
 unsigned relevant=pc>={build['shared_Deck_code_address']}u&&pc<{build['shared_Deck_code_address']+build['shared_Deck_code_bytes']}u;
 for(unsigned k=0;k<3;k++){{if(pc>=shared_root[k]&&pc<shared_end[k])relevant=1;for(unsigned h=0;h<5;h++)if(pc&&pc==shared_helpers[k][h])relevant=1;}}
 if(!relevant)return;
 for(unsigned k=0;k<3;k++){{if(pc==shared_root[k])shared_public[k]++;else if(pc>shared_root[k]&&pc<shared_end[k])shared_original[k]++;}}
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){{for(unsigned k=0;k<3;k++)if(pc==shared_entry[k])shared_errors++;return;}}
 unsigned slot=delta/1024u;uint32_t base={build['deck_arena_address']}u+delta;struct cpu current;read_cpu(&current);
 for(unsigned k=0;k<3;k++){{
  uint32_t frame=base+shared_offset[k];
  if(pc==shared_entry[k]){{shared_entries[k]++;deck_used[slot]=1;if(shared_pending[k][slot])shared_errors++;else shared_incoming[k][slot]=current;shared_pending[k][slot]++;}}
  if(pc==shared_fallback[k])shared_fallbacks[k]++;
  if(!shared_pending[k][slot])continue;
  if(pc==shared_return[k]){{
   shared_returns[k]++;shared_pending[k][slot]--;
   if(current.r[15]!=shared_incoming[k][slot].r[15]||rd32(frame+114u)||rd32(frame+94u))shared_errors++;
   for(unsigned i=0;i<15;i++){{unsigned preserve=k==0?((i>=2&&i<=7)||(i>=10&&i<=14)):k==1?(i==2||i==3):(i==2||i==10);if(preserve&&current.r[i]!=shared_incoming[k][slot].r[i])shared_errors++;}}
  }}
  if(pc==shared_helper_return[k]){{shared_helper_returns[k]++;if(current.r[15]!=rd32(frame+106u)+4u)shared_errors++;}}
  for(unsigned h=0;h<5;h++)if(pc&&pc==shared_helpers[k][h]&&current.r[15]==rd32(frame+106u)&&rd32(current.r[15])==shared_helper_return[k])shared_calls[k]++;
  if(pc>=shared_helper_return[k]+12u&&pc<shared_capture_end[k]){{uint32_t phase=pc-shared_helper_return[k],off=(phase==12u||phase==16u)?0u:phase==20u?64u:4u;if(current.r[15]!=frame+off)shared_errors++;}}
 }}
 if(pc>={symbols['bit']}u&&pc<{build['shared_Deck_code_address']+build['shared_Deck_code_bytes']}u){{
  unsigned matched=0;for(unsigned k=0;k<3;k++)if(shared_pending[k][slot]&&current.r[15]>=base+shared_low[k]&&current.r[15]<=base+shared_top[k]){{matched++;shared_C_observations[k]++;uint32_t off=current.r[15]-base;if(off<shared_min[k])shared_min[k]=off;}}
  if(matched!=1u)shared_C_outside++;
 }}
}}
'''
 # Keep the old coordinate counters for the unchanged retained report format.
 watch=f'''static void native_deck_watch(uint32_t pc){{
 shared_watch(pc);
 if(pc==0x11d1au)deck_entries++;
 if(pc>0x11d1au&&pc<0x11e64u)deck_source_steps++;
 if(pc=={symbols['biwn_v2_coordinate']}u){{deck_native_entries++;uint32_t delta=rd32(0xc0920u)-0xc0928u;if(delta<0x19400u&&!(delta&1023u))deck_valid_entries++;else deck_invalid_entries++;}}
 if(pc=={symbols['biwn_v2_coordinate_return']}u)deck_native_returns++;
}}
'''
 text,n=re.subn(r'static void native_deck_watch\(uint32_t pc\)\{.*?\n\}',lambda _:data+watch,text,count=1,flags=re.S);assert n==1
 text=text.replace('int observer_quiescent(void){','static int retained_observer_quiescent(void){',1)
 text+='\nint observer_quiescent(void){return retained_observer_quiescent()&&!shared_pending_total();}\n'
 text+=r'''
int shared_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"errors\":%llu,\"pending\":%u,\"C_stack_outside\":%llu",(unsigned long long)shared_errors,shared_pending_total(),(unsigned long long)shared_C_outside);
 const uint64_t *arrays[]={shared_public,shared_entries,shared_returns,shared_original,shared_fallbacks,shared_calls,shared_helper_returns,shared_C_observations};
 const char *keys[]={"public_entries","native_entries","native_returns","original_body_steps","fallback_entries","helper_entries","helper_returns","C_stack_observations"};
 for(unsigned j=0;j<8;j++){fprintf(f,",\"%s\":[",keys[j]);for(unsigned k=0;k<3;k++)fprintf(f,"%s%llu",k?",":"",(unsigned long long)arrays[j][k]);fputc(']',f);}
 fprintf(f,",\"C_stack_low_offsets\":[%u,%u,%u]}\n",shared_min[0],shared_min[1],shared_min[2]);return fclose(f)!=0;
}
'''
 return text,source
