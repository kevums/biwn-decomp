"""Read-only outer-task witnesses, retaining the five-caller/face/geometry checks."""
import shared_deck_outer_compact_geometry_observer_v1 as prior
ROOT=prior.ROOT


def observer_source(build,parent):
    text,source=prior.observer_source(build,parent)
    symbols=build['outer_symbols'];arena=build['outer_arena_address'];deck=build['deck_arena_address']
    # Geometry now returns through the outer bridge in the candidate. Keep the
    # exact original11EE4 check for the control and resolve only the declared
    # native outer capture (matching task, guest SP and saved logical return).
    old='if(g4_return_word[slot]==0x11ee4u)g4_parent_returns++;else g4_errors++;'
    new=f'''if(g4_return_word[slot]==0x11ee4u ||
       (g4_return_word[slot]=={symbols['biwn_outer_helper_return']}u &&
        rd32({arena}u+slot*384u+16u+106u)==g4_incoming[slot].r[15] &&
        rd32({arena}u+slot*384u+16u+110u)==0x11ee4u))g4_parent_returns++;else g4_errors++;'''
    assert text.count(old)==1;text=text.replace(old,new).replace('original_outer_parent_returns','matched_outer_parent_returns')
    anchor='static unsigned native_deck_regions('
    assert text.count(anchor)==1;text=text.replace(anchor,'static uint8_t o6_used[101];\n'+anchor,1)
    lo=text.index(anchor);hi=text.index('static uint8_t deck_used',lo);body=text[lo:hi]
    extra=f'''
 for(unsigned i=0;i<101;i++){{
  uint32_t p={arena}u+i*384u;
  if(memcmp(memory+p,expected+p-{build['resident_address']}u,16)||memcmp(memory+p+136u,expected+p+136u-{build['resident_address']}u,8)||memcmp(memory+p+368u,expected+p+368u-{build['resident_address']}u,16))errors++;
  if(!o6_used[i]&&memcmp(memory+p,expected+p-{build['resident_address']}u,384))errors++;
  uint32_t q={deck}u+i*1024u+392u;
  if(memcmp(memory+q,expected+q-{build['resident_address']}u,4))errors++;
 }}
'''
    assert body.count(' return errors;')==1;text=text[:lo]+body.replace(' return errors;',extra+' return errors;')+text[hi:]
    assert text.count('int32_t observe(uint32_t pc)')==1
    text=text.replace('int32_t observe(uint32_t pc)','static int32_t o6_retained_observe(uint32_t pc)',1)
    assert text.count('int observer_quiescent(void)')==1
    text=text.replace('int observer_quiescent(void)','static int o6_retained_quiescent(void)',1)
    text+=r'''
/* O6_WATCHER_BEGIN: independently extracted by the fixture qualifier. */
static unsigned o6_mode[101],o6_helper_pending[101];
static struct cpu o6_incoming[101];
static uint32_t o6_entry_word[101],o6_call_sp[101],o6_logical_return[101];
static uint8_t o6_shadow[101][384];
static uint64_t o6_public,o6_native_entries,o6_native_returns,o6_original_returns,o6_original_steps,o6_fallbacks,o6_iterations,o6_original_iterations,o6_wait_slices,o6_errors,o6_C_outside,o6_C_observations,o6_protected_checks,o6_scheduler_boundaries;
static uint32_t o6_min=368u,o6_min_heap=0xffffffffu;
static uint64_t o6_helper_entries[13],o6_helper_returns[13];
static const uint32_t o6_targets[13]={0x10990u,0x11828u,0xe03au,0x10c6eu,0x1102au,0x11ad4u,0x16bf4u,0x10e72u,0x11d1au,0xe19eu,0xe202u,0xe098u,0x17f14u};
static const uint32_t o6_rets[13]={0x11e86u,0x11e8cu,0x11ec4u,0x11ed6u,0x11edcu,0x11ee4u,0x11f12u,0x11f32u,0x11f38u,0x11f4au,0x11f50u,0x11f5eu,0x11f64u};
static unsigned o6_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=o6_mode[i]!=0;return n;}
static unsigned o6_helper_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=o6_helper_pending[i]!=0;return n;}
static void o6_check_commit(unsigned slot,uint32_t pc,const struct cpu *cpu){
 uint32_t f=O6_ARENA+slot*384u+16u;
 for(unsigned i=0;i<16;i++)if(cpu->r[i]!=rd32(f+4u+4u*i))o6_errors++;
 if(cpu->sr!=rd16(f+80u))o6_errors++;
 if(pc==O6_RETURN){if(rd32(f+114u)||rd32(f+94u)||rd32(f+68u)!=0x11f6au)o6_errors++;}
 else if(rd32(f+114u)!=1u||rd32(f+94u)!=6u||rd32(f+68u)!=(pc==O6_ITERATION?0x11e86u:0x11f50u))o6_errors++;
}
static void o6_watch(uint32_t pc){
 unsigned relevant=(pc>=0x11e6cu&&pc<0x11f6cu)||(pc>=O6_CODE&&pc<O6_END)||pc==0xdf60u||pc==0xdf8cu;
 for(unsigned i=0;i<13;i++)if(pc==o6_targets[i])relevant=1;
 for(unsigned i=0;i<5;i++)if(pc==O6_INNER_RETURNS[i])relevant=1;
 if(!relevant)return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==0x11e6cu||pc==O6_ENTRY)o6_errors++;return;}
 unsigned slot=delta/1024u;struct cpu cpu;read_cpu(&cpu);uint32_t base=O6_ARENA+slot*384u,f=base+16u;
 if(pc==0x11e6cu){
  o6_public++;if(o6_mode[slot]){o6_errors++;return;}
  o6_mode[slot]=2;o6_incoming[slot]=cpu;o6_entry_word[slot]=rd32(cpu.r[15]);
 }
 if(pc==O6_ENTRY){o6_native_entries++;o6_used[slot]=1;if(o6_mode[slot]!=2u)o6_errors++;o6_mode[slot]=1;}
 if(!o6_mode[slot])return;
 uint32_t heap=rd32(0x112d64u);if(heap<o6_min_heap)o6_min_heap=heap;
 if(pc==O6_FALLBACK)o6_fallbacks++;
 if(pc>0x11e6cu&&pc<0x11f6cu)o6_original_steps++;
 if(pc==0xdf60u||pc==0xdf8cu)o6_scheduler_boundaries++;
 if(pc==0x11e86u&&o6_mode[slot]==2u)o6_original_iterations++;
 if(pc==O6_ITERATION||pc==O6_WAIT){
  if(o6_mode[slot]!=1u)o6_errors++;
  if(pc==O6_ITERATION)o6_iterations++;else o6_wait_slices++;
  o6_check_commit(slot,pc,&cpu);
 }
 if(o6_mode[slot]==1u && ((pc>=O6_ASM_END&&pc<O6_END)||(pc>=O6_CAPTURE_FIRST&&pc<O6_HELPER_RETURN)) && cpu.r[15]>=base&&cpu.r[15]<base+384u){
  o6_C_observations++;uint32_t off=cpu.r[15]-base;if(off<o6_min)o6_min=off;if(off<144u||off>368u)o6_C_outside++;
 }
 for(unsigned h=0;h<13;h++)if(pc==o6_targets[h]){
  uint32_t ret=rd32(cpu.r[15]);unsigned direct=0;
  if(o6_mode[slot]==1u){
   if(ret==O6_HELPER_RETURN&&rd32(f+106u)==cpu.r[15]){
    uint32_t csp=rd32(f+98u),cp=rd32(f+102u),logical=rd32(f+110u);
    if(csp<base+144u||csp+60u>base+368u||cp!=f+4u)o6_errors++;
    else if(rd32(cp+64u)!=pc)o6_errors++;
    if(logical!=o6_rets[h]&&!(h==3u&&logical==0x11f1au))o6_errors++;
    direct=1;o6_logical_return[slot]=logical;memcpy(o6_shadow[slot],ram+base,384);
   }
  }else if(ret==o6_rets[h]||(h==3u&&ret==0x11f1au)){direct=1;o6_logical_return[slot]=ret;}
  if(direct){if(o6_helper_pending[slot])o6_errors++;o6_helper_pending[slot]=h+1u;o6_call_sp[slot]=cpu.r[15];o6_helper_entries[h]++;}
 }
 unsigned tag=o6_helper_pending[slot];
 if(tag && ((o6_mode[slot]==1u&&pc==O6_HELPER_RETURN)||(o6_mode[slot]==2u&&pc==o6_logical_return[slot]))){
  if(cpu.r[15]!=o6_call_sp[slot]+4u)o6_errors++;
  if(o6_mode[slot]==1u){if(memcmp(o6_shadow[slot],ram+base,384))o6_errors++;o6_protected_checks++;}
  o6_helper_returns[tag-1u]++;o6_helper_pending[slot]=0;
 }
 if(o6_mode[slot]==1u&&o6_helper_pending[slot])for(unsigned i=0;i<5;i++)if(pc==O6_INNER_RETURNS[i]){
  if(memcmp(o6_shadow[slot],ram+base,384))o6_errors++;o6_protected_checks++;
 }
 if(pc==O6_RETURN||pc==0x11f6au){
  if(o6_helper_pending[slot]||cpu.r[15]!=o6_incoming[slot].r[15]||cpu.r[14]!=o6_incoming[slot].r[14]||rd32(cpu.r[15])!=o6_entry_word[slot])o6_errors++;
  if(pc==O6_RETURN){o6_native_returns++;o6_check_commit(slot,pc,&cpu);}else o6_original_returns++;
  o6_mode[slot]=0;
 }
}
/* O6_WATCHER_END */
int32_t observe(uint32_t pc){o6_watch(pc);return o6_retained_observe(pc);}
int observer_quiescent(void){return o6_retained_quiescent()&&!o6_pending_total()&&!o6_helper_pending_total();}
int outer_dump(const char *path){
 FILE *file=fopen(path,"w");if(!file)return 1;
 fprintf(file,"{\"public_entries\":%llu,\"native_entries\":%llu,\"native_returns\":%llu,\"original_returns\":%llu,\"original_body_steps\":%llu,\"fallbacks\":%llu,\"native_iteration_boundaries\":%llu,\"original_iteration_boundaries\":%llu,\"native_wait_slices\":%llu,\"errors\":%llu,\"pending\":%u,\"helper_pending\":%u,\"C_stack_outside\":%llu,\"C_stack_observations\":%llu,\"C_stack_low_offset\":%u,\"protected_frame_checks\":%llu,\"scheduler_boundaries_reached\":%llu,\"minimum_heap_free_while_outer_active\":%u",(unsigned long long)o6_public,(unsigned long long)o6_native_entries,(unsigned long long)o6_native_returns,(unsigned long long)o6_original_returns,(unsigned long long)o6_original_steps,(unsigned long long)o6_fallbacks,(unsigned long long)o6_iterations,(unsigned long long)o6_original_iterations,(unsigned long long)o6_wait_slices,(unsigned long long)o6_errors,o6_pending_total(),o6_helper_pending_total(),(unsigned long long)o6_C_outside,(unsigned long long)o6_C_observations,o6_min,(unsigned long long)o6_protected_checks,(unsigned long long)o6_scheduler_boundaries,o6_min_heap);
 const uint64_t *arrays[]={o6_helper_entries,o6_helper_returns};const char *keys[]={"helper_entries","helper_returns"};
 for(unsigned j=0;j<2;j++){fprintf(file,",\"%s\":[",keys[j]);for(unsigned h=0;h<13;h++)fprintf(file,"%s%llu",h?",":"",(unsigned long long)arrays[j][h]);fputc(']',file);}
 fputs("}\n",file);return fclose(file)!=0;
}
'''
    array='{'+','.join(str(build['shared_Deck_symbols']['biwn_v4_'+name+'_return'])+'u'for name in ['coordinate','input','face','scan','geometry'])+'}'
    constants=dict(O6_ARENA=arena,O6_CODE=build['outer_code_address'],O6_END=build['outer_code_address']+build['outer_code_bytes'],O6_RETURN=symbols['biwn_outer_return'],O6_ENTRY=symbols['biwn_outer_entry'],O6_FALLBACK=symbols['biwn_outer_original_fallback'],O6_ITERATION=symbols['biwn_outer_iteration_boundary'],O6_WAIT=symbols['biwn_outer_wait_boundary'],O6_ASM_END=symbols['biwn_outer_asm_end'],O6_CAPTURE_FIRST=symbols['biwn_outer_capture_initialize'],O6_HELPER_RETURN=symbols['biwn_outer_helper_return'])
    text=text.replace('/* O6_WATCHER_BEGIN:', 'static const uint32_t o6_inner_returns[5]='+array+';\n/* O6_WATCHER_BEGIN:').replace('O6_INNER_RETURNS','o6_inner_returns')
    import re
    for name,value in constants.items():text=re.sub(r'\b'+name+r'\b',str(value)+'u',text)
    return text,source
