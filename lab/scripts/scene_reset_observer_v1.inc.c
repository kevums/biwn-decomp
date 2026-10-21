/* Read-only logical input-service reset witness. No emulated RAM writes. */
struct reset_write {uint32_t a,v;unsigned w;};
struct reset_pending {
 unsigned active,marker,n;uint32_t frame,csp,ret,guest_ret,meta[4];
 struct cpu expected;struct reset_write writes[25];
};
static struct reset_pending reset_slots[101];
static uint64_t reset_entries,reset_returns,reset_markers,reset_errors;
static uint64_t reset_original_entries,reset_original_returns;
static unsigned reset_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=reset_slots[i].active;return n;}
static uint32_t reset_read(unsigned a,unsigned w){
 a&=0xffffffu;if(a+w>0x200000u){reset_errors++;return 0;}
 return w==2?rd16(a):rd32(a);
}
static uint32_t reset_model_read(struct reset_pending *p,uint32_t a,unsigned w){
 uint32_t v=0;a&=0xffffffu;
 for(unsigned byte=0;byte<w;byte++){
  uint32_t at=a+byte;uint8_t b=at<0x200000u?ram[at]:0;
  if(at>=0x200000u)reset_errors++;
  for(unsigned j=0;j<p->n;j++)if(at>=p->writes[j].a&&at<p->writes[j].a+p->writes[j].w)
   b=(uint8_t)(p->writes[j].v>>(8u*(p->writes[j].w-1u-(at-p->writes[j].a))));
  v=(v<<8)|b;
 }
 return v;
}
static void reset_model_write(struct reset_pending *p,uint32_t a,unsigned w,uint32_t v){
 if(p->n>=25u){reset_errors++;return;}
 p->writes[p->n++]=(struct reset_write){a,v,w};
}
static void reset_load_cpu(struct cpu *cpu,uint32_t f){
 for(unsigned i=0;i<16;i++)cpu->r[i]=rd32(f+4u+4u*i);
 cpu->pc=rd32(f+68u);cpu->usp=rd32(f+72u);cpu->ssp=rd32(f+76u);cpu->sr=rd16(f+80u);
}
static void reset_watch(uint32_t pc){
 if(pc==0x1102au)reset_original_entries++;
 if(pc==0x110d2u)reset_original_returns++;
 if(pc!=RESET_DISPATCH&&pc!=RESET_MARKER&&!reset_pending_total())return;
 struct cpu cpu;read_cpu(&cpu);uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==RESET_MARKER)reset_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=RESET_ARENA+delta,f=base+144u;
 struct reset_pending *p=&reset_slots[slot];
 if(pc==RESET_DISPATCH&&cpu.r[15]+20u<=0x200000u&&rd32(cpu.r[15]+12u)==0x1102au){
  if(p->active){reset_errors++;return;}
  if(cpu.r[15]<base+608u||cpu.r[15]+20u>base+816u||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+8u)!=f+4u||rd32(cpu.r[15]+16u)!=RESET_INPUT_HELPER_RETURN||rd32(f+114u)!=1u||rd32(f+94u)||rd32(f+68u)!=0x1102au){reset_errors++;return;}
  memset(p,0,sizeof(*p));p->active=1;p->frame=f;p->csp=cpu.r[15];p->ret=rd32(cpu.r[15]);reset_load_cpu(&p->expected,f);p->guest_ret=reset_read(p->expected.r[15],4);
  if(p->guest_ret!=0x11d14u)reset_errors++;
  for(unsigned i=0;i<4;i++)p->meta[i]=rd32(f+(i?78u+4u*i:0u));
  for(unsigned i=0;i<3;i++){reset_model_write(p,0x47b88u+8u*i,2,0x4000u);for(unsigned j=1;j<4;j++)reset_model_write(p,0x47b88u+8u*i+2u*j,2,0);}
  reset_model_write(p,0x47bdau,2,0);reset_model_write(p,0x47bdcu,2,0);reset_model_write(p,0x47bdeu,2,0);
  uint32_t descriptor=reset_model_read(p,0x400e6u,4);p->expected.r[8]=descriptor;
  for(unsigned i=0;i<3;i++)reset_model_write(p,0x400ecu+4u*i,4,reset_model_read(p,descriptor+4u+4u*i,4));
  const uint32_t clears[7]={0x40100u,0x400fcu,0x400f8u,0x40104u,0x40406u,0x4040au,0x40402u};for(unsigned i=0;i<7;i++)reset_model_write(p,clears[i],4,0);
  p->expected.sr=(uint16_t)((p->expected.sr&0xfff0u)|4u);p->expected.pc=0x110d2u;
 }
 if(pc==RESET_MARKER){
  if(!p->active||p->marker||cpu.r[15]<base+608u||cpu.r[15]+8u>base+816u||rd32(cpu.r[15]+4u)!=f)reset_errors++;
  else{p->marker=1;reset_entries++;reset_markers++;}
 }
 if(p->active&&pc==p->ret){
  struct cpu actual;reset_load_cpu(&actual,f);
  if(!p->marker||cpu.r[15]!=p->csp+4u||rd32(f+114u)!=1u||rd32(f+94u)||p->n!=25u||actual.pc!=p->expected.pc||actual.usp!=p->expected.usp||actual.ssp!=p->expected.ssp||actual.sr!=p->expected.sr)reset_errors++;
  for(unsigned i=0;i<16;i++)if(actual.r[i]!=p->expected.r[i])reset_errors++;
  for(unsigned i=0;i<4;i++)if(p->meta[i]!=rd32(f+(i?78u+4u*i:0u)))reset_errors++;
  if(reset_read(actual.r[15],4)!=p->guest_ret)reset_errors++;
  for(unsigned i=0;i<p->n;i++)if(reset_read(p->writes[i].a,p->writes[i].w)!=p->writes[i].v)reset_errors++;
  reset_returns++;p->active=0;
 }
}
int reset_dump(const char *path){FILE *f=fopen(path,"w");if(!f)return 1;fprintf(f,"{\"entries\":%llu,\"returns\":%llu,\"markers\":%llu,\"errors\":%llu,\"pending\":%u,\"original_global_entries\":%llu,\"original_global_returns\":%llu}\n",(unsigned long long)reset_entries,(unsigned long long)reset_returns,(unsigned long long)reset_markers,(unsigned long long)reset_errors,reset_pending_total(),(unsigned long long)reset_original_entries,(unsigned long long)reset_original_returns);return fclose(f)!=0;}
