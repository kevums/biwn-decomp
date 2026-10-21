#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static struct cpu current;static uint8_t memory[0x200000],*ram=memory;
static uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
static uint16_t rd16(uint32_t a){return ((uint16_t)ram[a]<<8)|ram[a+1];}
static void read_cpu(struct cpu *o){*o=current;}
/* R33_RECORDS_WATCH_BEGIN: read-only scene record/source/provider boundaries. */
static unsigned r33_pending[101],r33_provider[101];
static struct cpu r33_incoming[101];
static uint32_t r33_guest_sp[101];
static uint8_t r33_frame[101][118],r33_stack[101][208];
static uint64_t r33_entries,r33_returns,r33_errors,r33_original_steps,r33_protected;
static uint64_t r33_provider_entries[2],r33_provider_returns[2];
static unsigned r33_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=r33_pending[i]+r33_provider[i];return n;}
static void r33_read_logical(uint32_t f,struct cpu *cpu){
 for(unsigned i=0;i<16;i++)cpu->r[i]=rd32(f+4u+i*4u);
 cpu->pc=rd32(f+68u);cpu->usp=rd32(f+72u);cpu->ssp=rd32(f+76u);cpu->sr=rd16(f+80u);
}
static void r33_watch(uint32_t pc){
 if(pc!=1514302u&&pc!=1518906u&&pc!=1500816u&&pc!=0xe3e0u&&pc!=0xe220u&&!(pc>=0x170a0u&&pc<0x17326u))return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==1514302u||pc==1518906u)r33_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=1570240u+delta,f=base+144u;
 if(pc==1514302u){
  r33_entries++;if(r33_pending[slot]||r33_provider[slot])r33_errors++;
  r33_pending[slot]=1;r33_read_logical(f,&r33_incoming[slot]);
  if(r33_incoming[slot].pc!=0x170a0u||rd32(f+114u)!=1u||rd32(f+94u))r33_errors++;
  if((r33_incoming[slot].sr&0x2000u?r33_incoming[slot].ssp:r33_incoming[slot].usp)!=r33_incoming[slot].r[15])r33_errors++;
 }
 if(!r33_pending[slot]){if(pc==1518906u)r33_errors++;return;}
 if(pc>=0x170a0u&&pc<0x17326u)r33_original_steps++;
 if(pc==0xe3e0u||pc==0xe220u){
  struct cpu physical;read_cpu(&physical);
  if(physical.r[15]==rd32(f+106u)&&rd32(physical.r[15])==1500816u){
   unsigned tag=pc==0xe3e0u?1u:2u;uint32_t logical_return=rd32(f+110u);
   if(r33_provider[slot]||rd32(f+102u)!=f+4u||rd32(f+68u)!=pc||rd32(f+64u)!=physical.r[15]||rd32(f+114u)!=1u||rd32(f+94u))r33_errors++;
   if(rd32(f+(rd16(f+80u)&0x2000u?76u:72u))!=physical.r[15])r33_errors++;
   if(tag==1u?(logical_return!=0x170d8u&&logical_return!=0x17166u):logical_return!=0x172c4u)r33_errors++;
   r33_provider[slot]=tag;r33_guest_sp[slot]=physical.r[15];r33_provider_entries[tag-1u]++;
   memcpy(r33_frame[slot],ram+f,118);memcpy(r33_stack[slot],ram+base+608u,208);
  }
 }
 if(pc==1500816u){
  unsigned tag=r33_provider[slot];struct cpu physical;read_cpu(&physical);
  if(!tag){r33_errors++;return;}
  if(physical.r[15]!=r33_guest_sp[slot]+4u||memcmp(r33_frame[slot],ram+f,118)||memcmp(r33_stack[slot],ram+base+608u,208))r33_errors++;
  r33_provider_returns[tag-1u]++;r33_protected++;r33_provider[slot]=0;
 }
 if(pc==1518906u){
  struct cpu current;r33_read_logical(f,&current);r33_returns++;
  if(r33_provider[slot]||current.pc!=0x17324u||rd32(f+114u)!=1u||rd32(f+94u)||current.r[15]!=r33_incoming[slot].r[15]||current.usp!=r33_incoming[slot].usp||current.ssp!=r33_incoming[slot].ssp)r33_errors++;
  if((current.sr&0xffe0u)!=(r33_incoming[slot].sr&0xffe0u))r33_errors++;
  for(unsigned i=0;i<16;i++)if(((i>=2&&i<=4)||(i>=10&&i<=13))&&current.r[i]!=r33_incoming[slot].r[i])r33_errors++;
  r33_pending[slot]=0;
 }
}

void clear(void){memset(memory,0,sizeof(memory));memset(&current,0,sizeof(current));memset(r33_pending,0,sizeof(r33_pending));memset(r33_provider,0,sizeof(r33_provider));memset(r33_provider_entries,0,sizeof(r33_provider_entries));memset(r33_provider_returns,0,sizeof(r33_provider_returns));r33_entries=r33_returns=r33_errors=r33_original_steps=r33_protected=0;}
void put(uint32_t a,uint32_t v){ram[a]=v>>24;ram[a+1]=v>>16;ram[a+2]=v>>8;ram[a+3]=v;}
void word(uint32_t a,uint16_t v){ram[a]=v>>8;ram[a+1]=v;}
void reg(unsigned n,uint32_t v){current.r[n]=v;}
void pc(uint32_t a){current.pc=a;r33_watch(a);}
void snapshot(const void *raw,const struct cpu *cpu){memcpy(memory,raw,sizeof(memory));current=*cpu;}
uint64_t stat(unsigned n){switch(n){case 0:return r33_errors;case 1:return r33_pending_total();case 2:return r33_entries;case 3:return r33_returns;case 4:return r33_protected;case 5:return r33_provider_entries[0];case 6:return r33_provider_returns[0];case 7:return r33_provider_entries[1];case 8:return r33_provider_returns[1];default:return r33_original_steps;}}
