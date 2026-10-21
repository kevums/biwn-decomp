/* Read-only full-CPU/stack witness for the internal native E03A body.
 * Actual MMIO read/write order is a separate pinned-bus component proof.
 */
struct c26_slot {unsigned active;struct cpu before;uint32_t words[8],ret;};
static struct c26_slot c26_slots[101];
static uint64_t c26_entries,c26_returns,c26_errors,c26_original_entries,c26_original_returns;
static unsigned c26_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=c26_slots[i].active;return n;}
static void c26_load(struct cpu *s,uint32_t frame){
 for(unsigned i=0;i<16;i++)s->r[i]=rd32(frame+4u+4u*i);
 s->pc=rd32(frame+68u);s->usp=rd32(frame+72u);s->ssp=rd32(frame+76u);s->sr=rd16(frame+80u);
}
static void c26_watch(uint32_t pc){
 if(pc==0xe03au)c26_original_entries++;
 if(pc==0xe096u)c26_original_returns++;
 if(pc!=CLEAR_BEGIN&&pc!=CLEAR_END)return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){c26_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=CLEAR_ARENA+delta,frame=base+144u;
 struct c26_slot *p=&c26_slots[slot];struct cpu physical,logical;read_cpu(&physical);
 const unsigned offsets[8]={0,82,86,90,98,102,106,110};
 if(pc==CLEAR_BEGIN){
  if(p->active){c26_errors++;return;}
  memset(p,0,sizeof(*p));p->active=1;c26_entries++;c26_load(&p->before,frame);
  uint32_t sp=p->before.r[15];
  if(sp<4u||sp>0x200000u-12u){c26_errors++;p->active=0;return;}
  p->ret=rd32(sp);
  if(p->before.pc!=0xe03au||p->ret!=0x17e2cu||rd32(frame+114u)!=1u||rd32(frame+94u)||
     physical.r[15]<base+608u||physical.r[15]>base+816u||
     rd32(frame+(p->before.sr&0x2000u?76u:72u))!=sp)c26_errors++;
  for(unsigned i=0;i<8;i++)p->words[i]=rd32(frame+offsets[i]);
  return;
 }
 if(!p->active){c26_errors++;return;}
 c26_load(&logical,frame);
 if(logical.r[15]<4u||logical.r[15]>0x200000u-4u){c26_errors++;c26_returns++;p->active=0;return;}
 for(unsigned i=0;i<16;i++)if(logical.r[i]!=p->before.r[i])c26_errors++;
 if(logical.pc!=0xe096u||logical.sr!=(uint16_t)((p->before.sr&0xffe0u)|0x10u)||
    logical.usp!=p->before.usp||logical.ssp!=p->before.ssp||
    rd32(logical.r[15])!=p->ret||rd32(logical.r[15]-4u)!=p->before.r[0]||
    rd32(frame+114u)!=1u||rd32(frame+94u)||
    physical.r[15]<base+608u||physical.r[15]>base+816u)c26_errors++;
 for(unsigned i=0;i<8;i++)if(p->words[i]!=rd32(frame+offsets[i]))c26_errors++;
 c26_returns++;p->active=0;
}
int clear_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"entries\":%llu,\"returns\":%llu,\"errors\":%llu,\"pending\":%u,\"original_global_entries\":%llu,\"original_global_returns\":%llu}\n",
 (unsigned long long)c26_entries,(unsigned long long)c26_returns,(unsigned long long)c26_errors,c26_pending_total(),(unsigned long long)c26_original_entries,(unsigned long long)c26_original_returns);
 return fclose(f)!=0;
}
