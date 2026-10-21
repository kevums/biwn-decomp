/* Read-only completed-call ABI/guest-frame witness. Not a second packing oracle. */
struct d27_slot{unsigned active;struct cpu before;uint32_t bus,meta[8],ret,records,output;};
static struct d27_slot d27_slots[101];
static uint64_t d27_entries,d27_returns,d27_errors,d27_original_entries,d27_original_returns;
static unsigned d27_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=d27_slots[i].active;return n;}
static void d27_load(struct cpu *s,uint32_t f){for(unsigned i=0;i<16;i++)s->r[i]=rd32(f+4u+4u*i);s->pc=rd32(f+68u);s->usp=rd32(f+72u);s->ssp=rd32(f+76u);s->sr=rd16(f+80u);}
static void d27_watch(uint32_t pc){
 if(pc==0x185b2u)d27_original_entries++;if(pc==0x18852u)d27_original_returns++;
 if(pc!=DISPLAY_BEGIN&&pc!=DISPLAY_END)return;
 uint32_t delta=rd32(0xc0920u)-0xc0928u;if(delta>=0x19400u||(delta&1023u)){d27_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=DISPLAY_ARENA+delta,f=base+144u;struct d27_slot*p=&d27_slots[slot];struct cpu physical,cpu;read_cpu(&physical);
 if(pc==DISPLAY_BEGIN){
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
