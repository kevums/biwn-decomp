#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static uint8_t owned[0x200000],*ram=owned;
static struct cpu current;
static unsigned arena_active[102],arena_used[102];
static uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
static uint16_t rd16(uint32_t a){return ((uint16_t)ram[a]<<8)|ram[a+1];}
static void read_cpu(struct cpu *o){*o=current;}
static unsigned task_id_valid(uint32_t task){return task>=0xc0928u&&task<0xd9d28u&&!((task-0xc0928u)&1023u);}
static unsigned task_arena_slot(uint32_t task){return task_id_valid(task)?(task-0xc0928u)/1024u:101u;}
static void arena_check_guards(void){}
/* Read-only resource/GPU scratch lifetime and input-call commitments.
 * Context/shadow arrays below are observer-owned, never guest memory. */
static unsigned r39_live,i39_live,r39_helpers_live;
static unsigned r39_mode[102],r39_helper[102],i39_pending[102],i39_route[102];
static struct cpu r39_incoming[102],i39_incoming[102];
static uint32_t r39_word[102],r39_low[102],r39_high[102],i39_entry_sp[102];
static uint8_t r39_shadow[102][224];
static uint64_t r39_public,r39_entries,r39_returns,r39_errors,r39_alias_errors,r39_C_outside,r39_C_observations,r39_guest_observations,r39_parked_checks,r39_helper_entries,r39_helper_returns;
static uint64_t i39_calls,i39_native,i39_original,i39_returns,i39_errors,i39_C_outside,i39_C_observations;
static uint32_t r39_C_low=240u,r39_guest_depth,i39_guest_depth;
static const uint32_t r39_GPU_entries[8]={1470772u,1470906u,1471040u,1471174u,1471308u,1471442u,1471576u,1471710u};
static const uint32_t r39_switches[4]={1569038u,1569164u,1569294u,1569436u};
static const uint32_t r39_helper_rets[4]={1569064u,1569190u,1569320u,1569478u};
static unsigned r39_pending_total(void){unsigned n=0;for(unsigned i=0;i<102;i++)n+=r39_mode[i]!=0;return n;}
static unsigned r39_helper_total(void){unsigned n=0;for(unsigned i=0;i<102;i++)n+=r39_helper[i]!=0;return n;}
static unsigned i39_pending_total(void){unsigned n=0;for(unsigned i=0;i<102;i++)n+=i39_pending[i]!=0;return n;}
static void r39_watch(uint32_t pc){
 if(!r39_live&&!i39_live&&pc!=0x1af04u&&pc!=0x1a266u&&pc!=1568888u)return;
 uint32_t task=rd32(0xc0920u);unsigned slot=task_arena_slot(task);struct cpu cpu;read_cpu(&cpu);
 uint32_t base=1471936u+slot*256u,ctx=base+168u,sp=cpu.r[15];
 if(r39_helpers_live)for(unsigned i=0;i<102;i++)if(r39_helper[i]){
  if(r39_high[i]<=r39_low[i]||r39_high[i]-r39_low[i]>224u)r39_errors++;
  else{r39_parked_checks++;if(memcmp(ram+r39_low[i],r39_shadow[i],r39_high[i]-r39_low[i]))r39_errors++;}
 }
 for(unsigned k=0;k<8;k++)if(pc==r39_GPU_entries[k]&&r39_mode[slot]==1u){r39_alias_errors++;r39_errors++;}
 if(pc==0x1af04u){
  r39_public++;
  if(r39_mode[slot]){r39_alias_errors++;r39_errors++;}
  else{r39_live++;r39_mode[slot]=2u;r39_incoming[slot]=cpu;r39_word[slot]=rd32(sp);}
 }
 if(pc==1568888u){
  r39_entries++;
  if(r39_mode[slot]!=2u){r39_errors++;if(!r39_mode[slot])r39_live++;}
  if(arena_active[slot]){r39_alias_errors++;r39_errors++;}
  r39_mode[slot]=1u;arena_active[slot]=1u;arena_used[slot]=1u;
 }
 if(r39_mode[slot]==1u){
  if(!(cpu.sr&0x2000u)){
   if(sp>=base+16u&&sp<=base+240u){r39_C_observations++;if(sp-base<r39_C_low)r39_C_low=sp-base;}
   else if(task_id_valid(task)&&sp>=task+64u&&sp<=task+1024u){
    r39_guest_observations++;uint32_t initial=r39_incoming[slot].r[15];
    if(initial>=sp&&initial-sp>r39_guest_depth)r39_guest_depth=initial-sp;
   }else r39_C_outside++;
  }
  for(unsigned k=0;k<4;k++)if(pc==r39_switches[k]){
   if(r39_helper[slot]||cpu.r[8]!=ctx||sp<base+16u||sp>ctx||rd32(ctx+68u)!=sp||rd32(ctx+60u)!=r39_incoming[slot].r[15])r39_errors++;
   else{r39_helper[slot]=k+1u;r39_low[slot]=sp;r39_high[slot]=ctx+72u;memcpy(r39_shadow[slot],ram+sp,ctx+72u-sp);r39_helper_entries++;r39_helpers_live++;}
  }
  for(unsigned k=0;k<4;k++)if(pc==r39_helper_rets[k]){
   if(r39_helper[slot]!=k+1u)r39_errors++;else{static const unsigned bytes[4]={4,4,4,20};if(sp!=r39_incoming[slot].r[15]-24u-bytes[k])r39_errors++;r39_helper[slot]=0;r39_helper_returns++;r39_helpers_live--;}
  }
  if(pc==1569022u){
   static const unsigned saved[6]={2,3,4,5,10,11};
   for(unsigned i=0;i<6;i++)if(cpu.r[saved[i]]!=r39_incoming[slot].r[saved[i]])r39_errors++;
   for(unsigned i=0;i<15;i++){
    unsigned guest_saved=0;for(unsigned j=0;j<6;j++)guest_saved|=i==saved[j];
    if(!guest_saved&&cpu.r[i]!=rd32(ctx+4u*i))r39_errors++;
   }
   if(sp!=r39_incoming[slot].r[15]||rd32(sp)!=r39_word[slot]||rd32(ctx+60u)!=sp||cpu.sr!=rd16(ctx+66u)||r39_helper[slot])r39_errors++;
   r39_returns++;r39_mode[slot]=0;r39_live--;arena_active[slot]=0;arena_check_guards();
  }
 }
 if(pc==0x1a266u){
  if(i39_pending[slot])i39_errors++;else i39_live++;
  i39_pending[slot]=1;i39_route[slot]=0;i39_incoming[slot]=cpu;i39_entry_sp[slot]=sp-4u;i39_calls++;
 }
 if(i39_pending[slot]){
  if(pc==1568732u&&(sp!=i39_entry_sp[slot]||rd32(sp)!=0x1a26cu))i39_errors++;
  if(pc==1568588u){if(i39_route[slot])i39_errors++;i39_route[slot]=1;i39_native++;}
  if(pc==0x191f4u){if(i39_route[slot])i39_errors++;i39_route[slot]=2;i39_original++;}
  if(i39_route[slot]==1u&&pc>=1558308u&&pc<1568888u){
   if((cpu.sr&0x2000u)||!task_id_valid(task)||sp<task+64u||sp>task+1024u)i39_C_outside++;
   else{i39_C_observations++;if(i39_entry_sp[slot]>=sp&&i39_entry_sp[slot]-sp>i39_guest_depth)i39_guest_depth=i39_entry_sp[slot]-sp;}
  }
  if(pc==0x1a26cu){
   static const unsigned saved[11]={2,3,4,5,6,7,10,11,12,13,14};
   for(unsigned i=0;i<11;i++)if(cpu.r[saved[i]]!=i39_incoming[slot].r[saved[i]])i39_errors++;
   if(sp!=i39_incoming[slot].r[15]||!i39_route[slot])i39_errors++;
   i39_returns++;i39_pending[slot]=0;i39_live--;
  }
 }
}
int resource_input_dump(const char *path){
 FILE *file=fopen(path,"w");if(!file)return 1;
 fprintf(file,"{\"resource_public\":%llu,\"resource_native_entries\":%llu,\"resource_returns\":%llu,\"resource_errors\":%llu,\"resource_alias_errors\":%llu,\"resource_C_outside\":%llu,\"resource_pending\":%u,\"resource_helper_pending\":%u,\"resource_helper_entries\":%llu,\"resource_helper_returns\":%llu,\"resource_parked_checks\":%llu,\"resource_C_observations\":%llu,\"resource_C_low\":%u,\"resource_guest_depth\":%u,\"input_calls\":%llu,\"input_native\":%llu,\"input_original\":%llu,\"input_returns\":%llu,\"input_errors\":%llu,\"input_C_outside\":%llu,\"input_pending\":%u,\"input_C_observations\":%llu,\"input_guest_depth\":%u}\n",
 (unsigned long long)r39_public,(unsigned long long)r39_entries,(unsigned long long)r39_returns,(unsigned long long)r39_errors,(unsigned long long)r39_alias_errors,(unsigned long long)r39_C_outside,r39_pending_total(),r39_helper_total(),(unsigned long long)r39_helper_entries,(unsigned long long)r39_helper_returns,(unsigned long long)r39_parked_checks,(unsigned long long)r39_C_observations,r39_C_low,r39_guest_depth,(unsigned long long)i39_calls,(unsigned long long)i39_native,(unsigned long long)i39_original,(unsigned long long)i39_returns,(unsigned long long)i39_errors,(unsigned long long)i39_C_outside,i39_pending_total(),(unsigned long long)i39_C_observations,i39_guest_depth);
 fclose(file);return 0;
}

