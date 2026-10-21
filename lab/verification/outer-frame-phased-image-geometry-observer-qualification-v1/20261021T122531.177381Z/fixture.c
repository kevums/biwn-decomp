
#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu {uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static struct cpu current;
static uint8_t memory[0x200000],*ram=memory,o6_used[101];
static uint32_t rd32(uint32_t a){return ((uint32_t)memory[a]<<24)|((uint32_t)memory[a+1]<<16)|((uint32_t)memory[a+2]<<8)|memory[a+3];}
static uint16_t rd16(uint32_t a){return ((uint16_t)memory[a]<<8)|memory[a+1];}
static void read_cpu(struct cpu *out){*out=current;}
static const uint32_t o6_inner_returns[5]={1498300u,1498504u,1498708u,1499116u,1499320u};
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
 uint32_t f=1673664u+slot*384u+16u;
 for(unsigned i=0;i<16;i++)if(cpu->r[i]!=rd32(f+4u+4u*i))o6_errors++;
 if(cpu->sr!=rd16(f+80u))o6_errors++;
 if(pc==1552572u){if(rd32(f+114u)||rd32(f+94u)||rd32(f+68u)!=0x11f6au)o6_errors++;}
 else if(rd32(f+114u)!=1u||rd32(f+94u)!=6u||rd32(f+68u)!=(pc==1552550u?0x11e86u:0x11f50u))o6_errors++;
}
static void o6_watch(uint32_t pc){
 unsigned relevant=(pc>=0x11e6cu&&pc<0x11f6cu)||(pc>=1552248u&&pc<1558308u)||pc==0xdf60u||pc==0xdf8cu;
 for(unsigned i=0;i<13;i++)if(pc==o6_targets[i])relevant=1;
 for(unsigned i=0;i<5;i++)if(pc==o6_inner_returns[i])relevant=1;
 if(!relevant)return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==0x11e6cu||pc==1552248u)o6_errors++;return;}
 unsigned slot=delta/1024u;struct cpu cpu;read_cpu(&cpu);uint32_t base=1673664u+slot*384u,f=base+16u;
 if(pc==0x11e6cu){
  o6_public++;if(o6_mode[slot]){o6_errors++;return;}
  o6_mode[slot]=2;o6_incoming[slot]=cpu;o6_entry_word[slot]=rd32(cpu.r[15]);
 }
 if(pc==1552248u){o6_native_entries++;o6_used[slot]=1;if(o6_mode[slot]!=2u)o6_errors++;o6_mode[slot]=1;}
 if(!o6_mode[slot])return;
 uint32_t heap=rd32(0x112d64u);if(heap<o6_min_heap)o6_min_heap=heap;
 if(pc==1552416u)o6_fallbacks++;
 if(pc>0x11e6cu&&pc<0x11f6cu)o6_original_steps++;
 if(pc==0xdf60u||pc==0xdf8cu)o6_scheduler_boundaries++;
 if(pc==0x11e86u&&o6_mode[slot]==2u)o6_original_iterations++;
 if(pc==1552550u||pc==1552532u){
  if(o6_mode[slot]!=1u)o6_errors++;
  if(pc==1552550u)o6_iterations++;else o6_wait_slices++;
  o6_check_commit(slot,pc,&cpu);
 }
 if(o6_mode[slot]==1u && ((pc>=1553342u&&pc<1558308u)||(pc>=1552576u&&pc<1553278u)) && cpu.r[15]>=base&&cpu.r[15]<base+384u){
  o6_C_observations++;uint32_t off=cpu.r[15]-base;if(off<o6_min)o6_min=off;if(off<144u||off>368u)o6_C_outside++;
 }
 for(unsigned h=0;h<13;h++)if(pc==o6_targets[h]){
  uint32_t ret=rd32(cpu.r[15]);unsigned direct=0;
  if(o6_mode[slot]==1u){
   if(ret==1553278u&&rd32(f+106u)==cpu.r[15]){
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
 if(tag && ((o6_mode[slot]==1u&&pc==1553278u)||(o6_mode[slot]==2u&&pc==o6_logical_return[slot]))){
  if(cpu.r[15]!=o6_call_sp[slot]+4u)o6_errors++;
  if(o6_mode[slot]==1u){if(memcmp(o6_shadow[slot],ram+base,384))o6_errors++;o6_protected_checks++;}
  o6_helper_returns[tag-1u]++;o6_helper_pending[slot]=0;
 }
 if(o6_mode[slot]==1u&&o6_helper_pending[slot])for(unsigned i=0;i<5;i++)if(pc==o6_inner_returns[i]){
  if(memcmp(o6_shadow[slot],ram+base,384))o6_errors++;o6_protected_checks++;
 }
 if(pc==1552572u||pc==0x11f6au){
  if(o6_helper_pending[slot]||cpu.r[15]!=o6_incoming[slot].r[15]||cpu.r[14]!=o6_incoming[slot].r[14]||rd32(cpu.r[15])!=o6_entry_word[slot])o6_errors++;
  if(pc==1552572u){o6_native_returns++;o6_check_commit(slot,pc,&cpu);}else o6_original_returns++;
  o6_mode[slot]=0;
 }
}

void fixture_reset(void){
 memset(memory,0,sizeof(memory));memset(&current,0,sizeof(current));memset(o6_used,0,sizeof(o6_used));
 memset(o6_mode,0,sizeof(o6_mode));memset(o6_helper_pending,0,sizeof(o6_helper_pending));memset(o6_incoming,0,sizeof(o6_incoming));
 memset(o6_entry_word,0,sizeof(o6_entry_word));memset(o6_call_sp,0,sizeof(o6_call_sp));memset(o6_logical_return,0,sizeof(o6_logical_return));memset(o6_shadow,0,sizeof(o6_shadow));
 memset(o6_helper_entries,0,sizeof(o6_helper_entries));memset(o6_helper_returns,0,sizeof(o6_helper_returns));
 o6_public=o6_native_entries=o6_native_returns=o6_original_returns=o6_original_steps=o6_fallbacks=o6_iterations=o6_original_iterations=o6_wait_slices=o6_errors=o6_C_outside=o6_C_observations=o6_protected_checks=o6_scheduler_boundaries=0;o6_min=368;o6_min_heap=0xffffffffu;
}
void fixture_register(unsigned i,uint32_t v){if(i<16)current.r[i]=v;}
void fixture_sr(uint16_t v){current.sr=v;}
void fixture_long(uint32_t a,uint32_t v){memory[a]=(uint8_t)(v>>24);memory[a+1]=(uint8_t)(v>>16);memory[a+2]=(uint8_t)(v>>8);memory[a+3]=(uint8_t)v;}
void fixture_word(uint32_t a,uint16_t v){memory[a]=(uint8_t)(v>>8);memory[a+1]=(uint8_t)v;}
void fixture_pc(uint32_t pc){o6_watch(pc);}
uint64_t fixture_stat(unsigned n){

 if(n==0)return o6_errors;if(n==1)return o6_pending_total();if(n==2)return o6_helper_pending_total();if(n==3)return o6_C_outside;
 if(n==4)return o6_public;if(n==5)return o6_native_entries;if(n==6)return o6_native_returns;if(n==7)return o6_original_returns;
 if(n==8)return o6_helper_entries[1];if(n==9)return o6_helper_returns[1];if(n==10)return o6_C_observations;if(n==11)return o6_protected_checks;return 0;
}
