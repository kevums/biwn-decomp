#include <stdint.h>
#include <stdio.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static struct cpu current;static uint8_t memory[0x200000],*ram=memory;
static uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
static uint16_t rd16(uint32_t a){return ((uint16_t)ram[a]<<8)|ram[a+1];}
static void read_cpu(struct cpu *s){*s=current;}
/* Read-only native17F14 witness with native185B2logical entry/end markers. */
struct r25_slot{unsigned active,helper,returned;struct cpu before,helper_cpu;uint32_t pointers[6],meta[3];};
static struct r25_slot r25_slots[101];
static uint64_t r25_entries,r25_returns,r25_helpers,r25_helper_returns,r25_errors;
static unsigned r25_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=r25_slots[i].active;return n;}
static void r25_load(struct cpu *s,uint32_t f){for(unsigned i=0;i<16;i++)s->r[i]=rd32(f+4u+4u*i);s->pc=rd32(f+68u);s->usp=rd32(f+72u);s->ssp=rd32(f+76u);s->sr=rd16(f+80u);}
static void r25_watch(uint32_t pc){
 if(pc!=1510468u&&pc!=1511878u&&pc!=1508558u&&pc!=1509786u)return;
 uint32_t delta=rd32(0xc0920u)-0xc0928u;if(delta>=0x19400u||(delta&1023u)){r25_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=1553344u+delta,f=base+144u;struct r25_slot *p=&r25_slots[slot];struct cpu physical,logical;read_cpu(&physical);
 if(pc==1510468u){
  if(p->active){r25_errors++;return;}memset(p,0,sizeof(*p));p->active=1;r25_entries++;r25_load(&p->before,f);
  if(p->before.r[15]<64u||p->before.r[15]>0x200000u-12u){r25_errors++;p->active=0;return;}
  if(p->before.pc!=0x17f14u||rd32(f+114u)!=1u||rd32(f+94u)||physical.r[15]<base+608u||physical.r[15]>base+816u||rd32(f+(p->before.sr&0x2000u?76u:72u))!=p->before.r[15])r25_errors++;
  for(unsigned i=0;i<3;i++){p->pointers[i]=rd32(0xbd83cu+4u*i);p->pointers[i+3]=rd32(0xbd830u+4u*i);p->meta[i]=rd32(f+82u+4u*i);}return;
 }
 if(!p->active){r25_errors++;return;}
 r25_load(&logical,f);
 if(pc==1508558u){
  if(p->helper||p->returned)r25_errors++;p->helper=1;r25_helpers++;
  struct cpu expected=p->before;expected.r[0]=p->pointers[3];expected.r[8]=0xbd838u;expected.r[9]=0xbd830u;expected.r[10]=0xbd834u;expected.r[15]-=16u;
  expected.sr=(uint16_t)((expected.sr&0xfff0u)|(p->pointers[4]?0u:4u)|(p->pointers[4]&0x80000000u?8u:0u));
  for(unsigned i=0;i<16;i++)if(logical.r[i]!=expected.r[i])r25_errors++;
  if(logical.pc!=0x185b2u||logical.sr!=expected.sr||rd32(expected.r[15])!=0x17f62u||rd32(expected.r[15]+4u)!=0x43da0u||rd32(expected.r[15]+8u)!=0x777c0u||rd32(expected.r[15]+12u)!=p->before.r[10])r25_errors++;
  for(unsigned i=0;i<3;i++)if(rd32(0xbd83cu+4u*i)!=p->pointers[(i+1u)%3u]||rd32(0xbd830u+4u*i)!=p->pointers[3u+(i+1u)%3u])r25_errors++;
  if(rd32(0x43daau)!=p->pointers[4])r25_errors++;
 }
 if(pc==1509786u){
  if(!p->helper||p->returned||logical.pc!=0x18852u||logical.r[15]!=p->before.r[15]-16u)r25_errors++;
  p->returned=1;p->helper_cpu=logical;r25_helper_returns++;
 }
 if(pc==1511878u){
  if(!p->helper||!p->returned||logical.pc!=0x17f66u||logical.sr!=p->helper_cpu.sr||logical.r[15]!=p->before.r[15]||logical.r[10]!=p->before.r[10]||rd32(f+114u)!=1u||rd32(f+94u)||physical.r[15]<base+608u||physical.r[15]>base+816u||rd32(f+(logical.sr&0x2000u?76u:72u))!=logical.r[15]||rd32(p->before.r[15]-16u)!=0x17f62u)r25_errors++;
  for(unsigned i=0;i<15;i++)if(i!=10u&&logical.r[i]!=p->helper_cpu.r[i])r25_errors++;
  if((logical.sr&0x2000u?logical.usp:logical.ssp)!=(p->before.sr&0x2000u?p->before.usp:p->before.ssp))r25_errors++;
  for(unsigned i=0;i<3;i++)if(rd32(f+82u+4u*i)!=p->meta[i])r25_errors++;
  r25_returns++;p->active=0;
 }
}
int rotation_dump(const char *path){FILE*f=fopen(path,"w");if(!f)return 1;fprintf(f,"{\"entries\":%llu,\"returns\":%llu,\"helper_entries\":%llu,\"helper_returns\":%llu,\"errors\":%llu,\"pending\":%u}\n",(unsigned long long)r25_entries,(unsigned long long)r25_returns,(unsigned long long)r25_helpers,(unsigned long long)r25_helper_returns,(unsigned long long)r25_errors,r25_pending_total());return fclose(f)!=0;}
/* Read-only completed-call ABI/guest-frame witness. Not a second packing oracle. */
struct d27_slot{unsigned active;struct cpu before;uint32_t bus,meta[8],ret,records,output;};
static struct d27_slot d27_slots[101];
static uint64_t d27_entries,d27_returns,d27_errors,d27_original_entries,d27_original_returns;
static unsigned d27_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=d27_slots[i].active;return n;}
static void d27_load(struct cpu *s,uint32_t f){for(unsigned i=0;i<16;i++)s->r[i]=rd32(f+4u+4u*i);s->pc=rd32(f+68u);s->usp=rd32(f+72u);s->ssp=rd32(f+76u);s->sr=rd16(f+80u);}
static void d27_watch(uint32_t pc){
 if(pc==0x185b2u)d27_original_entries++;if(pc==0x18852u)d27_original_returns++;
 if(pc!=1508558u&&pc!=1509786u)return;
 uint32_t delta=rd32(0xc0920u)-0xc0928u;if(delta>=0x19400u||(delta&1023u)){d27_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=1553344u+delta,f=base+144u;struct d27_slot*p=&d27_slots[slot];struct cpu physical,cpu;read_cpu(&physical);
 if(pc==1508558u){
  if(p->active){d27_errors++;return;}memset(p,0,sizeof(*p));p->active=1;d27_entries++;d27_load(&p->before,f);
  uint32_t sp=p->before.r[15];if(sp<64u||sp>0x200000u-12u){d27_errors++;p->active=0;return;}
  if(p->before.pc!=0x185b2u||rd32(f+114u)!=1u||rd32(f+94u)||physical.r[15]<base+608u||physical.r[15]>base+816u||(p->before.sr&0x2000u?p->before.ssp:p->before.usp)!=sp)d27_errors++;
  p->ret=rd32(sp);p->records=rd32(sp+4u);p->output=rd32(sp+8u);p->bus=rd32(f);
  if(p->records>0x200000u-36u||p->output>0x200000u-8u||(p->records&1u)||(p->output&1u)){d27_errors++;p->active=0;return;}
  for(unsigned i=0;i<8;i++)p->meta[i]=rd32(f+82u+4u*i);return;
 }
 if(!p->active){d27_errors++;return;}d27_load(&cpu,f);uint32_t sp=p->before.r[15],frame=sp-4u;
 if(cpu.pc!=0x18852u||cpu.r[15]!=sp||cpu.usp!=p->before.usp||cpu.ssp!=p->before.ssp||rd32(f+114u)!=1u||rd32(f+94u)||physical.r[15]<base+608u||physical.r[15]>base+816u||rd32(f)!=p->bus)d27_errors++;
 for(unsigned i=0;i<8;i++)if(rd32(f+82u+4u*i)!=p->meta[i])d27_errors++;
 if(rd32(sp)!=p->ret||rd32(sp+4u)!=p->records||rd32(sp+8u)!=p->output||rd32(frame)!=p->before.r[14])d27_errors++;
 for(unsigned i=2;i<=7;i++)if(cpu.r[i]!=p->before.r[i]||rd32(frame-56u+4u*(i-2u))!=p->before.r[i])d27_errors++;
 for(unsigned i=10;i<=13;i++)if(cpu.r[i]!=p->before.r[i]||rd32(frame-32u+4u*(i-10u))!=p->before.r[i])d27_errors++;
 if(cpu.r[14]!=p->before.r[14])d27_errors++;
 uint32_t field_end=rd32(frame-16u),distance=field_end-(p->records+18u),count=distance/36u;
 if(!count||distance%36u||count>(sp-60u)/4u||p->records>=0x200000u||distance>0x200000u-p->records){d27_errors++;goto done;}
 uint32_t table=sp-60u-count*4u,final_table=sp-60u,last_record=p->records+(count-1u)*36u;
 if(last_record>0x200000u-36u||cpu.r[8]<p->output+8u||cpu.r[8]>0x200000u||(cpu.r[8]&1u)){d27_errors++;goto done;}
 uint16_t expected_sr=(uint16_t)((p->before.sr&0xffe0u)|(final_table<(final_table-4u)?0x10u:0u));
 if(rd32(frame-4u)!=table||rd32(frame-12u)!=final_table||rd16(last_record)!=4u||cpu.r[1]!=4u||cpu.r[9]!=p->records+count*36u+6u||rd32(cpu.r[8]-4u)!=cpu.r[0]||cpu.sr!=expected_sr)d27_errors++;
 done:d27_returns++;p->active=0;
}
int display_dump(const char *path){FILE*f=fopen(path,"w");if(!f)return 1;fprintf(f,"{\"entries\":%llu,\"returns\":%llu,\"errors\":%llu,\"pending\":%u,\"original_global_entries\":%llu,\"original_global_returns\":%llu}\n",(unsigned long long)d27_entries,(unsigned long long)d27_returns,(unsigned long long)d27_errors,d27_pending_total(),(unsigned long long)d27_original_entries,(unsigned long long)d27_original_returns);return fclose(f)!=0;}

void snapshot(const void *raw,const struct cpu *s){memcpy(memory,raw,sizeof(memory));current=*s;}
void pc(uint32_t v){r25_watch(v);d27_watch(v);}
void clear(void){memset(r25_slots,0,sizeof(r25_slots));memset(d27_slots,0,sizeof(d27_slots));r25_entries=r25_returns=r25_helpers=r25_helper_returns=r25_errors=d27_entries=d27_returns=d27_errors=d27_original_entries=d27_original_returns=0;}
uint64_t stat(unsigned n){if(n==0)return r25_entries;if(n==1)return r25_returns;if(n==2)return r25_helpers;if(n==3)return r25_helper_returns;if(n==4)return r25_errors;if(n==5)return r25_pending_total();if(n==6)return d27_entries;if(n==7)return d27_returns;if(n==8)return d27_errors;if(n==9)return d27_pending_total();if(n==10)return d27_original_entries;return d27_original_returns;}