void fixture_reset(void){ram=owned;memset(owned,0,sizeof(owned));memset(&current,0,sizeof(current));memset(r39_mode,0,sizeof(r39_mode));memset(r39_helper,0,sizeof(r39_helper));memset(i39_pending,0,sizeof(i39_pending));memset(i39_route,0,sizeof(i39_route));memset(r39_incoming,0,sizeof(r39_incoming));memset(i39_incoming,0,sizeof(i39_incoming));memset(r39_word,0,sizeof(r39_word));memset(r39_low,0,sizeof(r39_low));memset(r39_high,0,sizeof(r39_high));memset(i39_entry_sp,0,sizeof(i39_entry_sp));memset(r39_shadow,0,sizeof(r39_shadow));memset(arena_active,0,sizeof(arena_active));memset(arena_used,0,sizeof(arena_used));r39_public=0;r39_entries=0;r39_returns=0;r39_errors=0;r39_alias_errors=0;r39_C_outside=0;r39_C_observations=0;r39_guest_observations=0;r39_parked_checks=0;r39_helper_entries=0;r39_helper_returns=0;i39_calls=0;i39_native=0;i39_original=0;i39_returns=0;i39_errors=0;i39_C_outside=0;i39_C_observations=0;r39_guest_depth=0;i39_guest_depth=0;r39_live=0;i39_live=0;r39_helpers_live=0;r39_C_low=240;}
void fixture_put(uint32_t a,uint32_t v){ram[a]=v>>24;ram[a+1]=v>>16;ram[a+2]=v>>8;ram[a+3]=v;}
void fixture_word(uint32_t a,uint16_t v){ram[a]=v>>8;ram[a+1]=v;}
void fixture_reg(unsigned i,uint32_t v){if(i<16)current.r[i]=v;}
void fixture_sr(uint16_t v){current.sr=v;}
void fixture_PC(uint32_t pc){current.pc=pc;}
void fixture_observe(uint32_t pc){r39_watch(pc);}
void fixture_CPU(void *out){memcpy(out,&current,sizeof(current));}
void fixture_RAM(void *out){memcpy(out,ram,0x200000);}
void fixture_live(void *memory,const struct cpu *cpu,uint32_t pc){ram=memory;current=*cpu;r39_watch(pc);}
void fixture_active(unsigned slot,unsigned value){if(slot<102)arena_active[slot]=value;}
uint64_t fixture_stat(unsigned n){
 if(n==0)return r39_errors;if(n==1)return r39_alias_errors;if(n==2)return r39_C_outside;if(n==3)return r39_pending_total();
 if(n==4)return r39_helper_total();if(n==5)return r39_returns;if(n==6)return r39_helper_returns;if(n==7)return i39_errors;
 if(n==8)return i39_C_outside;if(n==9)return i39_pending_total();if(n==10)return i39_returns;if(n==11)return i39_native;
 if(n==12)return i39_original;if(n==13)return r39_parked_checks;if(n==14)return r39_helper_entries;return 0;
}
