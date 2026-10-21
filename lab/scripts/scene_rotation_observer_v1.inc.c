/* Read-only witness for native17F14 and its retained185B2 capture. */
struct r25_slot {
 unsigned active,helper,returned;struct cpu before,helper_cpu;
 uint32_t pointers[6],meta[3];
};
static struct r25_slot r25_slots[101];
static uint64_t r25_entries,r25_returns,r25_helpers,r25_helper_returns,r25_errors;
static unsigned r25_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=r25_slots[i].active;return n;}
static void r25_load(struct cpu *s,uint32_t frame){
 for(unsigned i=0;i<16;i++)s->r[i]=rd32(frame+4u+4u*i);
 s->pc=rd32(frame+68u);s->usp=rd32(frame+72u);s->ssp=rd32(frame+76u);s->sr=rd16(frame+80u);
}
static void r25_watch(uint32_t pc){
 if(pc!=ROTATION_BEGIN&&pc!=ROTATION_END&&pc!=0x185b2u&&pc!=ROTATION_HELPER_RETURN)return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==ROTATION_BEGIN||pc==ROTATION_END)r25_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=ROTATION_ARENA+delta,frame=base+144u;
 struct r25_slot *p=&r25_slots[slot];struct cpu cpu,logical;read_cpu(&cpu);
 if(pc==ROTATION_BEGIN){
  if(p->active){r25_errors++;return;}
  memset(p,0,sizeof(*p));p->active=1;r25_entries++;r25_load(&p->before,frame);
  if(p->before.r[15]<16u||p->before.r[15]>0x200000u){r25_errors++;p->active=0;return;}
  if(p->before.pc!=0x17f14u||p->before.r[15]<16u||p->before.r[15]>0x200000u||
     rd32(frame+114u)!=1u||rd32(frame+94u)||cpu.r[15]<base+608u||cpu.r[15]>base+816u||
     rd32(frame+(p->before.sr&0x2000u?76u:72u))!=p->before.r[15])r25_errors++;
  for(unsigned i=0;i<3;i++){p->pointers[i]=rd32(0xbd83cu+4u*i);p->pointers[i+3]=rd32(0xbd830u+4u*i);p->meta[i]=rd32(frame+82u+4u*i);}
  return;
 }
 if(!p->active){if(pc==ROTATION_END)r25_errors++;return;}
 if(pc==0x185b2u){
  if(cpu.r[15]>0x200000u-16u){r25_errors++;return;}
  if(p->helper||p->returned)r25_errors++;
  p->helper=1;r25_helpers++;
  struct cpu expected=p->before;expected.r[0]=p->pointers[3];expected.r[8]=0xbd838u;
  expected.r[9]=0xbd830u;expected.r[10]=0xbd834u;expected.r[15]-=16u;
  expected.sr=(uint16_t)((expected.sr&0xfff0u)|(p->pointers[4]?0u:4u)|(p->pointers[4]&0x80000000u?8u:0u));
  for(unsigned i=0;i<16;i++)if(cpu.r[i]!=expected.r[i])r25_errors++;
  if(cpu.sr!=expected.sr||rd32(cpu.r[15])!=ROTATION_HELPER_RETURN||
     rd32(cpu.r[15]+4u)!=0x43da0u||rd32(cpu.r[15]+8u)!=0x777c0u||
     rd32(cpu.r[15]+12u)!=p->before.r[10]||rd32(frame+106u)!=cpu.r[15]||
     rd32(frame+110u)!=0x17f62u||rd32(frame+102u)!=frame+4u||
     rd32(frame+98u)<base+608u||rd32(frame+98u)>base+816u)r25_errors++;
  for(unsigned i=0;i<3;i++){
   if(rd32(0xbd83cu+4u*i)!=p->pointers[(i+1u)%3u]||
      rd32(0xbd830u+4u*i)!=p->pointers[3u+(i+1u)%3u])r25_errors++;
  }
  if(rd32(0x43daau)!=p->pointers[4])r25_errors++;
 }
 if(pc==ROTATION_HELPER_RETURN){
  if(!p->helper||p->returned||cpu.r[15]!=p->before.r[15]-12u)r25_errors++;
  p->returned=1;p->helper_cpu=cpu;r25_helper_returns++;
 }
 if(pc==ROTATION_END){
  r25_load(&logical,frame);
  if(!p->helper||!p->returned||logical.pc!=0x17f66u||logical.sr!=p->helper_cpu.sr||
     logical.r[15]!=p->before.r[15]||logical.r[10]!=p->before.r[10]||
     rd32(frame+114u)!=1u||rd32(frame+94u)||cpu.r[15]<base+608u||cpu.r[15]>base+816u||
     rd32(frame+(logical.sr&0x2000u?76u:72u))!=logical.r[15]||
     rd32(p->before.r[15]-16u)!=0x17f62u)r25_errors++;
  for(unsigned i=0;i<15;i++)if(i!=10u&&logical.r[i]!=p->helper_cpu.r[i])r25_errors++;
  if((logical.sr&0x2000u?logical.usp:logical.ssp)!=(p->before.sr&0x2000u?p->before.usp:p->before.ssp))r25_errors++;
  for(unsigned i=0;i<3;i++)if(rd32(frame+82u+4u*i)!=p->meta[i])r25_errors++;
  r25_returns++;p->active=0;
 }
}
int rotation_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"entries\":%llu,\"returns\":%llu,\"helper_entries\":%llu,\"helper_returns\":%llu,\"errors\":%llu,\"pending\":%u}\n",
 (unsigned long long)r25_entries,(unsigned long long)r25_returns,(unsigned long long)r25_helpers,(unsigned long long)r25_helper_returns,(unsigned long long)r25_errors,r25_pending_total());
 return fclose(f)!=0;
}
