/* Read-only gameplay trace. The retained core executes every instruction. */
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

struct cpu { uint32_t r[16],pc,usp,ssp; uint16_t sr; };
struct event { uint32_t frame,pc; struct cpu cpu; uint32_t X,Z,mode,floor,scene,tile; };
typedef char event_size_check[sizeof(struct event)==112?1:-1];
typedef void (*read_cpu_fn)(struct cpu *);
static const unsigned char *ram,*payload;
static uint32_t payload_size,frame,last_marker_frame;
static read_cpu_fn read_cpu;
static FILE *events;
static unsigned candidate,errors;
static uint64_t steps,entry_copies,copy_errors,heap_inits,resident_steps;
static uint64_t old_rng_steps,old_math_steps,old_keypad_steps,marker_steps,event_count;
static uint64_t rng_entries[8],math_entries[3],boundary_entries[4];
static uint32_t heap_base;
static const uint32_t rng[]={0x1a6e0,0x1a6f8,0x1a77c,0x1a7f4,0x1a87a,0x1a8c6,0x1a8e2,0x1a8f8,0x1a91e};
static const uint32_t math[]={0xe540,0xe588,0xe60a};
static const uint32_t boundaries[]={0x18e92,0x1a0f8,0x20f0c,0x20f78};

static uint32_t rd32(uint32_t address) {
    if(address>0x1ffffc){errors++;return 0;}
    return ((uint32_t)ram[address]<<24)|((uint32_t)ram[address+1]<<16)|
           ((uint32_t)ram[address+2]<<8)|ram[address+3];
}
static uint32_t rd16(uint32_t address) {
    if(address>0x1ffffe){errors++;return 0;}
    return ((uint32_t)ram[address]<<8)|ram[address+1];
}
int begin_observe(const void *memory,read_cpu_fn reader,int selected,
                  const void *code,uint32_t length,const char *path) {
    ram=memory;read_cpu=reader;candidate=(unsigned)selected;
    payload=code;payload_size=length;events=fopen(path,"wb");
    return events?0:1;
}
void set_frame(uint32_t value){frame=value;}
static void emit(uint32_t pc) {
    struct event record;
    memset(&record,0,sizeof(record));record.frame=frame;record.pc=pc;
    read_cpu(&record.cpu);record.X=rd32(0x49c50);record.Z=rd32(0x49c56);
    record.mode=rd16(0x49c60);record.floor=rd16(0x49c62);
    record.scene=rd16(0x49c64);record.tile=rd16(0x49c8c);
    if(fwrite(&record,sizeof(record),1,events)!=1)errors++;
    event_count++;
}

static uint8_t o6_used[101];
static unsigned native_deck_regions(const uint8_t *memory,const uint8_t *expected,const uint8_t *used){
 unsigned errors=0;
 if(memcmp(memory+1437120u,expected,34816u))errors++;
 if(memcmp(memory+1498048u,expected+60928u,46336u))errors++;
 for(unsigned i=0;i<101;i++){
  uint32_t p=1544384u+i*1024u;
  if(memcmp(memory+p,expected+p-1437120u,16)||memcmp(memory+p+1008u,expected+p+1008u-1437120u,16))errors++;
  if(memcmp(memory+p+136u,expected+p+136u-1437120u,8u))errors++;
  if(memcmp(memory+p+264u,expected+p+264u-1437120u,8u))errors++;
  if(memcmp(memory+p+400u,expected+p+400u-1437120u,16u))errors++;
  if(memcmp(memory+p+592u,expected+p+592u-1437120u,16u))errors++;
  if(memcmp(memory+p+816u,expected+p+816u-1437120u,16u))errors++;
  if(!used[i]&&memcmp(memory+p,expected+p-1437120u,1024))errors++;
 }

 for(unsigned i=0;i<101;i++){
  uint32_t p=1647808u+i*576u;
  if(memcmp(memory+p,expected+p-1437120u,16)||memcmp(memory+p+136u,expected+p+136u-1437120u,8)||memcmp(memory+p+560u,expected+p+560u-1437120u,16))errors++;
  if(!o6_used[i]&&memcmp(memory+p,expected+p-1437120u,576))errors++;
  uint32_t q=1544384u+i*1024u+392u;
  if(memcmp(memory+q,expected+q-1437120u,4))errors++;
 }
 return errors;
}

static uint8_t deck_used[101];
static uint64_t deck_entries,deck_native_entries,deck_valid_entries,deck_native_returns,deck_source_steps,deck_invalid_entries;

static const uint32_t shared_root[5]={72986u,72524u,71786u,71720u,72404u},shared_end[5]={73316u,72986u,72404u,71786u,72524u};
static const uint32_t shared_entry[5]={1498112u,1498316u,1498520u,1498724u,1498928u},shared_return[5]={1498300u,1498504u,1498708u,1498912u,1499116u};
static const uint32_t shared_helper_return[5]={1500178u,1500240u,1500302u,1500364u,1500426u},shared_capture_end[5]={1500232u,1500294u,1500356u,1500418u,1500480u};
static const uint32_t shared_fallback[5]={1499132u,1499148u,1499176u,1499164u,1499192u};
static const uint32_t shared_offset[5]={16u,144u,144u,272u,16u},shared_low[5]={832u,608u,608u,416u,832u},shared_top[5]={1008u,816u,816u,592u,1008u};
static const uint32_t shared_helpers[5][5]={{57964u,58688u,0u,0u,0u},{58560u,68718u,69234u,68790u,69674u},{68718u,68790u,0u,0u,0u},{72524u,71786u,72986u,0u,0u},{57964u,0u,0u,0u,0u}};
static uint64_t shared_public[5],shared_entries[5],shared_returns[5],shared_original[5],shared_fallbacks[5],shared_calls[5],shared_helper_returns[5],shared_C_observations[5],shared_errors,shared_C_outside;
static uint32_t shared_min[5]={1008u,816u,816u,592u,1008u};
static unsigned shared_pending[5][101];static struct cpu shared_incoming[5][101];
static unsigned shared_pending_total(void){unsigned n=0;for(unsigned k=0;k<5;k++)for(unsigned i=0;i<101;i++)n+=shared_pending[k][i];return n;}
static void shared_watch(uint32_t pc){
 unsigned relevant=pc>=1498112u&&pc<1538174u;
 for(unsigned k=0;k<5;k++){if(pc>=shared_root[k]&&pc<shared_end[k])relevant=1;for(unsigned h=0;h<5;h++)if(pc&&pc==shared_helpers[k][h])relevant=1;}
 if(!relevant)return;
 for(unsigned k=0;k<5;k++){if(pc==shared_root[k])shared_public[k]++;else if(pc>shared_root[k]&&pc<shared_end[k])shared_original[k]++;}
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){for(unsigned k=0;k<5;k++)if(pc==shared_entry[k])shared_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=1544384u+delta;struct cpu current;read_cpu(&current);
 for(unsigned k=0;k<5;k++){
  uint32_t frame=base+shared_offset[k];
  if(pc==shared_entry[k]){shared_entries[k]++;deck_used[slot]=1;if(shared_pending[k][slot])shared_errors++;else shared_incoming[k][slot]=current;shared_pending[k][slot]++;}
  if(pc==shared_fallback[k])shared_fallbacks[k]++;
  if(!shared_pending[k][slot])continue;
  if(pc==shared_return[k]){
   shared_returns[k]++;shared_pending[k][slot]--;
   if(current.r[15]!=shared_incoming[k][slot].r[15]||rd32(frame+114u)||rd32(frame+94u))shared_errors++;
   for(unsigned i=0;i<15;i++){unsigned preserve=k==0?((i>=2&&i<=7)||(i>=10&&i<=14)):k==1?(i==2||i==3):k==2?((i>=2&&i<=4)||(i>=10&&i<=14)):k==3?(i==2||i==10):(i==2||i==3);if(preserve&&current.r[i]!=shared_incoming[k][slot].r[i])shared_errors++;}
  }
  if(pc==shared_helper_return[k]){shared_helper_returns[k]++;if(current.r[15]!=rd32(frame+106u)+4u)shared_errors++;}
  for(unsigned h=0;h<5;h++)if(pc&&pc==shared_helpers[k][h]&&current.r[15]==rd32(frame+106u)&&rd32(current.r[15])==shared_helper_return[k])shared_calls[k]++;
  if(pc>=shared_helper_return[k]+12u&&pc<shared_capture_end[k]){uint32_t phase=pc-shared_helper_return[k],off=(phase==12u||phase==16u)?0u:phase==20u?64u:4u;if(current.r[15]!=frame+off)shared_errors++;}
 }
 if(pc>=1500488u&&pc<1538174u){
  unsigned matched=0;for(unsigned k=0;k<5;k++)if(shared_pending[k][slot]&&current.r[15]>=base+shared_low[k]&&current.r[15]<=base+shared_top[k]){matched++;shared_C_observations[k]++;uint32_t off=current.r[15]-base;if(off<shared_min[k])shared_min[k]=off;}
  if(matched!=1u)shared_C_outside++;
 }
}
static void native_deck_watch(uint32_t pc){
 shared_watch(pc);
 if(pc==0x11d1au)deck_entries++;
 if(pc>0x11d1au&&pc<0x11e64u)deck_source_steps++;
 if(pc==1498112u){deck_native_entries++;uint32_t delta=rd32(0xc0920u)-0xc0928u;if(delta<0x19400u&&!(delta&1023u))deck_valid_entries++;else deck_invalid_entries++;}
 if(pc==1498300u)deck_native_returns++;
}

/* Read-only task ownership, arena guards, and complete pool-initializer return. */
static unsigned arena_active[102],arena_used[102],arena_ready;
static uint32_t arena_max_depth;
static uint64_t arena_errors,arena_guard_checks,arena_stack_observations,arena_unused_checks,arena_code_checks;
static unsigned task_id_valid(uint32_t task){return task>=0xc0928u&&task<0xd9d28u&&((task-0xc0928u)&0x3ffu)==0;}
static unsigned task_arena_slot(uint32_t task){return task_id_valid(task)?(task-0xc0928u)/1024u:101u;}
static uint32_t task_arena_top(uint32_t task){return 1471936u+task_arena_slot(task)*256u+240u;}
static unsigned task_original_stack_valid(uint32_t task,uint32_t sp){return task_id_valid(task)&&sp>=task+38u&&sp<=task+0x400u;}
static unsigned task_arena_stack_valid(uint32_t task,uint32_t sp){uint32_t top=task_arena_top(task);return arena_active[task_arena_slot(task)]&&sp>=top-224u&&sp<=top;}
static unsigned task_stack_valid(uint32_t task,uint32_t sp){return task_original_stack_valid(task,sp)||task_arena_stack_valid(task,sp);}
static void arena_check_guards(void){
 if(!arena_ready){arena_errors++;return;}
 for(unsigned i=0;i<102;i++){uint32_t b=1471936u+i*256u;arena_guard_checks++;for(unsigned j=0;j<16;j++)if(ram[b+j]!=0xa5u||ram[b+240u+j]!=0xa5u)arena_errors++;}
}
static void arena_finish(void){
 arena_check_guards();arena_code_checks++;
 arena_errors+=native_deck_regions(ram,payload,deck_used);
 if(deck_valid_entries!=deck_native_returns)arena_errors++;
 for(unsigned i=0;i<102;i++){
  if(arena_active[i])arena_errors++;
  if(!arena_used[i]){arena_unused_checks++;uint32_t at=1471936u+i*256u;if(memcmp(ram+at,payload+at-0x15edc0u,256))arena_errors++;}
 }
}
static struct cpu pool_incoming;
static unsigned pool_pending;
static uint8_t pool_expected[0x19400];
static uint64_t pool_entries,pool_native_entries,pool_returns,pool_errors,pool_old_steps,pool_source_steps;
static void pool_put(unsigned at,uint32_t value,unsigned width){for(unsigned i=0;i<width;i++)pool_expected[at+i]=(uint8_t)(value>>(8u*(width-1u-i)));}
static void watch_pool_arena(uint32_t pc){
 native_deck_watch(pc);
 if(pc==0x400au){arena_ready=1;arena_check_guards();}
 if(pc==0xdd40u){
  if(pool_pending)pool_errors++;pool_pending=1;pool_entries++;read_cpu(&pool_incoming);
  if(!(pool_incoming.sr&0x2000u))pool_errors++;
  memcpy(pool_expected,ram+0xc0928u,sizeof(pool_expected));
  for(unsigned i=1;i<=100;i++)pool_put(i*1024u,i==100?0:0xc0928u+(i+1u)*1024u,4);
  pool_put(0,0xc0928u,4);pool_put(4,0xc0928u,4);pool_put(8,0xddccu,4);pool_put(12,0xc0d28u,4);
  pool_put(20,0,2);pool_put(26,0,4);pool_put(22,0,4);pool_put(34,0,4);
 }
 if(pc==1469212u)pool_native_entries++;
 if(pc>0xdd40u&&pc<0xddccu)pool_old_steps++;
 if(pc>=1468880u&&pc<1469286u)pool_source_steps++;
 if(pc==0xddccu&&pool_pending){
  struct cpu current;read_cpu(&current);pool_returns++;
  uint16_t sr=(uint16_t)(pool_incoming.sr&0xdff0u);
  for(unsigned i=0;i<16;i++){uint32_t want=pool_incoming.r[i];if(i==0)want=(want&0xffff0000u)|sr;else if(i==8)want=0xc0928u;else if(i==9||i==15)want=0xc0d28u;if(current.r[i]!=want)pool_errors++;}
  if(current.sr!=sr||current.usp!=0xc0d28u||current.ssp!=pool_incoming.ssp)pool_errors++;
  if(rd32(0x80)!=0xde08u||rd32(0x88)!=0xdeb6u||rd32(0x8c)!=0xdee2u||rd32(0x90)!=0xdef6u||rd32(0x20)!=0xddfeu||rd32(0xc0920u)!=0xc0928u||rd32(0xc0924u)!=0xc0d28u)pool_errors++;
  if(memcmp(ram+0xc0928u,pool_expected,sizeof(pool_expected)))pool_errors++;
  pool_pending=0;
 }
}
static void arena_dump(FILE *file){
 fprintf(file,",\"deck_entries\":%llu,\"deck_native_entries\":%llu,\"deck_native_returns\":%llu,\"deck_source_steps\":%llu,\"deck_invalid_entries\":%llu",(unsigned long long)deck_entries,(unsigned long long)deck_native_entries,(unsigned long long)deck_native_returns,(unsigned long long)deck_source_steps,(unsigned long long)deck_invalid_entries);

 arena_finish();
 fprintf(file,",\"arena_errors\":%llu,\"arena_guard_checks\":%llu,\"arena_stack_observations\":%llu,\"arena_unused_checks\":%llu,\"arena_code_checks\":%llu,\"arena_max_depth\":%u",(unsigned long long)arena_errors,(unsigned long long)arena_guard_checks,(unsigned long long)arena_stack_observations,(unsigned long long)arena_unused_checks,(unsigned long long)arena_code_checks,arena_max_depth);
 fprintf(file,",\"pool_entries\":%llu,\"pool_native_entries\":%llu,\"pool_returns\":%llu,\"pool_errors\":%llu,\"pool_old_steps\":%llu,\"pool_source_steps\":%llu,\"pool_pending\":%u",(unsigned long long)pool_entries,(unsigned long long)pool_native_entries,(unsigned long long)pool_returns,(unsigned long long)pool_errors,(unsigned long long)pool_old_steps,(unsigned long long)pool_source_steps,pool_pending);
 fputs(",\"arena_used_slots\":[",file);unsigned comma=0;for(unsigned i=0;i<102;i++)if(arena_used[i]){fprintf(file,"%s%u",comma?",":"",i);comma=1;}fputc(']',file);
}


static int32_t (*next_owner)(uint32_t);
void set_next_owner(void *fn){next_owner=(int32_t(*)(uint32_t))fn;}
struct acquire_call {uint32_t task;unsigned pending;struct cpu incoming;uint32_t min_sp;};
static struct acquire_call acquire_slots[256];
static uint64_t acquire_entries,acquire_native_entries,acquire_returns,acquire_old_steps;
static uint64_t acquire_monitor_errors,acquire_native_steps,acquire_loader_calls;
static uint64_t acquire_user_stack_observations,acquire_user_stack_outside;
static unsigned acquire_pending,acquire_slot_count;
static uint32_t acquire_user_min_headroom=0xffffffffu,acquire_max_private_depth;
static struct acquire_call *acquire_slot(uint32_t task){
    for(unsigned i=0;i<acquire_slot_count;i++)if(acquire_slots[i].task==task)return &acquire_slots[i];
    if(acquire_slot_count<256){struct acquire_call *slot=&acquire_slots[acquire_slot_count++];slot->task=task;return slot;}
    acquire_monitor_errors++;return NULL;
}
static void watch_acquire(uint32_t pc){
    if(!acquire_pending&&pc!=0x1ac68&&!(pc>=0x162722u&&pc<0x162d64u)&&!(pc>0x1ac68&&pc<0x1ae56))return;
    uint32_t task=rd32(0xc0920);struct acquire_call *slot=NULL;struct cpu current;
    if(pc==0x1ac68){
        slot=acquire_slot(task);if(!slot)return;
        if(slot->pending)acquire_monitor_errors++;
        read_cpu(&slot->incoming);slot->pending=1;slot->min_sp=slot->incoming.r[15];acquire_entries++;acquire_pending++;emit(pc);
    }
    if(pc>0x1ac68&&pc<0x1ae56)acquire_old_steps++;
    if(pc==0x162724u)acquire_native_entries++;
    if(pc>=0x162722u&&pc<0x162d64u)acquire_native_steps++;
    for(unsigned i=0;i<acquire_slot_count;i++)if(acquire_slots[i].pending&&acquire_slots[i].task==task){slot=&acquire_slots[i];break;}
    if(!slot||!slot->pending)return;
    read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];acquire_user_stack_observations++;
        if(!task_stack_valid(task,sp))acquire_user_stack_outside++;
        else if(task_original_stack_valid(task,sp)&&sp-task-38u<acquire_user_min_headroom)acquire_user_min_headroom=sp-task-38u;
        if(sp<slot->min_sp)slot->min_sp=sp;
    }
    if(pc==0x1b044){
        uint32_t sp=current.r[15],s=slot->incoming.r[15];acquire_loader_calls++;emit(pc);
        if(sp!=s-68u||rd32(sp+12)!=s-8u||rd32(sp+20)!=0u||rd32(sp+16)!=current.r[5]||rd32(sp+8)!=current.r[12]||rd32(sp+4)!=current.r[9]+current.r[10])acquire_monitor_errors++;
    }
    if(pc==0x162762u||pc==0x1ae54){
        uint32_t s=slot->incoming.r[15];acquire_returns++;emit(pc);
        const unsigned saved[]={2,3,4,5,6,7,10,11,12};
        for(unsigned i=0;i<9;i++)if(current.r[saved[i]]!=slot->incoming.r[saved[i]]||rd32(s-44u+4u*i)!=slot->incoming.r[saved[i]])acquire_monitor_errors++;
        if(current.r[14]!=slot->incoming.r[14]||current.r[15]!=s||rd32(s-4u)!=slot->incoming.r[14])acquire_monitor_errors++;
        uint32_t low=current.r[0]&0xffffu;uint16_t nz=(uint16_t)(low==0?4:(low&0x8000u)?8:0);
        if((current.sr&15u)!=nz||(current.sr&0xffe0u)!=(slot->incoming.sr&0xffe0u))acquire_monitor_errors++;
        if(s-slot->min_sp>acquire_max_private_depth)acquire_max_private_depth=s-slot->min_sp;
        slot->pending=0;acquire_pending--;
    }
}

/* Read-only live checks for lookup,single release andgroup release. */
static const uint32_t leaf_original[3]={109628u,110166u,110216u};
static const uint32_t leaf_original_end[3]={109672u,110216u,110298u};
static const uint32_t leaf_start[3]={1453490u,1453574u,1453712u};
static const uint32_t leaf_entry[3]={1453492u,1453576u,1453712u};
static const uint32_t leaf_end[3]={1453574u,1453712u,1453992u};
static const uint32_t leaf_return[3]={1453538u,1453628u,1453758u};
static struct cpu leaf_incoming[3],leaf_expected[3];
static unsigned char leaf_cache[3][144];
static unsigned leaf_pending[3],leaf_pending_any;
static uint32_t leaf_task[3],leaf_min_sp[3];
static uint64_t leaf_counts[3][8],leaf_min_headroom[3]={0xffffffffu,0xffffffffu,0xffffffffu},leaf_max_depth[3];
static uint64_t lookup_matches,lookup_misses,single_decrements,multi_nonnegative,multi_decrements,heap_floor_errors;
static uint16_t leaf_rd16(const unsigned char *p,unsigned i){return (uint16_t)(((uint16_t)p[i]<<8)|p[i+1]);}
static void leaf_wr16(unsigned char *p,unsigned i,uint16_t v){p[i]=(unsigned char)(v>>8);p[i+1]=(unsigned char)v;}
static uint16_t leaf_nz32(uint32_t v){return (uint16_t)(v==0?4:(v&0x80000000u)?8:0);}
static void prepare_leaf(unsigned k){
    struct cpu *in=&leaf_incoming[k],*ex=&leaf_expected[k];*ex=*in;memcpy(leaf_cache[k],ram+0x15b4a0u,144);
    uint32_t s=in->r[15];uint16_t wanted=(uint16_t)rd16(s+4u);unsigned index;
    if(k<2){
        for(index=0;index<36;index++)if(leaf_rd16(leaf_cache[k],index*4)==wanted)break;
        ex->r[1]=(in->r[1]&0xffff0000u)|index;ex->r[8]=0x15b4a0u;
        ex->r[0]=k==0?(index<36?index:0):(index<36?index:35)*4u;
        ex->sr=(uint16_t)((in->sr&0xffe0u)|leaf_nz32(in->r[2]));
        if(k==0){if(index<36)lookup_matches++;else lookup_misses++;}
        else if(index<36){uint16_t refs=leaf_rd16(leaf_cache[k],index*4+2);if(refs){leaf_wr16(leaf_cache[k],index*4+2,(uint16_t)(refs-1u));single_decrements++;}}
    }else{
        uint16_t x=(uint16_t)(in->sr&16u);
        if(!(wanted&0x8000u)){
            multi_nonnegative++;uint16_t mode=(uint16_t)rd16(0x15b530u);uint32_t doubled=(uint32_t)(int32_t)(int16_t)mode*2u;
            uint16_t remaining=(uint16_t)rd16(0x464a0u+doubled);x=(mode&0x8000u)?16u:0u;ex->r[0]=doubled;ex->r[1]&=0xffff0000u;ex->r[8]=0x15b4a0u;index=0;
            while((int16_t)remaining>0&&index<36){
                ex->r[0]=index*4u;
                if(leaf_rd16(leaf_cache[k],index*4)==wanted){uint16_t refs=leaf_rd16(leaf_cache[k],index*4+2);if((int16_t)refs>0){leaf_wr16(leaf_cache[k],index*4+2,(uint16_t)(refs-1u));multi_decrements++;}remaining=(uint16_t)(remaining-1u);wanted=(uint16_t)(wanted+1u);}
                index++;ex->r[1]=(ex->r[1]&0xffff0000u)|index;x=0;
            }
        }
        ex->sr=(uint16_t)((in->sr&0xffe0u)|x|leaf_nz32(in->r[3]));
    }
}
static void watch_leaf(uint32_t pc){
    if(pc==1438224u){heap_inits++;heap_base=rd32(0x112d60u);if(heap_base!=1705984u)heap_floor_errors++;}
    if(!leaf_pending_any&&!(pc>=0x1ac3cu&&pc<0x1ac68u)&&!(pc>=0x1ae56u&&pc<0x1aedau)&&!(pc>=1453490u&&pc<1453992u))return;
    for(unsigned k=0;k<3;k++){
        if(pc==leaf_original[k]){
            if(leaf_pending[k])leaf_counts[k][5]++;
            leaf_pending[k]=1;leaf_pending_any++;leaf_counts[k][0]++;read_cpu(&leaf_incoming[k]);leaf_min_sp[k]=leaf_incoming[k].r[15];leaf_task[k]=rd32(0xc0920u);prepare_leaf(k);emit(pc);
        }
        if(pc==leaf_entry[k])leaf_counts[k][1]++;
        if(pc>leaf_original[k]&&pc<leaf_original_end[k])leaf_counts[k][3]++;
        if(pc>=leaf_start[k]&&pc<leaf_end[k])leaf_counts[k][4]++;
        if(leaf_pending[k]){
            struct cpu current;read_cpu(&current);
            if(!(current.sr&0x2000u)){
                uint32_t task=rd32(0xc0920u),sp=current.r[15];leaf_counts[k][6]++;
                if(task!=leaf_task[k]||!task_stack_valid(task,sp))leaf_counts[k][7]++;
                else if(task_original_stack_valid(task,sp)&&sp-task-38u<leaf_min_headroom[k])leaf_min_headroom[k]=sp-task-38u;
                if(sp<leaf_min_sp[k])leaf_min_sp[k]=sp;
            }
            if(pc==leaf_return[k]||pc==leaf_original_end[k]-2u){
                struct cpu *in=&leaf_incoming[k],*ex=&leaf_expected[k];leaf_counts[k][2]++;emit(pc);
                for(unsigned i=0;i<16;i++)if(current.r[i]!=ex->r[i])leaf_counts[k][5]++;
                if(current.sr!=ex->sr||current.usp!=in->usp||current.ssp!=in->ssp||memcmp(leaf_cache[k],ram+0x15b4a0u,144))leaf_counts[k][5]++;
                uint32_t s=in->r[15];if(k<2){if(rd32(s-4u)!=in->r[2])leaf_counts[k][5]++;}else if(rd32(s-4u)!=in->r[3]||rd32(s-8u)!=in->r[2])leaf_counts[k][5]++;
                if(s-leaf_min_sp[k]>leaf_max_depth[k])leaf_max_depth[k]=s-leaf_min_sp[k];leaf_pending[k]=0;leaf_pending_any--;
            }
        }
    }
}


static struct cpu table_incoming;
static uint32_t table_handles[50];
static unsigned table_pending;
static uint64_t table_entries,table_native_entries,table_returns,table_old_steps,table_errors,table_native_steps;
static void watch_table(uint32_t pc){
    if(pc==0x1aeda){if(table_pending)table_errors++;table_pending=1;table_entries++;read_cpu(&table_incoming);for(unsigned i=0;i<50;i++)table_handles[i]=rd32(0x15b536u+12*i);emit(pc);}
    if(pc>0x1aeda&&pc<0x1af04)table_old_steps++;
    if(pc==0x162d64u)table_native_entries++;
    if(pc>=0x162d64u&&pc<0x162db2u)table_native_steps++;
    if(pc==0x162d84u){
        struct cpu current;read_cpu(&current);table_returns++;emit(pc);
        if(!table_pending||current.r[0]!=588||current.r[1]!=((table_incoming.r[1]&0xffff0000u)|50u)||current.r[8]!=0x15b534u||current.sr!=(table_incoming.sr&0xffe0u)||current.usp!=table_incoming.usp||current.ssp!=table_incoming.ssp)table_errors++;
        for(unsigned i=2;i<16;i++)if(i!=8&&current.r[i]!=table_incoming.r[i])table_errors++;
        for(unsigned i=0;i<50;i++)if(rd16(0x15b534u+12*i)!=0xffffu||rd16(0x15b53au+12*i)||rd16(0x15b53cu+12*i)||rd16(0x15b53eu+12*i)||rd32(0x15b536u+12*i)!=table_handles[i])table_errors++;
        table_pending=0;
    }
}

/* Read-only full return contract for complete1028E, tracked per source task. */
struct geometry_call {uint32_t task,object,return_word,min_sp;unsigned pending;struct cpu incoming,expected;};
static struct geometry_call geometry_calls[256];
static unsigned geometry_slots,geometry_pending;
static uint64_t geometry_entries,geometry_native_entries,geometry_returns,geometry_old_steps,geometry_native_steps,geometry_errors;
static uint64_t geometry_early,geometry_inside,geometry_last_outside,geometry_user_observations,geometry_stack_outside;
static uint32_t geometry_min_headroom=0xffffffffu,geometry_max_depth;
static struct geometry_call *geometry_slot(uint32_t task){
    for(unsigned i=0;i<geometry_slots;i++)if(geometry_calls[i].task==task)return &geometry_calls[i];
    if(geometry_slots>=256){geometry_errors++;return NULL;}
    struct geometry_call *call=&geometry_calls[geometry_slots++];call->task=task;return call;
}
static uint32_t geometry_read(uint32_t at){return rd32(at&0xffffffu);}
static void watch_geometry(uint32_t pc){
    if(!geometry_pending&&!(pc>=0x1028eu&&pc<0x102c4u)&&!(pc>=1453992u&&pc<1454204u))return;
    uint32_t task=rd32(0xc0920u);struct geometry_call *call=NULL;
    if(pc==0x1028eu){
        call=geometry_slot(task);if(!call)return;
        if(call->pending)geometry_errors++;
        read_cpu(&call->incoming);call->expected=call->incoming;call->min_sp=call->incoming.r[15];
        uint32_t sp=call->incoming.r[15],object=rd32(sp+4u),position,bound;unsigned early=0,last_outside=0;
        call->object=object;call->return_word=rd32(sp);
        position=geometry_read(object+4u);bound=geometry_read(object+30u);
        if((int32_t)position<(int32_t)bound)early=1;
        if(!early){position=geometry_read(object+4u);bound=geometry_read(object+26u);if((int32_t)position>=(int32_t)bound)early=1;}
        if(!early){position=geometry_read(object+10u);bound=geometry_read(object+38u);if((int32_t)position<(int32_t)bound)early=1;}
        if(!early){position=geometry_read(object+10u);bound=geometry_read(object+34u);last_outside=(int32_t)position>=(int32_t)bound;}
        call->expected.r[0]=early?1u:(call->incoming.r[0]&0xffff0000u)|last_outside;
        call->expected.r[1]=position;call->expected.r[8]=object;
        call->expected.sr=(uint16_t)((call->incoming.sr&0xffe0u)|(early?(call->incoming.sr&16u):last_outside?17u:4u));
        if(early)geometry_early++;else if(last_outside)geometry_last_outside++;else geometry_inside++;
        call->pending=1;geometry_pending++;geometry_entries++;emit(pc);
    }
    if(pc>0x1028eu&&pc<0x102c4u)geometry_old_steps++;
    if(pc==1453992u)geometry_native_entries++;
    if(pc>=1453992u&&pc<1454204u)geometry_native_steps++;
    if(!call){for(unsigned i=0;i<geometry_slots;i++)if(geometry_calls[i].task==task&&geometry_calls[i].pending){call=&geometry_calls[i];break;}}
    if(!call||!call->pending)return;
    struct cpu current;read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];geometry_user_observations++;
        if(!task_stack_valid(task,sp))geometry_stack_outside++;
        else if(task_original_stack_valid(task,sp)&&sp-task-38u<geometry_min_headroom)geometry_min_headroom=sp-task-38u;
        if(sp<call->min_sp)call->min_sp=sp;
    }
    if(pc==1454106u||pc==0x1029eu||pc==0x102c2u){
        geometry_returns++;emit(pc);
        for(unsigned i=0;i<16;i++)if(current.r[i]!=call->expected.r[i])geometry_errors++;
        if(current.sr!=call->expected.sr||current.usp!=call->incoming.usp||current.ssp!=call->incoming.ssp)geometry_errors++;
        uint32_t sp=call->incoming.r[15];if(rd32(sp)!=call->return_word||rd32(sp+4u)!=call->object)geometry_errors++;
        if(sp-call->min_sp>geometry_max_depth)geometry_max_depth=sp-call->min_sp;
        call->pending=0;geometry_pending--;
    }
}

/* Read-only entry/return prediction for complete1039C, stable RAM during call.
 * Unlike the component changing-read fixtures, this monitor takes entry samples.
 * Any live disagreement is an error to investigate, never silently accepted.
 */
struct select_call {uint32_t task,object,requested,ret,min_sp;unsigned pending,success;uint32_t record,lower_x,lower_z,upper_x,upper_z,header,sector,count;struct cpu incoming,expected;};
static struct select_call select_calls[256];
struct select_debug {struct select_call call;struct cpu actual;uint32_t frame,return_pc,error_delta;};
static struct select_debug select_debug_rows[256];static unsigned select_debug_count;
static unsigned select_slots,select_pending;
static uint64_t select_entries,select_native_entries,select_returns,select_old_steps,select_native_steps,select_errors,select_successes,select_failures,select_stack_outside,select_user_observations;
static uint32_t select_min_headroom=0xffffffffu,select_max_depth;
static struct select_call *select_slot(uint32_t task){
    for(unsigned i=0;i<select_slots;i++)if(select_calls[i].task==task)return &select_calls[i];
    if(select_slots>=256){select_errors++;return NULL;}
    struct select_call *s=&select_calls[select_slots++];s->task=task;return s;
}
static uint32_t select_read16(uint32_t address){return rd16(address&0x00ffffffu);}
static uint32_t select_read32(uint32_t address){return rd32(address&0x00ffffffu);}
static uint32_t select_offset(uint16_t value){uint16_t shifted=(uint16_t)((uint32_t)value<<6);return (uint32_t)(int32_t)(int16_t)shifted;}
static void watch_select(uint32_t pc){
    if(!select_pending&&!(pc>=0x1039cu&&pc<0x10430u)&&!(pc>=1454204u&&pc<1454502u))return;
    uint32_t task=select_read32(0xc0920u);struct select_call *s=NULL;
    if(pc==0x1039cu){
        s=select_slot(task);if(!s)return;if(s->pending)select_errors++;
        read_cpu(&s->incoming);s->expected=s->incoming;uint32_t sp=s->incoming.r[15];s->min_sp=sp;s->ret=select_read32(sp);s->object=select_read32(sp+4);s->requested=select_read16(sp+8);
        uint32_t object=s->object;uint16_t sector=select_read16(object+64u);uint32_t shifted=(uint32_t)(int32_t)(int16_t)sector*4u;uint32_t header=select_read32(0x49bb4u+shifted);uint16_t count=select_read16(header);
        s->header=header;s->sector=sector;s->count=count;s->success=(int16_t)s->requested<(int16_t)count;
        s->expected.r[0]=shifted&0xffff0000u;s->expected.r[1]=(s->incoming.r[1]&0xffff0000u)|s->requested;s->expected.r[8]=header;s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|4u|((sector&0x8000u)?16u:0u));
        if(s->success){
            s->record=select_read32(header+8u)+(uint32_t)((int32_t)(int16_t)s->requested*20);
            uint32_t record=s->record;s->lower_x=(select_read32(object+4u)&0xfffffc00u)+select_offset(select_read16(record+10u));s->lower_z=(select_read32(object+10u)&0xfffffc00u)+select_offset(select_read16(record+14u));s->upper_x=s->lower_x+select_offset(select_read16(record+16u));uint16_t last_width=select_read16(record+18u);s->upper_z=s->lower_z+select_offset(last_width);
            s->expected.r[0]=1;s->expected.r[1]=select_read32(object+10u)&0xfffffc00u;s->expected.r[8]=s->upper_z;s->expected.r[9]=record;s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|((last_width&0x400u)?16u:0u));select_successes++;
        }else select_failures++;
        s->pending=1;select_pending++;select_entries++;emit(pc);
    }
    if(pc>0x1039cu&&pc<0x10430u)select_old_steps++;
    if(pc==1454204u)select_native_entries++;
    if(pc>=1454204u&&pc<1454502u)select_native_steps++;
    if(!s)for(unsigned i=0;i<select_slots;i++)if(select_calls[i].task==task&&select_calls[i].pending){s=&select_calls[i];break;}
    if(!s||!s->pending)return;struct cpu current;read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];select_user_observations++;
        if(!task_stack_valid(task,sp))select_stack_outside++;
        else if(task_original_stack_valid(task,sp)&&sp-task-38u<select_min_headroom)select_min_headroom=sp-task-38u;
        if(sp<s->min_sp)s->min_sp=sp;
    }
    if(pc==1454292u||pc==0x1042eu){
        uint64_t errors_before=select_errors;select_returns++;emit(pc);for(unsigned i=0;i<16;i++)if(current.r[i]!=s->expected.r[i])select_errors++;
        if(current.sr!=s->expected.sr||current.usp!=s->incoming.usp||current.ssp!=s->incoming.ssp)select_errors++;
        uint32_t sp=s->incoming.r[15],obj=s->object;if(select_read32(sp)!=s->ret||select_read32(sp+4)!=obj||select_read16(sp+8)!=s->requested)select_errors++;
        if(s->success&&(select_read16(obj+66)!=s->requested||select_read32(obj+68)!=s->record||select_read32(obj+76)!=s->lower_x||select_read32(obj+84)!=s->lower_z||select_read32(obj+72)!=s->upper_x||select_read32(obj+80)!=s->upper_z))select_errors++;
        if(select_debug_count<256){struct select_debug *d=&select_debug_rows[select_debug_count++];d->call=*s;d->actual=current;d->frame=frame;d->return_pc=pc;d->error_delta=(uint32_t)(select_errors-errors_before);}else select_errors++;
        if(sp-s->min_sp>select_max_depth)select_max_depth=sp-s->min_sp;s->pending=0;select_pending--;
    }
}

static void select_debug_cpu(FILE *file,const struct cpu *cpu){
    fprintf(file,"{\"registers\":[");for(unsigned j=0;j<16;j++)fprintf(file,"%s%u",j?",":"",cpu->r[j]);
    fprintf(file,"],\"pc\":%u,\"usp\":%u,\"ssp\":%u,\"sr\":%u}",cpu->pc,cpu->usp,cpu->ssp,(unsigned)cpu->sr);
}
static void select_debug_dump(FILE *file){
    fprintf(file,",\"select_diagnostics\":[");
    for(unsigned i=0;i<select_debug_count;i++){
        const struct select_debug *d=&select_debug_rows[i];const struct select_call *s=&d->call;
        fprintf(file,"%s{\"frame\":%u,\"return_pc\":%u,\"errors_at_return\":%u,\"object\":%u,\"requested\":%u,\"sector\":%u,\"header\":%u,\"count\":%u,\"success\":%u,\"record\":%u,\"lower_x\":%u,\"lower_z\":%u,\"upper_x\":%u,\"upper_z\":%u,\"incoming\":",i?",":"",d->frame,d->return_pc,d->error_delta,s->object,s->requested,s->sector,s->header,s->count,s->success,s->record,s->lower_x,s->lower_z,s->upper_x,s->upper_z);
        select_debug_cpu(file,&s->incoming);fprintf(file,",\"expected\":");select_debug_cpu(file,&s->expected);fprintf(file,",\"actual\":");select_debug_cpu(file,&d->actual);fputc('}',file);
    }fputc(']',file);
}

/* Coordinator read-only stable-entry oracle for original102C4 complete search.
 * Every address uses the Jaguar24-bit bus; pointer register values stay32-bit.
 * Dynamic reads are checked separately by component replay, never assumed here.
 */
struct scan_call {
    uint32_t task,object,ret,min_sp,header,sector,count,index,record;
    uint32_t fields[6];
    unsigned pending,success,skipped,iterations;
    struct cpu incoming,expected;
};
struct scan_debug {struct scan_call call;struct cpu actual;uint32_t frame,return_pc,error_delta;};
static struct scan_call scan_calls[256];
static struct scan_debug scan_debug_rows[512];
static unsigned scan_slots,scan_pending,scan_debug_count;
static uint64_t scan_entries,scan_native_entries,scan_returns,scan_old_steps,scan_native_steps,scan_errors,scan_successes,scan_failures,scan_skips,scan_stack_outside,scan_user_observations,scan_iterations;
static uint32_t scan_min_headroom=0xffffffffu,scan_max_depth;
static const unsigned scan_field_offsets[6]={66,68,76,84,72,80};
static uint32_t scan_read16(uint32_t address){return rd16(address&0x00ffffffu);}
static uint32_t scan_read32(uint32_t address){return rd32(address&0x00ffffffu);}
static uint32_t scan_offset(uint16_t value){return (uint32_t)(int32_t)(int16_t)(uint16_t)((uint32_t)value<<6);}
static struct scan_call *scan_slot(uint32_t task){
    for(unsigned i=0;i<scan_slots;i++)if(scan_calls[i].task==task)return &scan_calls[i];
    if(scan_slots>=256){scan_errors++;return NULL;}
    struct scan_call *s=&scan_calls[scan_slots++];s->task=task;return s;
}
static void scan_predict(struct scan_call *s){
    uint32_t object=s->object;
    for(unsigned i=0;i<6;i++)s->fields[i]=i?scan_read32(object+scan_field_offsets[i]):scan_read16(object+66u);
    s->sector=scan_read16(object+64u);
    s->header=scan_read32(0x49bb4u+(uint32_t)(int32_t)(int16_t)s->sector*4u);
    uint32_t x=(scan_read32(object+4u)>>6)&15u,position_z=scan_read32(object+10u);
    uint32_t shifted_z=(position_z>>6)|((position_z&0x80000000u)?0xfc000000u:0u),z=shifted_z&15u;
    s->count=scan_read16(s->header);uint16_t index=(uint16_t)(s->count-1u);unsigned carry=s->count==0;
    s->success=0;s->skipped=(index&0x8000u)!=0;s->iterations=0;s->record=0;s->index=index;
    s->expected.r[0]=shifted_z&0xffff0000u;s->expected.r[1]=(s->incoming.r[1]&0xffff0000u)|index;s->expected.r[8]=s->header;
    if(!s->skipped){
        for(;;){
            s->iterations++;s->record=scan_read32(s->header+8u)+(uint32_t)((int32_t)(int16_t)index*20);
            s->expected.r[9]=s->record;
            uint16_t lower=scan_read16(s->record+10u);
            if((int16_t)x>=(int16_t)lower){
                uint32_t sum=scan_read16(s->record+10u)+scan_read16(s->record+16u);carry=sum>0xffffu;
                if((int16_t)x<(int16_t)(uint16_t)sum){
                    lower=scan_read16(s->record+14u);
                    if((int16_t)z>=(int16_t)lower){
                        sum=scan_read16(s->record+14u)+scan_read16(s->record+18u);carry=sum>0xffffu;
                        if((int16_t)z<(int16_t)(uint16_t)sum){s->success=1;break;}
                    }
                }
            }
            index=(uint16_t)(index-1u);if(index==0xffffu)break;
        }
        s->index=index;s->expected.r[0]=0;s->expected.r[1]=(s->incoming.r[1]&0xffff0000u)|index;
    }
    s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|4u|(carry?16u:0u));
    if(s->success){
        s->fields[0]=index;s->fields[1]=s->record;
        s->fields[2]=(scan_read32(object+4u)&0xfffffc00u)+scan_offset(scan_read16(s->record+10u));
        s->fields[3]=(scan_read32(object+10u)&0xfffffc00u)+scan_offset(scan_read16(s->record+14u));
        s->fields[4]=s->fields[2]+scan_offset(scan_read16(s->record+16u));
        uint16_t depth=scan_read16(s->record+18u);s->fields[5]=s->fields[3]+scan_offset(depth);
        s->expected.r[0]=1;s->expected.r[1]=scan_read32(object+10u)&0xfffffc00u;s->expected.r[8]=s->fields[5];
        s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|((depth&0x400u)?16u:0u));
    }
}
static void watch_scan(uint32_t pc){
    if(!scan_pending&&!(pc>=0x102c4u&&pc<0x1039cu)&&!(pc>=1454504u&&pc<1454932u))return;
    uint32_t task=scan_read32(0xc0920u);struct scan_call *s=NULL;
    if(pc==0x102c4u){
        s=scan_slot(task);if(!s)return;if(s->pending)scan_errors++;
        read_cpu(&s->incoming);s->expected=s->incoming;s->min_sp=s->incoming.r[15];s->ret=scan_read32(s->incoming.r[15]);s->object=scan_read32(s->incoming.r[15]+4u);
        scan_predict(s);s->pending=1;scan_pending++;scan_entries++;scan_iterations+=s->iterations;
        if(s->success)scan_successes++;else scan_failures++;if(s->skipped)scan_skips++;emit(pc);
    }
    if(pc>0x102c4u&&pc<0x1039cu)scan_old_steps++;
    if(pc==1454504u)scan_native_entries++;
    if(pc>=1454504u&&pc<1454932u)scan_native_steps++;
    if(!s)for(unsigned i=0;i<scan_slots;i++)if(scan_calls[i].task==task&&scan_calls[i].pending){s=&scan_calls[i];break;}
    if(!s||!s->pending)return;struct cpu current;read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];scan_user_observations++;
        if(!task_stack_valid(task,sp))scan_stack_outside++;
        else if(task_original_stack_valid(task,sp)&&sp-task-38u<scan_min_headroom)scan_min_headroom=sp-task-38u;
        if(sp<s->min_sp)s->min_sp=sp;
    }
    if(pc==1454568u||pc==0x1039au){
        uint64_t before=scan_errors;scan_returns++;emit(pc);
        for(unsigned i=0;i<16;i++)if(current.r[i]!=s->expected.r[i])scan_errors++;
        if(current.sr!=s->expected.sr||current.usp!=s->incoming.usp||current.ssp!=s->incoming.ssp)scan_errors++;
        uint32_t sp=s->incoming.r[15];if(scan_read32(sp)!=s->ret||scan_read32(sp+4u)!=s->object)scan_errors++;
        for(unsigned i=0;i<6;i++)if((i?scan_read32(s->object+scan_field_offsets[i]):scan_read16(s->object+66u))!=s->fields[i])scan_errors++;
        if(scan_debug_count<512){struct scan_debug *d=&scan_debug_rows[scan_debug_count++];d->call=*s;d->actual=current;d->frame=frame;d->return_pc=pc;d->error_delta=(uint32_t)(scan_errors-before);}
        if(sp-s->min_sp>scan_max_depth)scan_max_depth=sp-s->min_sp;s->pending=0;scan_pending--;
    }
}
static void scan_debug_dump(FILE *file){
    fprintf(file,",\"scan_diagnostics\":[");
    for(unsigned i=0;i<scan_debug_count;i++){
        const struct scan_debug *d=&scan_debug_rows[i];const struct scan_call *s=&d->call;
        fprintf(file,"%s{\"frame\":%u,\"return_pc\":%u,\"errors_at_return\":%u,\"object\":%u,\"sector\":%u,\"header\":%u,\"count\":%u,\"index\":%u,\"success\":%u,\"skipped\":%u,\"iterations\":%u,\"record\":%u,\"incoming\":",i?",":"",d->frame,d->return_pc,d->error_delta,s->object,s->sector,s->header,s->count,s->index,s->success,s->skipped,s->iterations,s->record);
        select_debug_cpu(file,&s->incoming);fprintf(file,",\"expected\":");select_debug_cpu(file,&s->expected);fprintf(file,",\"actual\":");select_debug_cpu(file,&d->actual);fputc('}',file);
    }fputc(']',file);
}

/* Stable-entry full10430 oracle, with shadow writes for actor/record overlap.
 * Read-only to guest RAM; all addresses resolve through24bit bus masking.
 */
struct door_store {uint32_t address,value;unsigned width;};
struct door_call {
    uint32_t task,object,ret,index,direction,min_sp,sector,header,record;
    unsigned pending,path,stores;
    struct door_store overlay[6];
    uint32_t fields[6];
    struct cpu incoming,expected;
};
struct door_debug {struct door_call call;struct cpu actual;uint32_t frame,return_pc,error_delta;};
static struct door_call door_calls[256];static unsigned door_slots,door_pending,door_debug_count;
static struct door_debug door_debug_rows[512];
static uint64_t door_entries,door_native_entries,door_returns,door_old_steps,door_native_steps,door_errors,door_count_rejects,door_sentinels,door_key_mismatches,door_successes,door_user_observations,door_stack_outside;
static uint32_t door_min_headroom=0xffffffffu,door_max_depth;
static const unsigned door_offsets[6]={22,24,30,38,26,34};
static uint32_t door_read(uint32_t address,unsigned width){address&=0xffffffu;if(width==2)return rd16(address);if(width==4)return rd32(address);if(address>0x1fffffu){errors++;return 0;}return ram[address];}
static uint32_t door_overlay_read(struct door_call *s,uint32_t address,unsigned width){
    uint32_t value=0;
    for(unsigned i=0;i<width;i++){
        uint32_t at=(address+i)&0xffffffu,byte=door_read(at,1);
        for(unsigned n=s->stores;n>0;n--){const struct door_store *w=&s->overlay[n-1];uint32_t delta=(at-w->address)&0xffffffu;if(delta<w->width){byte=(w->value>>(8u*(w->width-1u-delta)))&255u;break;}}
        value=(value<<8)|byte;
    }return value;
}
static void door_overlay_write(struct door_call *s,uint32_t address,unsigned width,uint32_t value){
    if(s->stores>=6){door_errors++;return;}struct door_store *w=&s->overlay[s->stores++];w->address=address&0xffffffu;w->width=width;w->value=value;
}
static uint32_t door_scaled(uint16_t value){return (uint32_t)(int32_t)(int16_t)value<<6;}
static struct door_call *door_slot(uint32_t task){
    for(unsigned i=0;i<door_slots;i++)if(door_calls[i].task==task)return &door_calls[i];
    if(door_slots>=256){door_errors++;return NULL;}struct door_call *s=&door_calls[door_slots++];s->task=task;return s;
}
static void door_predict(struct door_call *s){
    uint32_t object=s->object;s->path=0;s->stores=0;s->record=0;
    for(unsigned i=0;i<6;i++)s->fields[i]=door_read(object+door_offsets[i],i<2?2:4);
    uint16_t sector=door_read(object+64u,2);s->sector=sector;
    uint32_t offset=(uint32_t)(int32_t)(int16_t)sector*4u;
    s->header=door_read(0x49bb4u+offset,4);uint16_t count=door_read(s->header+2u,2);
    s->expected.r[0]=offset&0xffff0000u;s->expected.r[8]=s->header;s->expected.r[9]=object;
    s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|4u|((sector&0x8000u)?16u:0u));
    if((int16_t)s->index>=(int16_t)count)return;
    uint32_t product=(uint32_t)((int32_t)(int16_t)s->index*28),base=door_read(s->header+12u,4),record=base+product;s->record=record;
    s->expected.r[0]=record&0xffff0000u;s->expected.r[8]=record;s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|4u|((record<product)?16u:0u));
    s->path=1;if(door_read(record+26u,2)==0xffffu)return;
    uint16_t key=(uint16_t)s->incoming.r[1],compare=(uint16_t)s->incoming.r[3];
    if(s->direction<4u){
        const unsigned lhs[4]={6,74,82,12},rhs[4]={78,6,12,86};uint16_t left=door_read(object+lhs[s->direction],2),right=door_read(object+rhs[s->direction],2);
        key=(uint16_t)(left-right);compare=(uint16_t)(int16_t)(int8_t)door_read(record+11u+2u*s->direction,1);
    }
    uint16_t nibble=(key>>6)&15u;s->expected.r[1]=(s->incoming.r[1]&0xffff0000u)|nibble;s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|4u|((key&32u)?16u:0u));s->path=2;
    if(compare!=nibble)return;
    s->path=3;door_overlay_write(s,object+22u,2,0);
    door_overlay_write(s,object+24u,2,door_overlay_read(s,record+26u,2));
    door_overlay_write(s,object+30u,4,door_scaled(door_overlay_read(s,record+18u,2)));
    door_overlay_write(s,object+38u,4,door_scaled(door_overlay_read(s,record+20u,2)));
    uint32_t width=door_scaled(door_overlay_read(s,record+22u,2)),base_x=door_overlay_read(s,object+30u,4);door_overlay_write(s,object+26u,4,width+base_x);
    uint32_t depth=door_scaled(door_overlay_read(s,record+24u,2)),base_z=door_overlay_read(s,object+38u,4),upper_z=depth+base_z;door_overlay_write(s,object+34u,4,upper_z);
    for(unsigned i=0;i<6;i++)s->fields[i]=door_overlay_read(s,object+door_offsets[i],i<2?2:4);
    s->expected.r[0]=1;s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|((upper_z<depth)?16u:0u));
}
static void watch_door(uint32_t pc){
    if(!door_pending&&!(pc>=0x10430u&&pc<0x10520u)&&!(pc>=1454932u&&pc<1455390u))return;
    uint32_t task=door_read(0xc0920u,4);struct door_call *s=NULL;
    if(pc==0x10430u){
        s=door_slot(task);if(!s)return;if(s->pending)door_errors++;read_cpu(&s->incoming);s->expected=s->incoming;s->min_sp=s->incoming.r[15];s->ret=door_read(s->min_sp,4);s->object=door_read(s->min_sp+4u,4);s->index=door_read(s->min_sp+8u,2);s->direction=door_read(s->min_sp+10u,2);
        door_predict(s);s->pending=1;door_pending++;door_entries++;if(s->path==0)door_count_rejects++;else if(s->path==1)door_sentinels++;else if(s->path==2)door_key_mismatches++;else door_successes++;emit(pc);
    }
    if(pc>0x10430u&&pc<0x10520u)door_old_steps++;
    if(pc==1454932u)door_native_entries++;
    if(pc>=1454932u&&pc<1455390u)door_native_steps++;
    if(!s)for(unsigned i=0;i<door_slots;i++)if(door_calls[i].task==task&&door_calls[i].pending){s=&door_calls[i];break;}
    if(!s||!s->pending)return;struct cpu current;read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];door_user_observations++;
        if(!task_stack_valid(task,sp))door_stack_outside++;
        else if(task_original_stack_valid(task,sp)&&sp-task-38u<door_min_headroom)door_min_headroom=sp-task-38u;
        if(sp<s->min_sp)s->min_sp=sp;
    }
    if(pc==1455020u||pc==0x1051eu){
        uint64_t before=door_errors;door_returns++;emit(pc);
        for(unsigned i=0;i<16;i++)if(current.r[i]!=s->expected.r[i])door_errors++;
        if(current.sr!=s->expected.sr||current.usp!=s->incoming.usp||current.ssp!=s->incoming.ssp)door_errors++;
        uint32_t sp=s->incoming.r[15];if(door_read(sp,4)!=s->ret||door_read(sp+4u,4)!=s->object||door_read(sp+8u,2)!=s->index||door_read(sp+10u,2)!=s->direction)door_errors++;
        for(unsigned i=0;i<6;i++)if(door_read(s->object+door_offsets[i],i<2?2:4)!=s->fields[i])door_errors++;
        if(door_debug_count<512){struct door_debug *d=&door_debug_rows[door_debug_count++];d->call=*s;d->actual=current;d->frame=frame;d->return_pc=pc;d->error_delta=(uint32_t)(door_errors-before);}
        if(sp-s->min_sp>door_max_depth)door_max_depth=sp-s->min_sp;s->pending=0;door_pending--;
    }
}
static void door_debug_dump(FILE *file){
    fprintf(file,",\"door_diagnostics\":[");
    for(unsigned i=0;i<door_debug_count;i++){
        const struct door_debug *d=&door_debug_rows[i];const struct door_call *s=&d->call;
        fprintf(file,"%s{\"frame\":%u,\"return_pc\":%u,\"errors_at_return\":%u,\"object\":%u,\"index\":%u,\"direction\":%u,\"path\":%u,\"sector\":%u,\"header\":%u,\"record\":%u,\"incoming\":",i?",":"",d->frame,d->return_pc,d->error_delta,s->object,s->index,s->direction,s->path,s->sector,s->header,s->record);
        select_debug_cpu(file,&s->incoming);fprintf(file,",\"expected\":");select_debug_cpu(file,&s->expected);fprintf(file,",\"actual\":");select_debug_cpu(file,&d->actual);fputc('}',file);
    }fputc(']',file);
}

/* Stable-entry oracle for original10520/105DA. Shadow writes preserve aliases.
 * Guest RAM is read-only. Changing/device/concurrent reads remain separate limits. */
struct interior_store {uint32_t address,value;unsigned width;};
struct interior_call {
    uint32_t task,object,ret,kind,min_sp,header,record,iterations;
    unsigned pending,path,stores;
    struct interior_store overlay[6];
    uint32_t fields[6];
    struct cpu incoming,expected;
};
struct interior_debug {struct interior_call call;struct cpu actual;uint32_t frame,return_pc,error_delta;};
static struct interior_call interior_calls[256];
static struct interior_debug interior_debug_rows[512];
static unsigned interior_slots,interior_pending,interior_debug_count;
static uint64_t interior_entries,interior_native_entries,interior_returns,interior_old_steps,interior_native_steps;
static uint64_t interior_errors,interior_skips,interior_successes,interior_failures,interior_iterations,interior_user_observations,interior_stack_outside;
static uint64_t interior_kind_entries[2],interior_kind_successes[2],interior_kind_failures[2];
static uint32_t interior_min_headroom=0xffffffffu,interior_max_depth;
static const unsigned interior_offsets[6]={42,44,52,60,48,56};
static uint32_t interior_read(uint32_t a,unsigned width){
    a&=0xffffffu;
    if(a>0x200000u-width){interior_errors++;return 0;}
    if(width==4)return rd32(a);if(width==2)return rd16(a);return ram[a];
}
#ifndef BIWN_INTERIOR_TASK
#define BIWN_INTERIOR_TASK() interior_read(0xc0920u,4)
#endif
static uint32_t interior_overlay_read(struct interior_call *s,uint32_t a,unsigned width){
    uint32_t value=0;
    for(unsigned i=0;i<width;i++){
        uint32_t at=(a+i)&0xffffffu,byte=interior_read(at,1);
        for(unsigned n=s->stores;n>0;n--){
            const struct interior_store *w=&s->overlay[n-1];uint32_t delta=(at-w->address)&0xffffffu;
            if(delta<w->width){byte=(w->value>>(8u*(w->width-1u-delta)))&255u;break;}
        }value=(value<<8)|byte;
    }return value;
}
static void interior_overlay_write(struct interior_call *s,uint32_t a,unsigned width,uint32_t value){
    if(s->stores>=6){interior_errors++;return;}
    struct interior_store *w=&s->overlay[s->stores++];w->address=a&0xffffffu;w->width=width;w->value=value;
}
static uint32_t interior_word_scale(uint16_t value){return (uint32_t)(int32_t)(int16_t)(uint16_t)((uint32_t)value<<6);}
static struct interior_call *interior_slot(uint32_t task){
    for(unsigned i=0;i<interior_slots;i++)if(interior_calls[i].task==task)return &interior_calls[i];
    if(interior_slots>=256){interior_errors++;return NULL;}
    struct interior_call *s=&interior_calls[interior_slots++];s->task=task;return s;
}
static void interior_predict(struct interior_call *s){
    uint32_t object=s->object;s->stores=0;s->record=0;s->iterations=0;s->path=0;
    if(s->kind) s->fields[0]=interior_read(object+16u,2);
    else for(unsigned i=0;i<6;i++)s->fields[i]=interior_read(object+interior_offsets[i],i?4:2);
    uint32_t header=interior_read(0x49c18u,4);s->header=header;
    s->expected.r[s->kind?9:8]=header;
    uint32_t x=interior_read(object+(s->kind?2u:4u),4);
    uint32_t origin=interior_read(s->kind?0x49c6au:object+30u,4);x=(x-origin)>>6;
    uint32_t difference=interior_read(object+(s->kind?8u:10u),4);
    origin=interior_read(s->kind?0x49c72u:object+38u,4);difference-=origin;
    uint32_t z=difference>>6,d0=difference;
    uint16_t count=interior_read(header,2),index=(uint16_t)(count-1u);unsigned xbit=count==0;
    if(!(index&0x8000u)){
        s->path=1;
        for(;;){
            d0=(uint32_t)((int32_t)(int16_t)index*24);
            s->record=interior_read(header+4u,4)+d0;s->iterations++;
            s->expected.r[s->kind?8:9]=s->record;
            uint16_t lower=interior_read(s->record+2u,2);
            if((int16_t)(uint16_t)x>=(int16_t)lower){
                lower=interior_read(s->record+2u,2);uint16_t width=interior_read(s->record+6u,2);
                uint32_t sum=(uint32_t)lower+width;xbit=sum>65535u;d0=(d0&0xffff0000u)|(uint16_t)sum;
                if((int16_t)(uint16_t)x<(int16_t)(uint16_t)d0){
                    lower=interior_read(s->record+4u,2);
                    if((int16_t)(uint16_t)z>=(int16_t)lower){
                        lower=interior_read(s->record+4u,2);uint16_t depth=interior_read(s->record+8u,2);
                        sum=(uint32_t)lower+depth;xbit=sum>65535u;d0=(d0&0xffff0000u)|(uint16_t)sum;
                        if((int16_t)(uint16_t)z<(int16_t)(uint16_t)d0)break;
                    }
                }
            }
            index=(uint16_t)(index-1u);if(index==0xffffu)break;
        }
    }
    s->expected.r[1]=(s->incoming.r[1]&0xffff0000u)|index;
    s->expected.r[0]=d0&0xffff0000u;
    s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|4u|(xbit?16u:0u));
    if(index&0x8000u)return;
    s->path=2;s->expected.r[0]=1;s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|(xbit?16u:0u));
    if(s->kind){interior_overlay_write(s,object+16u,2,index);s->fields[0]=interior_overlay_read(s,object+16u,2);return;}
    interior_overlay_write(s,object+42u,2,index);interior_overlay_write(s,object+44u,4,s->record);
    uint16_t word=interior_overlay_read(s,s->record+2u,2);uint32_t scaled=interior_word_scale(word);
    origin=interior_overlay_read(s,object+30u,4);interior_overlay_write(s,object+52u,4,origin+scaled);
    word=interior_overlay_read(s,s->record+4u,2);scaled=interior_word_scale(word);
    origin=interior_overlay_read(s,object+38u,4);interior_overlay_write(s,object+60u,4,origin+scaled);
    word=interior_overlay_read(s,s->record+6u,2);scaled=interior_word_scale(word);
    origin=interior_overlay_read(s,object+52u,4);interior_overlay_write(s,object+48u,4,origin+scaled);
    word=interior_overlay_read(s,s->record+8u,2);scaled=interior_word_scale(word);
    origin=interior_overlay_read(s,object+60u,4);uint32_t upper=origin+scaled;interior_overlay_write(s,object+56u,4,upper);
    s->expected.r[8]=upper;s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|((word&0x400u)?16u:0u));
    for(unsigned i=0;i<6;i++)s->fields[i]=interior_overlay_read(s,object+interior_offsets[i],i?4:2);
}
static void watch_interior(uint32_t pc){
    if(!interior_pending&&!(pc>=0x10520u&&pc<0x10652u)&&!(pc>=1455392u&&pc<1456008u))return;
    uint32_t task=BIWN_INTERIOR_TASK();struct interior_call *s=NULL;
    if(pc==0x10520u||pc==0x105dau){
        s=interior_slot(task);if(!s)return;if(s->pending)interior_errors++;
        read_cpu(&s->incoming);s->expected=s->incoming;s->kind=pc==0x105dau;s->min_sp=s->incoming.r[15];
        s->ret=interior_read(s->min_sp,4);s->object=interior_read(s->min_sp+4u,4);
        interior_predict(s);s->pending=1;interior_pending++;interior_entries++;interior_kind_entries[s->kind]++;
        interior_iterations+=s->iterations;
        if(s->path==0)interior_skips++;
        if(s->path==2){interior_successes++;interior_kind_successes[s->kind]++;}
        else{interior_failures++;interior_kind_failures[s->kind]++;}emit(pc);
    }
    if((pc>0x10520u&&pc<0x105dau)||(pc>0x105dau&&pc<0x10652u))interior_old_steps++;
    if(pc==1455392u||pc==1455398u)interior_native_entries++;
    if(pc>=1455392u&&pc<1456008u)interior_native_steps++;
    if(!s)for(unsigned i=0;i<interior_slots;i++)if(interior_calls[i].task==task&&interior_calls[i].pending){s=&interior_calls[i];break;}
    if(!s||!s->pending)return;struct cpu current;read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];interior_user_observations++;
        if(!task_stack_valid(task,sp))interior_stack_outside++;
        else if(task_original_stack_valid(task,sp)&&sp-task-38u<interior_min_headroom)interior_min_headroom=sp-task-38u;
        if(sp<s->min_sp)s->min_sp=sp;
    }
    if(pc==1455438u||pc==(s->kind?0x10650u:0x105d8u)){
        uint64_t before=interior_errors;interior_returns++;emit(pc);
        for(unsigned i=0;i<16;i++)if(current.r[i]!=s->expected.r[i])interior_errors++;
        if(current.sr!=s->expected.sr||current.usp!=s->incoming.usp||current.ssp!=s->incoming.ssp)interior_errors++;
        uint32_t sp=s->incoming.r[15];if(interior_read(sp,4)!=s->ret||interior_read(sp+4u,4)!=s->object)interior_errors++;
        if(s->kind){if(interior_read(s->object+16u,2)!=s->fields[0])interior_errors++;}
        else for(unsigned i=0;i<6;i++)if(interior_read(s->object+interior_offsets[i],i?4:2)!=s->fields[i])interior_errors++;
        if(interior_debug_count<512){struct interior_debug *d=&interior_debug_rows[interior_debug_count++];d->call=*s;d->actual=current;d->frame=frame;d->return_pc=pc;d->error_delta=(uint32_t)(interior_errors-before);}
        if(sp-s->min_sp>interior_max_depth)interior_max_depth=sp-s->min_sp;s->pending=0;interior_pending--;
    }
}
static void interior_debug_dump(FILE *file){
    fprintf(file,",\"interior_diagnostics\":[");
    for(unsigned i=0;i<interior_debug_count;i++){
        const struct interior_debug *d=&interior_debug_rows[i];const struct interior_call *s=&d->call;
        fprintf(file,"%s{\"frame\":%u,\"return_pc\":%u,\"errors_at_return\":%u,\"kind\":%u,\"object\":%u,\"header\":%u,\"record\":%u,\"iterations\":%u,\"path\":%u,\"incoming\":",i?",":"",d->frame,d->return_pc,d->error_delta,s->kind,s->object,s->header,s->record,s->iterations,s->path);
        select_debug_cpu(file,&s->incoming);fprintf(file,",\"expected\":");select_debug_cpu(file,&s->expected);fprintf(file,",\"actual\":");select_debug_cpu(file,&d->actual);fputc('}',file);
    }fputc(']',file);
}

/* Read-only stable-entry dispatcher/real-child ABI oracle. The children run;
 * their captured actual outputs, not a second child algorithm, predict root
 * return. Does not predict concurrent changes to the entry pool/flags reads. */
#ifndef BIWN_ACTOR_DISPATCH_TASK
#define BIWN_ACTOR_DISPATCH_TASK() rd32(0xc0920u)
#endif
struct ad_call {uint32_t task,sp,ret,args[5],slot,min_sp;unsigned pending,actor,full,child,returned,native;uint32_t context[18];struct cpu incoming,expected,output;};
static struct ad_call ad_calls[256];
static unsigned ad_slots,ad_pending;
static uint64_t ad_entries,ad_native_entries,ad_returns,ad_old_steps,ad_native_steps,ad_errors,ad_child_entries,ad_child_returns,ad_actor,ad_sprite,ad_full,ad_stack_observations,ad_stack_outside;
static uint32_t ad_max_depth,ad_min_headroom=0xffffffffu,ad_max_child_depth,ad_min_context_clearance=0xffffffffu;
static uint64_t ad_context_collisions,ad_context_checks,ad_child_below_context,ad_context_SP_inside;
static uint32_t ad_sx(uint16_t x){return(uint32_t)(x&0x7fffu)-(uint32_t)(x&0x8000u);}
static void ad_compare(const struct cpu *a,const struct cpu *b){
    for(unsigned i=0;i<16;i++)if(a->r[i]!=b->r[i])ad_errors++;
    if(a->sr!=b->sr||a->usp!=b->usp||a->ssp!=b->ssp)ad_errors++;
}
static void ad_bank(struct cpu *c){if(c->sr&0x2000u)c->ssp=c->r[15];else c->usp=c->r[15];}
static void watch_actor_dispatch(uint32_t pc){
    if(pc==1456328u)ad_native_entries++;
    if(pc>0x13ae0u&&pc<0x13b5au)ad_old_steps++;
    if(pc>=1456008u&&pc<1456580u)ad_native_steps++;
    if(!ad_pending&&pc!=0x13ae0u)return;
    uint32_t task=BIWN_ACTOR_DISPATCH_TASK();struct ad_call *call=NULL;struct cpu current;
    for(unsigned i=0;i<ad_slots;i++)if(ad_calls[i].task==task){call=&ad_calls[i];break;}
    if(pc==0x13ae0u){
        if(!call){if(ad_slots==256){ad_errors++;return;}call=&ad_calls[ad_slots++];call->task=task;}
        if(call->pending)ad_errors++;
        read_cpu(&call->incoming);call->expected=call->incoming;call->sp=call->incoming.r[15];call->ret=rd32(call->sp);call->min_sp=call->sp;
        uint32_t s=call->sp;call->args[0]=rd16(s+4);call->args[1]=rd32(s+6);call->args[2]=rd16(s+10);call->args[3]=rd32(s+12);call->args[4]=rd16(s+16);
        call->pending=1;call->child=call->returned=call->full=call->native=0;ad_entries++;ad_pending++;
        uint32_t id=call->args[0],flags=(rd16((0x4208cu+ad_sx((uint16_t)id))&~1u)>>(((0x4208cu+ad_sx((uint16_t)id))&1u)?0:8))&255u;
        call->actor=flags&1u;call->slot=0;
        struct cpu *expected=&call->expected;
        expected->r[9]=ad_sx((uint16_t)id);expected->r[5]=call->args[1];expected->r[4]=(expected->r[4]&0xffff0000u)|call->args[2];expected->r[3]=call->args[3];expected->r[2]=(expected->r[2]&0xffff0000u)|call->args[4];
        if(call->actor){
            ad_actor++;while(call->slot<40&&rd16(0x49d6cu+206u*call->slot))call->slot++;
            if(call->slot==40){call->full=1;ad_full++;}
            expected->r[0]=206u*(call->full?39u:call->slot);expected->r[1]=(expected->r[1]&0xffff0000u)|call->slot;expected->r[8]=0x49d6cu;
        }else{ad_sprite++;expected->r[8]=0x4208cu;}
        uint16_t x=(call->actor&&call->slot)?0:(call->incoming.sr&16u);
        expected->sr=(uint16_t)((expected->sr&0xffe0u)|(call->full?0u:x|(id==0?4u:0u)|((id&0x8000u)?8u:0u)));
        expected->r[15]=call->sp-16u-(call->actor?16u:14u)-4u;ad_bank(expected);emit(pc);
    }
    if(!call||!call->pending)return;
    if(pc==1456328u)call->native=1;
    read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];ad_stack_observations++;
        if(!task_stack_valid(task,sp))ad_stack_outside++;
        else if(task_original_stack_valid(task,sp)&&sp-task-38u<ad_min_headroom)ad_min_headroom=sp-task-38u;
        if(sp<call->min_sp)call->min_sp=sp;
        if(call->child&&!call->returned){
            uint32_t floor=call->sp-264u;
            if(call->native&&sp<floor){ad_child_below_context++;if(sp>=call->sp-336u)ad_context_SP_inside++;}
            if(sp>=floor&&sp-floor<ad_min_context_clearance)ad_min_context_clearance=sp-floor;
            if(call->sp>=sp&&call->sp-sp>ad_max_child_depth)ad_max_child_depth=call->sp-sp;
        }
    }
    if(pc==(call->actor?0x134dcu:0x137e0u)){
        ad_child_entries++;if(call->full||call->child)ad_errors++;call->child=1;
        ad_compare(&current,&call->expected);
        if(call->native)for(unsigned i=0;i<18;i++)call->context[i]=rd32(call->sp-336u+4u*i);
        uint32_t s=current.r[15]+4u;
        if(rd16(s)!=call->args[0])ad_errors++;s+=2;
        if(call->actor){if(rd16(s)!=call->slot)ad_errors++;s+=2;}
        if(rd32(s)!=call->args[1]||rd16(s+4)!=call->args[2]||rd32(s+6)!=call->args[3]||rd16(s+10)!=call->args[4])ad_errors++;
    }
    if(pc==1456444u||pc==1456540u||pc==0x13b3au||pc==0x13b50u){
        if(call->full||!call->child||call->returned)ad_errors++;
        if(call->native){ad_context_checks++;for(unsigned i=0;i<18;i++)if(rd32(call->sp-336u+4u*i)!=call->context[i])ad_context_collisions++;}
        call->returned=1;call->output=current;ad_child_returns++;
        if(current.r[15]!=call->sp-16u-(call->actor?16u:14u))ad_errors++;
    }
    if(pc==1456382u||pc==0x13b58u){
        struct cpu expected=call->full?call->expected:call->output;
        if(!call->full&&(!call->child||!call->returned))ad_errors++;
        for(unsigned i=2;i<=5;i++)expected.r[i]=call->incoming.r[i];expected.r[15]=call->sp;ad_bank(&expected);
        ad_compare(&current,&expected);
        uint32_t s=call->sp;
        if(rd32(s)!=call->ret||rd16(s+4)!=call->args[0]||rd32(s+6)!=call->args[1]||rd16(s+10)!=call->args[2]||rd32(s+12)!=call->args[3]||rd16(s+16)!=call->args[4])ad_errors++;
        if(s-call->min_sp>ad_max_depth)ad_max_depth=s-call->min_sp;
        ad_returns++;ad_pending--;call->pending=0;emit(pc);
    }
}

/* Original-facing134DC adapter and helper transparency, read-only.
 * Full algorithm/public-store equivalence is the separate component proof. */
#ifndef BIWN_ACTOR_INITIALIZE_TASK
#define BIWN_ACTOR_INITIALIZE_TASK() rd32(0xc0920u)
#endif
struct ai_call {uint32_t task,sp,ret,args[6],object,callback,min_sp,helper;unsigned pending,native,helper_pending;uint32_t context[19];struct cpu incoming;};
static struct ai_call ai_calls[256];static unsigned ai_slots,ai_pending;
static uint64_t ai_entries,ai_native_entries,ai_returns,ai_old_steps,ai_native_steps,ai_errors,ai_helper_entries,ai_helper_returns,ai_context_checks,ai_context_corruptions,ai_stack_observations,ai_stack_outside;
static uint32_t ai_max_depth,ai_min_headroom=0xffffffffu;
static uint32_t ai_sx(uint16_t x){return(uint32_t)(x&0x7fffu)-(uint32_t)(x&0x8000u);}
static uint32_t ai_callback(uint32_t target){switch(target){
case 0x13706:return 0xf4d8;case 0x13714:return 0xedc4;case 0x13722:return 0xfcc2;case 0x13730:return 0x17f80;case 0x1373e:return 0x178e0;case 0x1374a:return 0xf720;case 0x13756:return 0x21d40;case 0x13762:return 0x15080;case 0x1376e:return 0x14fc0;case 0x1377a:return 0xf888;case 0x13786:return 0x15140;case 0x13792:return 0x14100;case 0x1379e:return 0x11f80;case 0x137aa:return 0x128a0;case 0x137b6:return 0x15a80;default:return 0;}}
static void watch_actor_initialize(uint32_t pc){
 if(pc==1457900u)ai_native_entries++;
 if(pc>0x134dcu&&pc<0x137e0u)ai_old_steps++;
 if(pc>=1456580u&&pc<1458200u)ai_native_steps++;
 if(!ai_pending&&pc!=0x134dcu)return;
 uint32_t task=BIWN_ACTOR_INITIALIZE_TASK();struct ai_call *call=NULL;struct cpu current;
 for(unsigned i=0;i<ai_slots;i++)if(ai_calls[i].task==task){call=&ai_calls[i];break;}
 if(pc==0x134dcu){
  if(!call){if(ai_slots==256){ai_errors++;return;}call=&ai_calls[ai_slots++];call->task=task;}
  if(call->pending)ai_errors++;
  read_cpu(&call->incoming);call->sp=call->incoming.r[15];call->ret=rd32(call->sp);call->min_sp=call->sp;
  uint32_t s=call->sp;call->args[0]=rd16(s+4);call->args[1]=rd16(s+6);call->args[2]=rd32(s+8);call->args[3]=rd16(s+12);call->args[4]=rd32(s+14);call->args[5]=rd16(s+18);
  call->object=0x49d6cu+206u*ai_sx((uint16_t)call->args[1]);call->callback=0;
  uint16_t index=(uint16_t)(call->args[0]-4u);
  if(index<=114u){uint16_t offset=(uint16_t)rd16(0x13620u+2u*index);call->callback=ai_callback(0x13620u+ai_sx(offset));}
  call->pending=1;call->native=call->helper_pending=0;ai_pending++;ai_entries++;emit(pc);
 }
 if(!call||!call->pending)return;
 if(pc==1457900u)call->native=1;
 read_cpu(&current);
 if(!(current.sr&0x2000u)){
  uint32_t sp=current.r[15];ai_stack_observations++;
  if(!task_stack_valid(task,sp))ai_stack_outside++;
  else if(task_original_stack_valid(task,sp)&&sp-task-38u<ai_min_headroom)ai_min_headroom=sp-task-38u;
  if(sp<call->min_sp)call->min_sp=sp;
 }
 if(pc==0x102c4u||pc==0x10520u||pc==0xdf6cu){
  if(call->helper_pending)ai_errors++;call->helper_pending=1;call->helper=pc;ai_helper_entries++;
  uint32_t bytes=pc==0xdf6cu?8u:4u;
  if(current.r[15]!=call->sp-32u-bytes-4u)ai_errors++;
  if(pc==0xdf6cu){
   uint32_t slot=ai_sx((uint16_t)call->args[1]);
   if(!call->callback||rd32(current.r[15]+4)!=call->callback||rd32(current.r[15]+8)!=slot||current.r[11]!=slot)ai_errors++;
   if((current.sr&31u)!=((slot==0?4u:0u)|((slot&0x80000000u)?8u:0u)))ai_errors++;
  }else if(rd32(current.r[15]+4)!=call->object||current.r[8]!=call->object)ai_errors++;
  if(call->native){
   for(unsigned i=0;i<19;i++)call->context[i]=rd32(call->sp-480u+4u*i);
   for(unsigned i=0;i<15;i++)if(call->context[i]!=current.r[i])ai_errors++;
   if(call->context[15]!=call->sp||(call->context[16]&0xffffu)!=current.sr)ai_errors++;
  }
 }
 if((call->helper==0x102c4u&&(pc==1457996u||pc==0x135f0u))||(call->helper==0x10520u&&(pc==1458076u||pc==0x13602u))||(call->helper==0xdf6cu&&(pc==1458160u||pc==0x137c6u))){
  if(!call->helper_pending)ai_errors++;
  if(call->native){ai_context_checks++;for(unsigned i=0;i<19;i++)if(rd32(call->sp-480u+4u*i)!=call->context[i])ai_context_corruptions++;}
  uint32_t bytes=call->helper==0xdf6cu?8u:4u;
  if(current.r[15]!=call->sp-32u-bytes)ai_errors++;
  call->helper_pending=0;ai_helper_returns++;
 }
 if(pc==1457954u||pc==0x137deu){
  if(call->helper_pending)ai_errors++;
  const unsigned saved[]={2,3,4,5,6,7,10,11};for(unsigned i=0;i<8;i++)if(current.r[saved[i]]!=call->incoming.r[saved[i]])ai_errors++;
  uint32_t s=call->sp;
  if(current.r[15]!=s||rd32(s)!=call->ret||rd16(s+4)!=call->args[0]||rd16(s+6)!=call->args[1]||rd32(s+8)!=call->args[2]||rd16(s+12)!=call->args[3]||rd32(s+14)!=call->args[4]||rd16(s+18)!=call->args[5])ai_errors++;
  if(s-call->min_sp>ai_max_depth)ai_max_depth=s-call->min_sp;
  ai_pending--;call->pending=0;ai_returns++;emit(pc);
 }
}

/*137E0root/capture/helper/context/task-stack monitor. Read-only; actual sprite
 * algorithm equivalence is a separate full-CPU/ordered-memory fixture proof. */
#ifndef BIWN_SPRITE_CREATE_TASK
#define BIWN_SPRITE_CREATE_TASK() rd32(0xc0920u)
#endif
struct sc_call {uint32_t task,sp,ret,args[5],object,min_sp,helper,allocation_arg;unsigned pending,native,helper_pending;uint32_t context[19];struct cpu incoming;};
static struct sc_call sc_calls[256];static unsigned sc_slots,sc_pending;
static uint64_t sc_entries,sc_native_entries,sc_returns,sc_old_steps,sc_native_steps,sc_errors,sc_helper_entries,sc_helper_returns,sc_context_checks,sc_context_corruptions,sc_stack_observations,sc_stack_outside,sc_position_calls,sc_allocate_calls,sc_decode_calls;
static uint32_t sc_max_depth,sc_min_headroom=0xffffffffu;
static void watch_sprite_create(uint32_t pc){
 if(pc==1460056u)sc_native_entries++;
 if(pc>0x137e0u&&pc<0x13ae0u)sc_old_steps++;
 if(pc>=1458200u&&pc<1460380u)sc_native_steps++;
 if(!sc_pending&&pc!=0x137e0u)return;
 uint32_t task=BIWN_SPRITE_CREATE_TASK();struct sc_call *call=NULL;struct cpu current;
 for(unsigned i=0;i<sc_slots;i++)if(sc_calls[i].task==task){call=&sc_calls[i];break;}
 if(pc==0x137e0u){
  if(!call){if(sc_slots==256){sc_errors++;return;}call=&sc_calls[sc_slots++];call->task=task;}
  if(call->pending)sc_errors++;
  read_cpu(&call->incoming);call->sp=call->incoming.r[15];call->ret=rd32(call->sp);call->min_sp=call->sp;
  uint32_t s=call->sp;call->args[0]=rd16(s+4);call->args[1]=rd32(s+6);call->args[2]=rd16(s+10);call->args[3]=rd32(s+12);call->args[4]=rd16(s+16);
  call->object=0;for(unsigned i=0;i<40;i++)if(!rd16(0x4bd9cu+i*30u)){call->object=0x4bd9cu+i*30u;break;}
  call->pending=1;call->native=call->helper_pending=0;call->allocation_arg=0;sc_pending++;sc_entries++;emit(pc);
 }
 if(!call||!call->pending)return;
 if(pc==1460056u)call->native=1;
 read_cpu(&current);
 if(!(current.sr&0x2000u)){
  uint32_t sp=current.r[15];sc_stack_observations++;
  if(!task_stack_valid(task,sp))sc_stack_outside++;
  else if(task_original_stack_valid(task,sp)&&sp-task-38u<sc_min_headroom)sc_min_headroom=sp-task-38u;
  if(sp<call->min_sp)call->min_sp=sp;
 }
 if(pc==0x105dau||pc==0x152a2u||pc==0xe2b8u){
  if(call->helper_pending)sc_errors++;call->helper_pending=1;call->helper=pc;sc_helper_entries++;
  uint32_t bytes=pc==0xe2b8u?16u:4u;
  if(current.r[15]!=call->sp-52u-bytes-4u)sc_errors++;
  if(pc==0x105dau){sc_position_calls++;if(!call->object||rd32(current.r[15]+4)!=call->object||current.r[11]+current.r[5]!=call->object)sc_errors++;}
  if(pc==0x152a2u){sc_allocate_calls++;call->allocation_arg=rd32(current.r[15]+4);if(call->allocation_arg!=current.r[9]+16u)sc_errors++;}
  if(pc==0xe2b8u){sc_decode_calls++;if(rd32(current.r[15]+4)!=0x6e6a0u||rd32(current.r[15]+8)!=current.r[9]||rd32(current.r[15]+12)!=current.r[7]||rd32(current.r[15]+16)!=call->allocation_arg)sc_errors++;}
  if(call->native){
   for(unsigned i=0;i<19;i++)call->context[i]=rd32(call->sp-500u+4u*i);
   for(unsigned i=0;i<15;i++)if(call->context[i]!=current.r[i])sc_errors++;
   if(call->context[15]!=call->sp||(call->context[16]&0xffffu)!=current.sr)sc_errors++;
  }
 }
 if((call->helper==0x105dau&&(pc==1460166u||pc==0x13882u))||(call->helper==0x152a2u&&(pc==1460246u||pc==0x13a56u))||(call->helper==0xe2b8u&&(pc==1460340u||pc==0x13ad4u))){
  if(!call->helper_pending)sc_errors++;
  if(call->native){sc_context_checks++;for(unsigned i=0;i<19;i++)if(rd32(call->sp-500u+4u*i)!=call->context[i])sc_context_corruptions++;}
  uint32_t bytes=call->helper==0xe2b8u?16u:4u;
  if(current.r[15]!=call->sp-52u-bytes)sc_errors++;
  call->helper_pending=0;sc_helper_returns++;
 }
 if(pc==1460118u||pc==0x13adeu){
  if(call->helper_pending)sc_errors++;
  const unsigned saved[]={2,3,4,5,6,7,10,11,12,13,14};for(unsigned i=0;i<11;i++)if(current.r[saved[i]]!=call->incoming.r[saved[i]])sc_errors++;
  uint32_t s=call->sp;
  if(current.r[15]!=s||rd32(s)!=call->ret||rd16(s+4)!=call->args[0]||rd32(s+6)!=call->args[1]||rd16(s+10)!=call->args[2]||rd32(s+12)!=call->args[3]||rd16(s+16)!=call->args[4])sc_errors++;
  if(s-call->min_sp>sc_max_depth)sc_max_depth=s-call->min_sp;
  sc_pending--;call->pending=0;sc_returns++;emit(pc);
 }
}

/* Read-only public-root, shared-context, virtual-C-boundary and task observer.
 * Algorithm outputs are independently checked by the finite native fixtures.
 * Per-task nested public roots are needed for the original movement control. */
#ifndef BIWN_ACTOR_CHAIN_TASK
#define BIWN_ACTOR_CHAIN_TASK() rd32(0xc0920u)
#endif
static void array(FILE *,const char *,const uint64_t *,unsigned);
static const uint32_t ach_original[3]={0x13c9au,0x13b5au,0x13bb0u};
static const uint32_t ach_original_return[3]={0x13f10u,0x13baeu,0x13c98u};
static const uint32_t ach_compiled[3]={1464848u,1464920u,1464992u};
static const uint32_t ach_return[3]={1464918u,1464990u,1465062u};
static const uint32_t ach_save[3]={40u,8u,4u},ach_args[3]={8u,10u,10u};
static const uint32_t ach_saved_mask[3]={0x3cfcu,0x404u,0x400u};
static const uint32_t ach_helper_return[10]={1465140u,1465186u,1465232u,1465278u,1465324u,1465370u,1465416u,1465462u,1465508u,1465554u};
static const uint32_t ach_helper_target[10]={78912u,57888u,66460u,66244u,66190u,67154u,66460u,66244u,66190u,67154u};
static const uint32_t ach_targets[6]={0x13440u,0xe220u,0x1039cu,0x102c4u,0x1028eu,0x10652u};
struct ach_call{
 uint32_t task,sp,ret,min_sp,context,helper_sp,helper_ret,virtual_sp,virtual_d2,virtual_a2,virtual_kind;
 unsigned pending,native,kind,helper_pending,virtual_pending;
 unsigned char args[10],context_copy[80],virtual_args[10];
 struct cpu incoming;
};
static struct ach_call ach_calls[256];static unsigned ach_slots,ach_pending;
static uint64_t ach_entries[3],ach_native[3],ach_returns[3],ach_old_steps[3],ach_max_depth[3];
static uint64_t ach_min_headroom[3]={0xffffffffu,0xffffffffu,0xffffffffu};
static uint64_t ach_helper_counts[6],ach_virtual_entries[2],ach_virtual_returns[2];
static uint64_t ach_source_steps,ach_errors,ach_context_errors,ach_virtual_errors,ach_stack_outside,ach_stack_observations,ach_context_checks;
static struct ach_call *ach_active(uint32_t task){
 struct ach_call *result=NULL;
 for(unsigned i=0;i<ach_slots;i++)if(ach_calls[i].pending&&ach_calls[i].task==task&&(!result||ach_calls[i].sp<result->sp))result=&ach_calls[i];
 return result;
}
static void watch_actor_chain(uint32_t pc){
 int entering=-1;
 for(unsigned k=0;k<3;k++){
  if(pc==ach_original[k])entering=(int)k;
  uint32_t end=k==0?0x13f12u:k==1?0x13bb0u:0x13c9au;
  if(pc>ach_original[k]&&pc<end)ach_old_steps[k]++;
 }
 if(pc>=1460380u&&pc<1465568u)ach_source_steps++;
 if(!ach_pending&&entering<0)return;
 uint32_t task=BIWN_ACTOR_CHAIN_TASK();struct cpu current;read_cpu(&current);
 if(entering>=0){
  struct ach_call *slot=NULL;
  for(unsigned i=0;i<ach_slots;i++)if(!ach_calls[i].pending){slot=&ach_calls[i];break;}
  if(!slot){if(ach_slots==256){ach_errors++;return;}slot=&ach_calls[ach_slots++];}
  memset(slot,0,sizeof(*slot));slot->incoming=current;slot->task=task;slot->sp=current.r[15];slot->min_sp=slot->sp;slot->ret=rd32(slot->sp);slot->kind=(unsigned)entering;slot->context=slot->sp-ach_save[slot->kind]-320u;
  if(slot->sp>0x1ffff0u){ach_errors++;return;}
  memcpy(slot->args,ram+slot->sp+4u,ach_args[slot->kind]);slot->pending=1;ach_pending++;ach_entries[slot->kind]++;emit(pc);
 }
 struct ach_call *call=ach_active(task);
 if(!call)return;
 for(unsigned k=0;k<3;k++)if(pc==ach_compiled[k]){
  if(call->kind!=k)ach_errors++;
  call->native=1;ach_native[k]++;
 }
 for(unsigned i=0;i<ach_slots;i++){
  struct ach_call *slot=&ach_calls[i];
  if(!slot->pending||slot->task!=task)continue;
  if((current.sr&0x2000u)==(slot->incoming.sr&0x2000u)&&current.r[15]<slot->min_sp)slot->min_sp=current.r[15];
  if(!(current.sr&0x2000u)){
   uint32_t sp=current.r[15];ach_stack_observations++;
   if(!task_stack_valid(task,sp))ach_stack_outside++;
   else if(task_original_stack_valid(task,sp)&&sp-task-38u<ach_min_headroom[slot->kind])ach_min_headroom[slot->kind]=sp-task-38u;
  }
 }
 if(pc==1465064u){
  uint32_t ctx=rd32(current.r[15]+4u),sp=rd32(ctx+60u),entry=rd32(ctx+72u),kind=entry==0x13b5au?0u:1u;
  if(!call->native||call->kind!=0||call->virtual_pending||call->helper_pending||ctx!=call->context||sp!=call->sp-54u||rd32(ctx+76u)!=0x13c9au||(entry!=0x13b5au&&entry!=0x13bb0u))ach_virtual_errors++;
  call->virtual_pending=1;call->virtual_sp=sp;call->virtual_d2=rd32(ctx+8u);call->virtual_a2=rd32(ctx+40u);call->virtual_kind=kind;
  if(sp>0x1ffff2u){ach_virtual_errors++;return;}
  memcpy(call->virtual_args,ram+sp+4u,10);ach_virtual_entries[kind]++;emit(pc);
 }
 if(pc==1465076u){
  uint32_t ctx=call->context,sp=call->virtual_sp;
  if(!call->virtual_pending||call->helper_pending||rd32(ctx+60u)!=sp||rd32(ctx+8u)!=call->virtual_d2||rd32(ctx+40u)!=call->virtual_a2||rd32(ctx+76u)!=0x13c9au||sp>0x1ffff2u||memcmp(ram+sp+4u,call->virtual_args,10))ach_virtual_errors++;
  ach_virtual_returns[call->virtual_kind]++;call->virtual_pending=0;emit(pc);
 }
 if(call->native){
  for(unsigned t=0;t<6;t++)if(pc==ach_targets[t]){
   uint32_t ret=rd32(current.r[15]);int capture=-1;
   for(unsigned i=0;i<10;i++)if(ach_helper_return[i]==ret)capture=(int)i;
   if(capture>=0){
    uint32_t ctx=call->context;
    if(call->helper_pending||ach_helper_target[capture]!=pc)ach_errors++;
    for(unsigned i=0;i<15;i++)if(rd32(ctx+4u*i)!=current.r[i])ach_context_errors++;
    if(rd32(ctx+60u)!=current.r[15]+4u||(rd32(ctx+64u)&0xffffu)!=current.sr||rd32(ctx+76u)!=ach_original[call->kind])ach_context_errors++;
    if(ctx>0x1fffb0u){ach_context_errors++;return;}
    memcpy(call->context_copy,ram+ctx,80);call->helper_sp=current.r[15];call->helper_ret=ret;call->helper_pending=1;ach_helper_counts[t]++;
   }
  }
  if(call->helper_pending&&pc==call->helper_ret){
   if(current.r[15]!=call->helper_sp+4u||memcmp(call->context_copy,ram+call->context,80))ach_context_errors++;
   ach_context_checks++;call->helper_pending=0;
  }
 }
 if(pc==ach_return[call->kind]||pc==ach_original_return[call->kind]){
  if(call->helper_pending||call->virtual_pending||current.r[15]!=call->sp||rd32(call->sp)!=call->ret||memcmp(ram+call->sp+4u,call->args,ach_args[call->kind]))ach_errors++;
  for(unsigned i=0;i<15;i++)if((ach_saved_mask[call->kind]&(1u<<i))&&current.r[i]!=call->incoming.r[i])ach_errors++;
  uint32_t depth=call->sp-call->min_sp;if(depth>ach_max_depth[call->kind])ach_max_depth[call->kind]=depth;
  ach_returns[call->kind]++;call->pending=0;ach_pending--;emit(pc);
 }
}
static void ach_dump(FILE *file){
 array(file,"ach_entries",ach_entries,3);array(file,"ach_native",ach_native,3);array(file,"ach_returns",ach_returns,3);array(file,"ach_old_steps",ach_old_steps,3);
 array(file,"ach_max_depth",ach_max_depth,3);array(file,"ach_min_headroom",ach_min_headroom,3);array(file,"ach_helper_counts",ach_helper_counts,6);array(file,"ach_virtual_entries",ach_virtual_entries,2);array(file,"ach_virtual_returns",ach_virtual_returns,2);
 fprintf(file,",\"ach_pending\":%u,\"ach_source_steps\":%llu,\"ach_errors\":%llu,\"ach_context_errors\":%llu,\"ach_virtual_errors\":%llu,\"ach_stack_outside\":%llu,\"ach_stack_observations\":%llu,\"ach_context_checks\":%llu",ach_pending,(unsigned long long)ach_source_steps,(unsigned long long)ach_errors,(unsigned long long)ach_context_errors,(unsigned long long)ach_virtual_errors,(unsigned long long)ach_stack_outside,(unsigned long long)ach_stack_observations,(unsigned long long)ach_context_checks);
}

/* Read-only four-leaf navigation boundary/context/task observer.
 * Full algorithm equivalence remains the separate original-execution matrix. */
#ifndef BIWN_NAVIGATION_TASK
#define BIWN_NAVIGATION_TASK() rd32(0xc0920u)
#endif
static void array(FILE *,const char *,const uint64_t *,unsigned);
static const uint32_t an_original[4]={0xf368u,0x13f12u,0x13f7cu,0x13feau};
static const uint32_t an_original_end[4]={0xf4d8u,0x13f7cu,0x13feau,0x1404cu};
static const uint32_t an_original_returns[7]={0xf4d6u,0x13f58u,0x13f7au,0x13fc6u,0x13fe8u,0x14028u,0x1404au};
static const unsigned an_return_kind[7]={0,1,1,2,2,3,3};
static const uint32_t an_compiled[4]={1466892u,1466956u,1467012u,1467068u};
static const uint32_t an_return[4]={1466954u,1467010u,1467066u,1467122u};
struct an_call{struct cpu incoming;uint32_t task,sp,ret,min_sp,context;unsigned char args[8];unsigned pending,native,kind,context_entered;};
static struct an_call an_calls[256];static unsigned an_slots,an_pending;
static uint64_t an_entries[4],an_native[4],an_returns[4],an_old_steps[4],an_max_depth[4];
static uint64_t an_min_headroom[4]={0xffffffffu,0xffffffffu,0xffffffffu,0xffffffffu};
static uint64_t an_errors,an_context_errors,an_context_entries,an_context_returns,an_stack_outside,an_stack_observations,an_source_steps;
static void watch_actor_navigation(uint32_t pc){
 int entering=-1;
 for(unsigned k=0;k<4;k++){if(pc==an_original[k])entering=(int)k;else if(pc>an_original[k]&&pc<an_original_end[k])an_old_steps[k]++;}
 if(pc>=1465568u&&pc<1467156u)an_source_steps++;
 if(!an_pending&&entering<0)return;
 struct cpu current;read_cpu(&current);uint32_t task=BIWN_NAVIGATION_TASK();struct an_call*call=NULL;
 for(unsigned i=0;i<an_slots;i++)if(an_calls[i].pending&&an_calls[i].task==task)call=&an_calls[i];
 if(entering>=0){
  if(call){an_errors++;return;}
  for(unsigned i=0;i<an_slots;i++)if(!an_calls[i].pending){call=&an_calls[i];break;}
  if(!call){if(an_slots==256){an_errors++;return;}call=&an_calls[an_slots++];}
  memset(call,0,sizeof(*call));call->incoming=current;call->task=task;call->sp=call->min_sp=current.r[15];call->kind=(unsigned)entering;call->context=call->sp-96u-(entering==0?8u:0u);
  if(call->sp>0x1ffff0u||call->sp<104u){an_errors++;return;}
  call->ret=rd32(call->sp);memcpy(call->args,ram+call->sp+4u,8);call->pending=1;an_pending++;an_entries[call->kind]++;
 }
 if(!call||!call->pending)return;
 unsigned k=call->kind;
 if(pc==an_compiled[k]){call->native=1;an_native[k]++;}
 if((current.sr&0x2000u)==(call->incoming.sr&0x2000u)&&current.r[15]<call->min_sp)call->min_sp=current.r[15];
 if(!(current.sr&0x2000u)){
  an_stack_observations++;uint32_t sp=current.r[15];
  if(!task_stack_valid(task,sp))an_stack_outside++;
  else if(task_original_stack_valid(task,sp)&&sp-task-38u<an_min_headroom[k])an_min_headroom[k]=sp-task-38u;
 }
 if(pc==1465622u){
  uint32_t ctx=call->context;if(!call->native||call->context_entered||ctx>0x1fffb8u||rd32(current.r[15]+4u)!=ctx){an_context_errors++;return;}
  for(unsigned i=0;i<15;i++)if(rd32(ctx+4u*i)!=call->incoming.r[i])an_context_errors++;
  if(rd32(ctx+60u)!=call->sp||(rd32(ctx+64u)&0xffffu)!=call->incoming.sr||rd32(ctx+68u)!=an_original[k])an_context_errors++;
  call->context_entered=1;an_context_entries++;
 }
 int returning=pc==an_return[k];
 for(unsigned i=0;i<7;i++)if(pc==an_original_returns[i]&&k==an_return_kind[i])returning=1;
 if(returning){
  if(current.r[15]!=call->sp||rd32(call->sp)!=call->ret||memcmp(ram+call->sp+4u,call->args,8))an_errors++;
  for(unsigned i=0;i<15;i++)if((0x7cfcu&(1u<<i))&&current.r[i]!=call->incoming.r[i])an_errors++;
  if(call->native){
   uint32_t ctx=call->context;if(!call->context_entered)an_context_errors++;
   for(unsigned i=0;i<15;i++)if(rd32(ctx+4u*i)!=current.r[i])an_context_errors++;
   if(rd32(ctx+60u)!=call->sp||(rd32(ctx+64u)&0xffffu)!=current.sr||rd32(ctx+68u)!=an_original[k])an_context_errors++;
   an_context_returns++;
  }
  uint32_t depth=call->sp-call->min_sp;if(depth>an_max_depth[k])an_max_depth[k]=depth;
  an_returns[k]++;call->pending=0;an_pending--;
 }
}
static void an_dump(FILE*f){
 array(f,"an_entries",an_entries,4);array(f,"an_native",an_native,4);array(f,"an_returns",an_returns,4);array(f,"an_old_steps",an_old_steps,4);array(f,"an_max_depth",an_max_depth,4);array(f,"an_min_headroom",an_min_headroom,4);
 fprintf(f,",\"an_pending\":%u,\"an_errors\":%llu,\"an_context_errors\":%llu,\"an_context_entries\":%llu,\"an_context_returns\":%llu,\"an_stack_outside\":%llu,\"an_stack_observations\":%llu,\"an_source_steps\":%llu",an_pending,(unsigned long long)an_errors,(unsigned long long)an_context_errors,(unsigned long long)an_context_entries,(unsigned long long)an_context_returns,(unsigned long long)an_stack_outside,(unsigned long long)an_stack_observations,(unsigned long long)an_source_steps);
}

#ifndef BIWN_DIRECTION_TASK
#define BIWN_DIRECTION_TASK() rd32(0xc0920u)
#endif
int biwn_direction_predict(const unsigned char *,const uint32_t *,uint16_t,uint32_t *,uint16_t *);
struct dir_call {uint32_t task,sp,context,min_sp;unsigned pending,native;struct cpu incoming;uint32_t expected[16];uint16_t expected_sr;unsigned char args[4];};
static struct dir_call dir_calls[256];
static unsigned dir_slots,dir_pending;
static uint64_t dir_entries,dir_native,dir_returns,dir_old_steps,dir_source_steps,dir_errors,dir_context_errors,dir_stack_outside,dir_stack_observations,dir_context_entries,dir_context_returns;
static uint32_t dir_max_depth,dir_min_headroom=0xffffffffu;
static uint32_t dir_u32(uint32_t address){return rd32(address);}
static void watch_direction(uint32_t pc){
 if(!dir_pending&&pc!=0x13440u&&!(pc>=1467156u&&pc<1467954u)&&!(pc>0x13440u&&pc<0x134dcu))return;
 uint32_t task=BIWN_DIRECTION_TASK();struct cpu current;read_cpu(&current);struct dir_call *call=NULL;
 for(unsigned i=0;i<dir_slots;i++)if(dir_calls[i].task==task){call=&dir_calls[i];break;}
 if(pc==0x13440u){
  if(!call){if(dir_slots==256){dir_errors++;return;}call=&dir_calls[dir_slots++];call->task=task;}
  if(call->pending){dir_errors++;return;}
  call->sp=current.r[15];call->incoming=current;call->min_sp=call->sp;call->context=call->sp-124u;call->native=0;
  if(call->sp>0x1ffff8u||biwn_direction_predict(ram,current.r,current.sr,call->expected,&call->expected_sr)){dir_errors++;return;}
  memcpy(call->args,ram+call->sp+4u,4);call->pending=1;dir_pending++;dir_entries++;
 }
 if(pc>0x13440u&&pc<0x134dcu)dir_old_steps++;
 if(pc>=1467156u&&pc<1467954u)dir_source_steps++;
 if(pc==1467808u){dir_native++;if(!call||!call->pending)dir_errors++;else call->native=1;}
 if(!call||!call->pending)return;
 if(current.r[15]<call->min_sp)call->min_sp=current.r[15];
 if(!(current.sr&0x2000u)){
  dir_stack_observations++;uint32_t sp=current.r[15];
  if(!task_stack_valid(task,sp))dir_stack_outside++;
  else if(task_original_stack_valid(task,sp)&&sp-task-38u<dir_min_headroom)dir_min_headroom=sp-task-38u;
 }
 if(pc==1467188u){
  dir_context_entries++;uint32_t context=rd32(current.r[15]+4u);
  if(!call->native||context!=call->context)dir_context_errors++;
  else{
   for(unsigned i=0;i<16;i++)if(dir_u32(context+4u*i)!=call->incoming.r[i])dir_context_errors++;
   if(rd32(context+64u)!=(uint32_t)call->incoming.sr||rd32(context+68u)!=0x13440u)dir_context_errors++;
  }
 }
 if(pc==1467870u||pc==0x134dau){
  dir_returns++;
  if(pc==1467870u&&!call->native)dir_errors++;
  for(unsigned i=0;i<16;i++)if(current.r[i]!=call->expected[i])dir_errors++;
  if(current.sr!=call->expected_sr||current.usp!=call->incoming.usp||current.ssp!=call->incoming.ssp||memcmp(ram+call->sp+4u,call->args,4))dir_errors++;
  if(call->native){
   dir_context_returns++;
   for(unsigned i=0;i<16;i++)if(rd32(call->context+4u*i)!=current.r[i])dir_context_errors++;
   if(rd32(call->context+64u)!=(uint32_t)current.sr||rd32(call->context+68u)!=0x13440u)dir_context_errors++;
  }
  if(call->sp-call->min_sp>dir_max_depth)dir_max_depth=call->sp-call->min_sp;
  call->pending=0;dir_pending--;
 }
}

static void dir_dump(FILE *file){fprintf(file,",\"dir_entries\":%llu,\"dir_native\":%llu,\"dir_returns\":%llu,\"dir_old_steps\":%llu,\"dir_source_steps\":%llu,\"dir_errors\":%llu,\"dir_context_errors\":%llu,\"dir_stack_outside\":%llu,\"dir_stack_observations\":%llu,\"dir_context_entries\":%llu,\"dir_context_returns\":%llu,\"dir_pending\":%llu,\"dir_max_depth\":%llu,\"dir_min_headroom\":%llu",(unsigned long long)dir_entries,(unsigned long long)dir_native,(unsigned long long)dir_returns,(unsigned long long)dir_old_steps,(unsigned long long)dir_source_steps,(unsigned long long)dir_errors,(unsigned long long)dir_context_errors,(unsigned long long)dir_stack_outside,(unsigned long long)dir_stack_observations,(unsigned long long)dir_context_entries,(unsigned long long)dir_context_returns,(unsigned long long)dir_pending,(unsigned long long)dir_max_depth,(unsigned long long)dir_min_headroom);}

/* Read-only eight-root oracle. Original CMPI captures after the synchronized read at retirement; native MOVEA captures its actual A0 result. Pre-read peeks are diagnostic only. No GPU execution occurs in the observer. */
struct mb_call{uint32_t task,sp,context,minimum,kind,args[5],ack,pre_ack;unsigned pending,native,helpers,wait_active,ack_seen;struct cpu incoming;};
static struct mb_call mb_calls[256];
static unsigned mb_slots,mb_pending;
static uint64_t mb_entries[8],mb_native[8],mb_returns[8],mb_old_steps,mb_source_steps,mb_errors,mb_context_errors,mb_helpers,mb_context_entries,mb_context_returns,mb_stack_outside,mb_stack_observations,mb_ack_checks,mb_stale_previews;
static uint32_t mb_max_depth,mb_min_headroom=0xffffffffu;
static const uint32_t mb_original[8]={0xe0a6u,0xe0f2u,0xe148u,0xe19eu,0xe202u,0xe220u,0xe26cu,0xe2b8u},mb_end[8]={0xe0f2u,0xe148u,0xe19eu,0xe202u,0xe220u,0xe26cu,0xe2b8u,0xe2f4u},mb_code[8]={0x167134u,0x1671bau,0x167240u,0x1672c6u,0x16734cu,0x1673d2u,0x167458u,0x1674deu},mb_return[8]={0x1671b8u,0x16723eu,0x1672c4u,0x16734au,0x1673d0u,0x167456u,0x1674dcu,0x167562u},mb_command[8]={0x4d80u,0x6ae0u,0x6da0u,0x52e0u,0x57a0u,0x4320u,0x4720u,0x4b00u},mb_args[8]={0x0u,0x0u,0x0u,0x0u,0x0u,0x5u,0x5u,0x3u};
static const uint32_t mb_poll[16]={0xe0deu,0xe134u,0xe18au,0xe1eeu,0xe212u,0xe258u,0xe2a4u,0xe2e0u,0x166bbau,0x166c80u,0x166d3cu,0x166e12u,0x166e96u,0x166f5eu,0x167020u,0x1670cau};
static uint32_t(*mb_gpu_read)(uint32_t,uint32_t);
void mb_set_gpu_reader(void*fn){mb_gpu_read=(uint32_t(*)(uint32_t,uint32_t))fn;}
static uint16_t mb_upper(const struct mb_call*call){uint16_t sr=(uint16_t)(call->incoming.sr&0xfff0u);return call->kind==3?(uint16_t)(sr&0xffefu):sr;}
static uint16_t mb_cmp_sr(const struct mb_call*call){uint32_t a=call->ack,b=mb_command[call->kind],v=a-b;return(uint16_t)(mb_upper(call)|(v?0u:4u)|((v&0x80000000u)?8u:0u)|((((a^b)&(a^v))&0x80000000u)?2u:0u)|(a<b?1u:0u));}
static void watch_mailbox(uint32_t pc){
 int entry=-1,native=-1,ret=-1,original_ret=-1;
 for(unsigned k=0;k<8;k++){if(pc==mb_original[k])entry=(int)k;if(pc==mb_code[k])native=(int)k;if(pc==mb_return[k])ret=(int)k;if(pc==mb_end[k]-2u)original_ret=(int)k;}
 if(!mb_pending&&entry<0&&!(pc>=0x166b68u&&pc<0x1675a0u))return;
 uint32_t task=rd32(0xc0920u);struct cpu current;read_cpu(&current);struct mb_call*call=NULL;
 for(unsigned i=0;i<mb_slots;i++)if(mb_calls[i].task==task){call=&mb_calls[i];break;}
 if(entry>=0){
  if(!call){if(mb_slots==256){mb_errors++;return;}call=&mb_calls[mb_slots++];call->task=task;}
  if(call->pending){mb_errors++;return;}
  call->sp=current.r[15];call->context=task_arena_top(task)-124u;call->minimum=call->sp;call->kind=(unsigned)entry;call->native=call->helpers=call->wait_active=call->ack_seen=0;call->incoming=current;
  if(call->sp>0x1fffe8u||call->sp<96u){mb_errors++;return;}
  for(unsigned i=0;i<mb_args[entry];i++)call->args[i]=rd32(call->sp+4u+4u*i);
  call->pending=1;mb_pending++;mb_entries[entry]++;
 }
 for(unsigned k=0;k<8;k++)if(pc>mb_original[k]&&pc<mb_end[k])mb_old_steps++;
 if(pc>=0x166b68u&&pc<0x1675a0u)mb_source_steps++;
 if(native>=0){
  if(!call||!call->pending)mb_errors++;
  else{if((unsigned)native!=call->kind)mb_errors++;call->native=1;arena_active[task_arena_slot(task)]=1;arena_used[task_arena_slot(task)]=1;mb_native[native]++;}
 }
 if(!call||!call->pending)return;
 for(unsigned i=0;i<16;i++)if(pc==mb_poll[i]){if(!mb_gpu_read){mb_errors++;return;}call->pre_ack=mb_gpu_read(0xf03204u,0);}
 if(current.r[15]<call->minimum&&task_original_stack_valid(task,current.r[15]))call->minimum=current.r[15];
 if(call->native&&task_arena_stack_valid(task,current.r[15])){uint32_t depth=task_arena_top(task)-current.r[15];if(depth>arena_max_depth)arena_max_depth=depth;arena_stack_observations++;}
 if(!(current.sr&0x2000u)){uint32_t sp=current.r[15];mb_stack_observations++;if(!task_stack_valid(task,sp))mb_stack_outside++;else if(task_original_stack_valid(task,sp)&&sp-task-38u<mb_min_headroom)mb_min_headroom=sp-task-38u;}
 if(pc==0x166b68u){
  mb_context_entries++;uint32_t context=rd32(current.r[15]+4u);
  if(!call->native||context!=call->context)mb_context_errors++;
  else{for(unsigned i=0;i<16;i++)if(rd32(context+4u*i)!=call->incoming.r[i])mb_context_errors++;
   if(rd32(context+64u)!=(uint32_t)call->incoming.sr||rd32(context+68u)!=mb_original[call->kind])mb_context_errors++;}
 }
 if(pc==0xe0a4u||pc==0x162720u)call->wait_active=0;
 if(pc==0xe098u&&!call->wait_active){
  call->wait_active=1;mb_helpers++;
  if(call->helpers>=(call->kind==4?1u:2u))mb_errors++;
  for(unsigned i=0;i<15;i++){uint32_t want=call->incoming.r[i];if(call->helpers&&call->kind==3&&i==0)want=0x47bc8u;if(current.r[i]!=want)mb_errors++;}
  if(current.r[15]!=call->sp-4u)mb_errors++;
  if(!call->helpers){if(current.sr!=call->incoming.sr)mb_errors++;}
  else if(!call->ack_seen||current.sr!=mb_cmp_sr(call))mb_errors++;
  call->helpers++;
 }
 if(ret>=0||original_ret>=0){
  unsigned kind=(unsigned)(ret>=0?ret:original_ret);mb_returns[kind]++;
  if(kind!=call->kind||call->helpers!=(kind==4?1u:2u)||!call->ack_seen)mb_errors++;
  if(ret>=0&&!call->native)mb_errors++;
  for(unsigned i=0;i<16;i++){uint32_t want=call->incoming.r[i];if(kind==3&&i==0)want=0x47bc8u;if(current.r[i]!=want)mb_errors++;}
  uint16_t sr=kind==4?mb_cmp_sr(call):(uint16_t)(mb_upper(call)|4u);
  if(current.sr!=sr||current.usp!=call->incoming.usp||current.ssp!=call->incoming.ssp)mb_errors++;
  for(unsigned i=0;i<mb_args[kind];i++)if(rd32(call->sp+4u+4u*i)!=call->args[i])mb_errors++;
  if(call->native){mb_context_returns++;for(unsigned i=0;i<16;i++)if(rd32(call->context+4u*i)!=current.r[i])mb_context_errors++;
   if(rd32(call->context+64u)!=(uint32_t)current.sr||rd32(call->context+68u)!=mb_original[kind])mb_context_errors++;}
  if(call->sp-call->minimum>mb_max_depth)mb_max_depth=call->sp-call->minimum;
  if(call->native){arena_check_guards();arena_active[task_arena_slot(task)]=0;}
  call->pending=0;mb_pending--;
 }
}
static void(*mb_next_retired)(uint32_t,int32_t);
void mb_set_next_retired(void*fn){mb_next_retired=(void(*)(uint32_t,int32_t))fn;}
static void mb_capture_retired(uint32_t pc){
 if(!mb_pending)return;
 unsigned index;for(index=0;index<16;index++)if(pc==mb_poll[index])break;
 if(index==16)return;
 uint32_t task=rd32(0xc0920u);struct mb_call*call=NULL;
 for(unsigned i=0;i<mb_slots;i++)if(mb_calls[i].task==task&&mb_calls[i].pending){call=&mb_calls[i];break;}
 if(!call){mb_errors++;return;}
 if(index<8){if(!mb_gpu_read){mb_errors++;return;}call->ack=mb_gpu_read(0xf03204u,0);}
 else{struct cpu after;read_cpu(&after);call->ack=after.r[8];}
 call->ack_seen=1;mb_ack_checks++;if(call->ack!=call->pre_ack)mb_stale_previews++;
}
void mb_retired(uint32_t pc,int32_t cycles){mb_capture_retired(pc);if(mb_next_retired)mb_next_retired(pc,cycles);}

static void mb_dump(FILE*file){
 fprintf(file,",\"mb_stale_previews\":%llu",(unsigned long long)mb_stale_previews);
 const uint64_t*arrays[]={mb_entries,mb_native,mb_returns};const char*names[]={"mb_entries","mb_native","mb_returns"};
 for(unsigned j=0;j<3;j++){fprintf(file,",\"%s\":[",names[j]);for(unsigned k=0;k<8;k++)fprintf(file,"%s%llu",k?",":"",(unsigned long long)arrays[j][k]);fputc(']',file);}
 fprintf(file,",\"mb_old_steps\":%llu,\"mb_source_steps\":%llu,\"mb_errors\":%llu,\"mb_context_errors\":%llu,\"mb_helpers\":%llu,\"mb_context_entries\":%llu,\"mb_context_returns\":%llu,\"mb_pending\":%u,\"mb_stack_outside\":%llu,\"mb_stack_observations\":%llu,\"mb_max_depth\":%u,\"mb_min_headroom\":%u,\"mb_ack_checks\":%llu",(unsigned long long)mb_old_steps,(unsigned long long)mb_source_steps,(unsigned long long)mb_errors,(unsigned long long)mb_context_errors,(unsigned long long)mb_helpers,(unsigned long long)mb_context_entries,(unsigned long long)mb_context_returns,mb_pending,(unsigned long long)mb_stack_outside,(unsigned long long)mb_stack_observations,mb_max_depth,mb_min_headroom,(unsigned long long)mb_ack_checks);
}


static int retained_observer_quiescent(void){return !(pool_pending||acquire_pending||table_pending||leaf_pending_any||geometry_pending||select_pending||scan_pending||door_pending||interior_pending||ad_pending||ai_pending||sc_pending||ach_pending||an_pending||dir_pending||mb_pending);}

static int32_t face_retained_observe(uint32_t pc) {
    steps++;
    watch_pool_arena(pc);watch_mailbox(pc);watch_acquire(pc);watch_table(pc);watch_leaf(pc);watch_geometry(pc);watch_select(pc);watch_scan(pc);watch_door(pc);watch_interior(pc);watch_actor_dispatch(pc);watch_actor_initialize(pc);watch_sprite_create(pc);watch_actor_chain(pc);watch_actor_navigation(pc);watch_direction(pc);
    if(pc==0x400a){
        entry_copies++;
        if(candidate&&memcmp(ram+0x15edc0,payload,payload_size))copy_errors++;
    }
    if(pc==0x155c0){heap_inits++;heap_base=rd32(0x112d60);}
    if(pc>=0x15edc0&&pc<0x15edc0+payload_size)resident_steps++;
    if(pc>=rng[0]&&pc<rng[8]){
        for(unsigned i=0;i<8;i++){
            if(pc==rng[i]){rng_entries[i]++;emit(pc);}
            else if(pc>rng[i]&&pc<rng[i+1])old_rng_steps++;
        }
    }
    if(pc>=0xe540&&pc<0xe61c){
        int entry=0;
        for(unsigned i=0;i<3;i++)if(pc==math[i]){math_entries[i]++;entry=1;}
        if(!entry)old_math_steps++;
    }
    if(pc>=0x1b71e&&pc<0x1b780)old_keypad_steps++;
    if(pc==0x18e92||pc==0x1a0f8||pc==0x20f0c||pc==0x20f78){
        for(unsigned i=0;i<4;i++)if(pc==boundaries[i])boundary_entries[i]++;
        emit(pc);
    }
    if(pc==0x1b0ee){
        marker_steps++;
        if(last_marker_frame!=frame){last_marker_frame=frame;emit(pc);}
    }
    int32_t result=next_owner?next_owner(pc):0;if(result)errors++;return result;
}
static void array(FILE *file,const char *name,const uint64_t *values,unsigned count){
    fprintf(file,",\"%s\":[",name);
    for(unsigned i=0;i<count;i++)fprintf(file,"%s%llu",i?",":"",(unsigned long long)values[i]);
    fputc(']',file);
}
int finish_observe(const char *path){
    if(events&&fclose(events))errors++;
    FILE *file=fopen(path,"w");if(!file)return 1;
    fprintf(file,"{\"instructions\":%llu,\"entry_copies\":%llu,\"copy_errors\":%llu,"
        "\"heap_inits\":%llu,\"heap_base\":%u,\"resident_steps\":%llu,"
        "\"old_rng_steps\":%llu,\"old_math_steps\":%llu,\"old_keypad_steps\":%llu,"
        "\"marker_steps\":%llu,\"events\":%llu,\"event_record_bytes\":%u,\"errors\":%u",
        (unsigned long long)steps,(unsigned long long)entry_copies,(unsigned long long)copy_errors,
        (unsigned long long)heap_inits,heap_base,(unsigned long long)resident_steps,
        (unsigned long long)old_rng_steps,(unsigned long long)old_math_steps,(unsigned long long)old_keypad_steps,
        (unsigned long long)marker_steps,(unsigned long long)event_count,(unsigned)sizeof(struct event),errors);

    fprintf(file,",\"acquire_entries\":%llu,\"acquire_native_entries\":%llu,\"acquire_returns\":%llu,\"acquire_old_steps\":%llu,\"acquire_monitor_errors\":%llu,\"acquire_native_steps\":%llu,\"acquire_pending\":%u,\"acquire_loader_calls\":%llu",
        (unsigned long long)acquire_entries,(unsigned long long)acquire_native_entries,(unsigned long long)acquire_returns,(unsigned long long)acquire_old_steps,(unsigned long long)acquire_monitor_errors,(unsigned long long)acquire_native_steps,acquire_pending,(unsigned long long)acquire_loader_calls);
    fprintf(file,",\"acquire_user_stack_observations\":%llu,\"acquire_user_stack_outside\":%llu,\"acquire_user_min_headroom\":%u,\"acquire_max_private_depth\":%u",
        (unsigned long long)acquire_user_stack_observations,(unsigned long long)acquire_user_stack_outside,acquire_user_min_headroom,acquire_max_private_depth);


    fprintf(file,",\"table_entries\":%llu,\"table_native_entries\":%llu,\"table_returns\":%llu,\"table_old_steps\":%llu,\"table_errors\":%llu,\"table_pending\":%u,\"table_native_steps\":%llu",(unsigned long long)table_entries,(unsigned long long)table_native_entries,(unsigned long long)table_returns,(unsigned long long)table_old_steps,(unsigned long long)table_errors,table_pending,(unsigned long long)table_native_steps);


    array(file,"lookup_counts",leaf_counts[0],8);array(file,"single_counts",leaf_counts[1],8);array(file,"multi_counts",leaf_counts[2],8);array(file,"leaf_min_headroom",leaf_min_headroom,3);array(file,"leaf_max_depth",leaf_max_depth,3);
    fprintf(file,",\"leaf_pending\":%u,\"lookup_matches\":%llu,\"lookup_misses\":%llu,\"single_decrements\":%llu,\"multi_nonnegative\":%llu,\"multi_decrements\":%llu,\"heap_floor_errors\":%llu",leaf_pending_any,(unsigned long long)lookup_matches,(unsigned long long)lookup_misses,(unsigned long long)single_decrements,(unsigned long long)multi_nonnegative,(unsigned long long)multi_decrements,(unsigned long long)heap_floor_errors);


    fprintf(file,",\"geometry_entries\":%llu,\"geometry_native_entries\":%llu,\"geometry_returns\":%llu,\"geometry_old_steps\":%llu,\"geometry_native_steps\":%llu,\"geometry_errors\":%llu,\"geometry_pending\":%u,\"geometry_early\":%llu,\"geometry_inside\":%llu,\"geometry_last_outside\":%llu,\"geometry_user_observations\":%llu,\"geometry_stack_outside\":%llu,\"geometry_min_headroom\":%u,\"geometry_max_depth\":%u",(unsigned long long)geometry_entries,(unsigned long long)geometry_native_entries,(unsigned long long)geometry_returns,(unsigned long long)geometry_old_steps,(unsigned long long)geometry_native_steps,(unsigned long long)geometry_errors,geometry_pending,(unsigned long long)geometry_early,(unsigned long long)geometry_inside,(unsigned long long)geometry_last_outside,(unsigned long long)geometry_user_observations,(unsigned long long)geometry_stack_outside,geometry_min_headroom,geometry_max_depth);


    fprintf(file,",\"select_entries\":%llu,\"select_native_entries\":%llu,\"select_returns\":%llu,\"select_old_steps\":%llu,\"select_native_steps\":%llu,\"select_errors\":%llu,\"select_pending\":%u,\"select_successes\":%llu,\"select_failures\":%llu,\"select_user_observations\":%llu,\"select_stack_outside\":%llu,\"select_min_headroom\":%u,\"select_max_depth\":%u",(unsigned long long)select_entries,(unsigned long long)select_native_entries,(unsigned long long)select_returns,(unsigned long long)select_old_steps,(unsigned long long)select_native_steps,(unsigned long long)select_errors,select_pending,(unsigned long long)select_successes,(unsigned long long)select_failures,(unsigned long long)select_user_observations,(unsigned long long)select_stack_outside,select_min_headroom,select_max_depth);


    fprintf(file,",\"scan_entries\":%llu,\"scan_native_entries\":%llu,\"scan_returns\":%llu,\"scan_old_steps\":%llu,\"scan_native_steps\":%llu,\"scan_errors\":%llu,\"scan_pending\":%u,\"scan_successes\":%llu,\"scan_failures\":%llu,\"scan_skips\":%llu,\"scan_iterations\":%llu,\"scan_user_observations\":%llu,\"scan_stack_outside\":%llu,\"scan_min_headroom\":%u,\"scan_max_depth\":%u",(unsigned long long)scan_entries,(unsigned long long)scan_native_entries,(unsigned long long)scan_returns,(unsigned long long)scan_old_steps,(unsigned long long)scan_native_steps,(unsigned long long)scan_errors,scan_pending,(unsigned long long)scan_successes,(unsigned long long)scan_failures,(unsigned long long)scan_skips,(unsigned long long)scan_iterations,(unsigned long long)scan_user_observations,(unsigned long long)scan_stack_outside,scan_min_headroom,scan_max_depth);


    fprintf(file,",\"door_entries\":%llu,\"door_native_entries\":%llu,\"door_returns\":%llu,\"door_old_steps\":%llu,\"door_native_steps\":%llu,\"door_errors\":%llu,\"door_pending\":%u,\"door_count_rejects\":%llu,\"door_sentinels\":%llu,\"door_key_mismatches\":%llu,\"door_successes\":%llu,\"door_user_observations\":%llu,\"door_stack_outside\":%llu,\"door_min_headroom\":%u,\"door_max_depth\":%u",(unsigned long long)door_entries,(unsigned long long)door_native_entries,(unsigned long long)door_returns,(unsigned long long)door_old_steps,(unsigned long long)door_native_steps,(unsigned long long)door_errors,door_pending,(unsigned long long)door_count_rejects,(unsigned long long)door_sentinels,(unsigned long long)door_key_mismatches,(unsigned long long)door_successes,(unsigned long long)door_user_observations,(unsigned long long)door_stack_outside,door_min_headroom,door_max_depth);


    fprintf(file,",\"interior_entries\":%llu,\"interior_native_entries\":%llu,\"interior_returns\":%llu,\"interior_old_steps\":%llu,\"interior_native_steps\":%llu,\"interior_errors\":%llu,\"interior_skips\":%llu,\"interior_successes\":%llu,\"interior_failures\":%llu,\"interior_iterations\":%llu,\"interior_user_observations\":%llu,\"interior_stack_outside\":%llu",(unsigned long long)interior_entries,(unsigned long long)interior_native_entries,(unsigned long long)interior_returns,(unsigned long long)interior_old_steps,(unsigned long long)interior_native_steps,(unsigned long long)interior_errors,(unsigned long long)interior_skips,(unsigned long long)interior_successes,(unsigned long long)interior_failures,(unsigned long long)interior_iterations,(unsigned long long)interior_user_observations,(unsigned long long)interior_stack_outside);
    fprintf(file,",\"interior_pending\":%u,\"interior_min_headroom\":%u,\"interior_max_depth\":%u",interior_pending,interior_min_headroom,interior_max_depth);
    fprintf(file,",\"interior_kind_entries\":[%llu,%llu]",(unsigned long long)interior_kind_entries[0],(unsigned long long)interior_kind_entries[1]);
    fprintf(file,",\"interior_kind_successes\":[%llu,%llu]",(unsigned long long)interior_kind_successes[0],(unsigned long long)interior_kind_successes[1]);
    fprintf(file,",\"interior_kind_failures\":[%llu,%llu]",(unsigned long long)interior_kind_failures[0],(unsigned long long)interior_kind_failures[1]);

    fprintf(file,",\"ad_entries\":%llu",(unsigned long long)ad_entries);
    fprintf(file,",\"ad_native_entries\":%llu",(unsigned long long)ad_native_entries);
    fprintf(file,",\"ad_returns\":%llu",(unsigned long long)ad_returns);
    fprintf(file,",\"ad_old_steps\":%llu",(unsigned long long)ad_old_steps);
    fprintf(file,",\"ad_native_steps\":%llu",(unsigned long long)ad_native_steps);
    fprintf(file,",\"ad_errors\":%llu",(unsigned long long)ad_errors);
    fprintf(file,",\"ad_child_entries\":%llu",(unsigned long long)ad_child_entries);
    fprintf(file,",\"ad_child_returns\":%llu",(unsigned long long)ad_child_returns);
    fprintf(file,",\"ad_actor\":%llu",(unsigned long long)ad_actor);
    fprintf(file,",\"ad_sprite\":%llu",(unsigned long long)ad_sprite);
    fprintf(file,",\"ad_full\":%llu",(unsigned long long)ad_full);
    fprintf(file,",\"ad_stack_observations\":%llu",(unsigned long long)ad_stack_observations);
    fprintf(file,",\"ad_stack_outside\":%llu",(unsigned long long)ad_stack_outside);
    fprintf(file,",\"ad_pending\":%llu",(unsigned long long)ad_pending);
    fprintf(file,",\"ad_min_headroom\":%llu",(unsigned long long)ad_min_headroom);
    fprintf(file,",\"ad_max_depth\":%llu",(unsigned long long)ad_max_depth);
    fprintf(file,",\"ad_max_child_depth\":%llu",(unsigned long long)ad_max_child_depth);
    fprintf(file,",\"ad_min_context_clearance\":%llu",(unsigned long long)ad_min_context_clearance);
    fprintf(file,",\"ad_context_collisions\":%llu",(unsigned long long)ad_context_collisions);
    fprintf(file,",\"ad_context_checks\":%llu",(unsigned long long)ad_context_checks);
    fprintf(file,",\"ad_child_below_context\":%llu",(unsigned long long)ad_child_below_context);
    fprintf(file,",\"ad_context_SP_inside\":%llu",(unsigned long long)ad_context_SP_inside);
    fprintf(file,",\"ai_entries\":%llu",(unsigned long long)ai_entries);
    fprintf(file,",\"ai_native_entries\":%llu",(unsigned long long)ai_native_entries);
    fprintf(file,",\"ai_returns\":%llu",(unsigned long long)ai_returns);
    fprintf(file,",\"ai_old_steps\":%llu",(unsigned long long)ai_old_steps);
    fprintf(file,",\"ai_native_steps\":%llu",(unsigned long long)ai_native_steps);
    fprintf(file,",\"ai_errors\":%llu",(unsigned long long)ai_errors);
    fprintf(file,",\"ai_pending\":%llu",(unsigned long long)ai_pending);
    fprintf(file,",\"ai_helper_entries\":%llu",(unsigned long long)ai_helper_entries);
    fprintf(file,",\"ai_helper_returns\":%llu",(unsigned long long)ai_helper_returns);
    fprintf(file,",\"ai_context_checks\":%llu",(unsigned long long)ai_context_checks);
    fprintf(file,",\"ai_context_corruptions\":%llu",(unsigned long long)ai_context_corruptions);
    fprintf(file,",\"ai_stack_observations\":%llu",(unsigned long long)ai_stack_observations);
    fprintf(file,",\"ai_stack_outside\":%llu",(unsigned long long)ai_stack_outside);
    fprintf(file,",\"ai_max_depth\":%llu",(unsigned long long)ai_max_depth);
    fprintf(file,",\"ai_min_headroom\":%llu",(unsigned long long)ai_min_headroom);
    fprintf(file,",\"sc_entries\":%llu",(unsigned long long)sc_entries);
    fprintf(file,",\"sc_native_entries\":%llu",(unsigned long long)sc_native_entries);
    fprintf(file,",\"sc_returns\":%llu",(unsigned long long)sc_returns);
    fprintf(file,",\"sc_old_steps\":%llu",(unsigned long long)sc_old_steps);
    fprintf(file,",\"sc_native_steps\":%llu",(unsigned long long)sc_native_steps);
    fprintf(file,",\"sc_errors\":%llu",(unsigned long long)sc_errors);
    fprintf(file,",\"sc_pending\":%llu",(unsigned long long)sc_pending);
    fprintf(file,",\"sc_helper_entries\":%llu",(unsigned long long)sc_helper_entries);
    fprintf(file,",\"sc_helper_returns\":%llu",(unsigned long long)sc_helper_returns);
    fprintf(file,",\"sc_context_checks\":%llu",(unsigned long long)sc_context_checks);
    fprintf(file,",\"sc_context_corruptions\":%llu",(unsigned long long)sc_context_corruptions);
    fprintf(file,",\"sc_stack_observations\":%llu",(unsigned long long)sc_stack_observations);
    fprintf(file,",\"sc_stack_outside\":%llu",(unsigned long long)sc_stack_outside);
    fprintf(file,",\"sc_max_depth\":%llu",(unsigned long long)sc_max_depth);
    fprintf(file,",\"sc_min_headroom\":%llu",(unsigned long long)sc_min_headroom);
    fprintf(file,",\"sc_position_calls\":%llu",(unsigned long long)sc_position_calls);
    fprintf(file,",\"sc_allocate_calls\":%llu",(unsigned long long)sc_allocate_calls);
    fprintf(file,",\"sc_decode_calls\":%llu",(unsigned long long)sc_decode_calls);

    ach_dump(file);an_dump(file);dir_dump(file);mb_dump(file);arena_dump(file);

    select_debug_dump(file);scan_debug_dump(file);door_debug_dump(file);interior_debug_dump(file);
    array(file,"rng_entries",rng_entries,8);array(file,"math_entries",math_entries,3);
    array(file,"boundary_entries",boundary_entries,4);fputs("}\n",file);
    return fclose(file)!=0;
}

static int face_retained_quiescent(void){return retained_observer_quiescent()&&!shared_pending_total();}

int shared_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"errors\":%llu,\"pending\":%u,\"C_stack_outside\":%llu",(unsigned long long)shared_errors,shared_pending_total(),(unsigned long long)shared_C_outside);
 const uint64_t *arrays[]={shared_public,shared_entries,shared_returns,shared_original,shared_fallbacks,shared_calls,shared_helper_returns,shared_C_observations};
 const char *keys[]={"public_entries","native_entries","native_returns","original_body_steps","fallback_entries","helper_entries","helper_returns","C_stack_observations"};
 for(unsigned j=0;j<8;j++){fprintf(f,",\"%s\":[",keys[j]);for(unsigned k=0;k<5;k++)fprintf(f,"%s%llu",k?",":"",(unsigned long long)arrays[j][k]);fputc(']',f);}
 fprintf(f,",\"C_stack_low_offsets\":[%u,%u,%u,%u,%u]}\n",shared_min[0],shared_min[1],shared_min[2],shared_min[3],shared_min[4]);return fclose(f)!=0;
}

static unsigned face_pending[101];
static struct cpu face_incoming[101];
static uint32_t face_return_word[101];
static uint8_t face_parent_frame[101][118],face_parent_stack[101][176];
static unsigned face_parent_active[101];
static uint64_t face_entries,face_returns,face_body_steps,face_helpers,face_errors,face_positive_speed,face_native_parent_returns,face_original_parent_returns,face_parent_checks;
static unsigned face_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=face_pending[i];return n;}
static void face_watch(uint32_t pc){
 if(!((pc>=0x1186au&&pc<0x11ad4u)||pc==1498708u||pc==0x10c6eu||pc==0x10cb6u))return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==0x1186au)face_errors++;return;}
 unsigned slot=delta/1024u;uint32_t base=1544384u+delta;struct cpu cpu;
 if(pc==0x1186au){
  face_entries++;if(face_pending[slot]){face_errors++;return;}
  face_pending[slot]=1;read_cpu(&cpu);face_incoming[slot]=cpu;face_return_word[slot]=rd32(cpu.r[15]);
  if((int32_t)rd32(0x40104u)>0)face_positive_speed++;
  face_parent_active[slot]=rd32(base+272u+114u)!=0;
  if(face_parent_active[slot]){memcpy(face_parent_frame[slot],ram+base+272u,118);memcpy(face_parent_stack[slot],ram+base+416u,176);}
 }
 if(!face_pending[slot])return;
 if(pc>=0x1186au&&pc<0x11ad4u)face_body_steps++;
 if(pc==0x10c6eu||pc==0x10cb6u)face_helpers++;
 if(pc==0x11ad2u||pc==1498708u){
  face_returns++;read_cpu(&cpu);face_pending[slot]=0;
  if(cpu.r[15]!=face_incoming[slot].r[15]||rd32(cpu.r[15])!=face_return_word[slot])face_errors++;
  for(unsigned i=0;i<15;i++)if((i==2u||i==3u||i==4u||i>=10u)&&cpu.r[i]!=face_incoming[slot].r[i])face_errors++;
  if(face_return_word[slot]==1500364u)face_native_parent_returns++;
  else if(face_return_word[slot]==0x11856u)face_original_parent_returns++;
  else face_errors++;
  if(face_parent_active[slot]){face_parent_checks++;if(memcmp(face_parent_frame[slot],ram+base+272u,118)||memcmp(face_parent_stack[slot],ram+base+416u,176))face_errors++;}
 }
}
static int32_t g4_retained_observe(uint32_t pc){face_watch(pc);return face_retained_observe(pc);}
static int g4_retained_quiescent(void){return face_retained_quiescent()&&!face_pending_total();}
int face_dump(const char *path){
 FILE *file=fopen(path,"w");if(!file)return 1;
 fprintf(file,"{\"entries\":%llu,\"returns\":%llu,\"body_steps\":%llu,\"helpers\":%llu,\"errors\":%llu,\"pending\":%u,\"positive_speed_entries\":%llu,\"native_parent_returns\":%llu,\"original_parent_returns\":%llu,\"suspended_native_parent_checks\":%llu}\n",(unsigned long long)face_entries,(unsigned long long)face_returns,(unsigned long long)face_body_steps,(unsigned long long)face_helpers,(unsigned long long)face_errors,face_pending_total(),(unsigned long long)face_positive_speed,(unsigned long long)face_native_parent_returns,(unsigned long long)face_original_parent_returns,(unsigned long long)face_parent_checks);
 return fclose(file)!=0;
}

/* Read-only geometry witness. Compiled helper completion is the actual
 * service_geometry C return, before deck_call consumes its logical RTS.
 * Original helpers use their actual logical RTS boundary. */
/* Read-only geometry witness. Compiled helper completion is the actual
 * service_geometry C return, before deck_call consumes its logical RTS.
 * Original helpers use their actual logical RTS boundary. */
static unsigned g6_pending[101],g6_calls[101],g6_active[101];
static uint32_t g6_sp[101];
static uint64_t g6_native_calls,g6_native_returns,g6_original_calls,g6_original_returns,g6_original_body_steps,g6_active_entries,g6_inactive_entries;
static const uint32_t g6_targets[2]={0x1b45au,0x149aeu};
static const uint32_t g6_returns[16]={0x107aau,0x107d2u,0x107e6u,0x10808u,0x1081cu,0x1083eu,0x10852u,0x10874u,0x10888u,0x108aau,0x108beu,0x108e0u,0x108f6u,0x10918u,0x10938u,0x1095au};
static unsigned g5_gpu_pending[101];
static uint32_t g5_gpu_sp[101];
static uint64_t g5_native_gpu_entries,g5_native_gpu_returns,g5_original_gpu_entries,g5_original_gpu_returns,g5_original_faces_steps;
static unsigned g4_pending[101],g4_helper_pending[101],g4_native[101],g4_marker_seen[101],g4_order[101];
static struct cpu g4_incoming[101];
static uint32_t g4_return_word[101],g4_service_sp[101],g4_service_ret[101];
static uint64_t g4_entries,g4_returns,g4_body_steps,g4_errors,g4_parent_returns;
static uint64_t g4_helpers[5],g4_helper_returns[5],g4_compiled[5],g4_markers[5],g4_transform_entries,g4_transform_returns;
static unsigned g4_transform_pending[101];
static uint32_t g4_plane_sp[101],g4_plane_ret[101],g4_plane_guest_sp[101];
static uint64_t g4_original_plane_entries,g4_original_plane_returns,g4_original_plane_steps;
static const uint32_t g4_targets[5]={0x10968u,0x11384u,0x10ba4u,0x1142eu,0x10734u};
static const uint32_t g4_logical_returns[5]={0x11ae6u,0x11b32u,0x11b38u,0x11b3eu,0x11b44u};
static unsigned g4_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=g4_pending[i]+g4_helper_pending[i]+g4_transform_pending[i]+g5_gpu_pending[i]+g6_pending[i];return n;}
static void g4_watch(uint32_t pc){
 unsigned relevant=(pc>=0x11ad4u&&pc<0x11b4cu)||pc==1498928u||pc==1499116u||pc==1500426u||pc==1535378u||pc==1532934u||pc==1507606u||pc==1532944u||pc==1533366u||pc==0x1b45au||pc==0x149aeu||(pc>=0x10734u&&pc<0x10968u)||pc==0xe26cu||pc==0x11684u||(pc>=0x1142eu&&pc<0x11762u)||pc==0x113feu||(pc>=0x110d4u&&pc<0x11384u);
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h])relevant=1;
 for(unsigned j=0;j<16;j++)if(pc==g6_returns[j])relevant=1;
 for(unsigned i=0;i<101;i++)if((g4_native[i]&&g4_helper_pending[i]&&pc==g4_service_ret[i])||(g4_transform_pending[i]==1u&&pc==g4_plane_ret[i]))relevant=1;
 if(!relevant)return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==0x11ad4u||pc==1498928u)g4_errors++;return;}
 unsigned slot=delta/1024u;struct cpu cpu;read_cpu(&cpu);uint32_t f=1544384u+delta+16u;
 if(pc==0x11ad4u){
  g4_entries++;if(g4_pending[slot]){g4_errors++;return;}
  g4_pending[slot]=1;g4_incoming[slot]=cpu;g4_return_word[slot]=rd32(cpu.r[15]);g4_order[slot]=0;
 }
 if(!g4_pending[slot])return;
 if(pc==1498928u)g4_native[slot]=1;
 if(pc>0x11ad4u&&pc<0x11b4cu)g4_body_steps++;
 uint32_t helper_sp=g4_incoming[slot].r[15]-16u;
 if(pc==1535378u){
  unsigned target=rd32(cpu.r[15]+16u),h=target==0x10968u?0u:target==0x11384u?1u:target==0x10ba4u?2u:5u;
  if(h<3){
   if(!g4_native[slot]||g4_helper_pending[slot]||g4_order[slot]!=h||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(f+114u)!=1u)g4_errors++;
   if(cpu.r[15]<1544384u+delta+832u||cpu.r[15]+20u>1544384u+delta+1008u||rd32(cpu.r[15])<1498112u||rd32(cpu.r[15])>=1538174u)g4_errors++;
   if(rd32(f+68u)!=target||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[h]||rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
   g4_service_sp[slot]=cpu.r[15];g4_service_ret[slot]=rd32(cpu.r[15]);g4_helper_pending[slot]=h+1u;g4_marker_seen[slot]=0;g4_helpers[h]++;g4_compiled[h]++;
  }
 }
 if(pc==1532944u){
  unsigned h=3u;
  if(!g4_native[slot]||g4_helper_pending[slot]||g4_order[slot]!=h||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(cpu.r[15]+16u)!=0x1142eu||rd32(f+114u)!=1u)g4_errors++;
  if(cpu.r[15]<1544384u+delta+832u||cpu.r[15]+20u>1544384u+delta+1008u||rd32(cpu.r[15])<1498112u||rd32(cpu.r[15])>=1538174u)g4_errors++;
  if(rd32(f+68u)!=0x1142eu||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[h]||rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
  g4_service_sp[slot]=cpu.r[15];g4_service_ret[slot]=rd32(cpu.r[15]);g4_helper_pending[slot]=4u;g4_marker_seen[slot]=1u;g4_helpers[h]++;g4_compiled[h]++;g4_markers[h]++;
 }
 if(pc==1533366u){
  unsigned h=4u;
  if(!g4_native[slot]||g4_helper_pending[slot]||g4_order[slot]!=h||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(cpu.r[15]+16u)!=0x10734u||rd32(f+114u)!=1u)g4_errors++;
  if(cpu.r[15]<1544384u+delta+832u||cpu.r[15]+20u>1544384u+delta+1008u||rd32(cpu.r[15])<1498112u||rd32(cpu.r[15])>=1538174u)g4_errors++;
  if(rd32(f+68u)!=0x10734u||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[h]||rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
  if(rd32(f+90u)!=2u||rd32(f+82u)!=1535378u||rd32(f+86u)!=f||g6_pending[slot])g4_errors++;
  g4_service_sp[slot]=cpu.r[15];g4_service_ret[slot]=rd32(cpu.r[15]);g4_helper_pending[slot]=5u;g4_marker_seen[slot]=1u;g4_helpers[h]++;g4_compiled[h]++;g4_markers[h]++;
  g6_calls[slot]=0;g6_active[slot]=rd16(0x403ccu)!=0u;if(g6_active[slot])g6_active_entries++;else g6_inactive_entries++;
 }
 if(g4_helper_pending[slot]==5u){
  if(!g4_native[slot]&&pc>=0x10734u&&pc<0x10968u)g6_original_body_steps++;
  if(pc==0x1b45au||pc==0x149aeu){
   unsigned j=g6_calls[slot];uint32_t sp=cpu.r[15],want=helper_sp-((j&1u)?108u:84u);
   if(j>=16u||!g6_active[slot]||g6_pending[slot]||sp!=want||pc!=g6_targets[j&1u])g4_errors++;
   if(g4_native[slot]){
    uint32_t csp=rd32(f+98u);
    if(j>=16u||rd32(f+90u)!=15u-j||rd32(f+82u)!=1508920u||rd32(f+86u)!=f||rd32(f+114u)!=1u)g4_errors++;
    if(rd32(sp)!=1500426u||rd32(f+106u)!=sp||j>=16u||rd32(f+110u)!=g6_returns[j%16u]||rd32(f+64u)!=sp||rd32(f+68u)!=pc||rd32(f+102u)!=f+4u)g4_errors++;
    if(csp<1544384u+delta+832u||csp+44u>1544384u+delta+1008u)g4_errors++;
    g6_pending[slot]=1u;g6_native_calls++;
   }else{
    if(j>=16u||rd32(sp)!=g6_returns[j%16u])g4_errors++;
    g6_pending[slot]=2u;g6_original_calls++;
   }
   g6_sp[slot]=sp;
  }
  if(g6_pending[slot]&&((g6_pending[slot]==1u&&pc==1500426u)||(g6_pending[slot]==2u&&pc==g6_returns[g6_calls[slot]%16u]))){
   if(cpu.r[15]!=g6_sp[slot]+4u)g4_errors++;
   if(g6_pending[slot]==1u)g6_native_returns++;else g6_original_returns++;
   g6_calls[slot]++;g6_pending[slot]=0;
  }
 }
 if(g4_helper_pending[slot]==4u&&!g4_native[slot]&&pc>=0x1142eu&&pc<0x11762u)g5_original_faces_steps++;
 if(pc==0xe26cu&&g4_helper_pending[slot]==4u){
  uint32_t sp=cpu.r[15],expected=helper_sp-58u;
  if(g5_gpu_pending[slot]||sp!=expected||rd16(sp+20u)!=0u)g4_errors++;
  if(g4_native[slot]){
   uint32_t csp=rd32(f+98u);
   if(rd32(sp)!=1500426u||rd32(f+106u)!=sp||rd32(f+110u)!=0x11684u||rd32(f+64u)!=sp||rd32(f+68u)!=0xe26cu||rd32(f+102u)!=f+4u||rd32(f+114u)!=1u)g4_errors++;
   if(csp<1544384u+delta+832u||csp+44u>1544384u+delta+1008u)g4_errors++;
   g5_gpu_pending[slot]=1u;g5_native_gpu_entries++;
  }else{
   if(rd32(sp)!=0x11684u)g4_errors++;
   g5_gpu_pending[slot]=2u;g5_original_gpu_entries++;
  }
  g5_gpu_sp[slot]=sp;
 }
 if(g5_gpu_pending[slot]&&((g5_gpu_pending[slot]==1u&&pc==1500426u)||(g5_gpu_pending[slot]==2u&&pc==0x11684u))){
  if(cpu.r[15]!=g5_gpu_sp[slot]+4u)g4_errors++;
  if(g5_gpu_pending[slot]==1u)g5_native_gpu_returns++;else g5_original_gpu_returns++;
  g5_gpu_pending[slot]=0;
 }
 if(pc==1532934u){
  uint32_t target=rd32(cpu.r[15]+8u);unsigned tag=g4_helper_pending[slot];
  if(!tag||tag>3u||rd32(cpu.r[15]+4u)!=f||g4_targets[tag-1u]!=target||g4_marker_seen[slot])g4_errors++;
  else {g4_marker_seen[slot]=1;g4_markers[tag-1u]++;}
 }
 if(pc==1507606u){
  if(!g4_native[slot]||g4_helper_pending[slot]!=2u||g4_transform_pending[slot]||rd32(cpu.r[15]+4u)!=f||rd32(cpu.r[15]+12u)!=f+4u||rd32(cpu.r[15]+16u)!=0x110d4u)g4_errors++;
  if(cpu.r[15]<1544384u+delta+832u||cpu.r[15]+20u>1544384u+delta+1008u||rd32(cpu.r[15])<1498112u||rd32(cpu.r[15])>=1538174u)g4_errors++;
  if(rd32(f+68u)!=0x110d4u||rd32(f+64u)!=helper_sp-18u||rd32(helper_sp-18u)!=0x113feu||rd32(f+114u)!=1u)g4_errors++;
  g4_transform_pending[slot]=1;g4_transform_entries++;g4_plane_sp[slot]=cpu.r[15];g4_plane_ret[slot]=rd32(cpu.r[15]);g4_plane_guest_sp[slot]=rd32(f+64u);
 }
 if(g4_transform_pending[slot]==1u&&pc==g4_plane_ret[slot]){
  uint32_t logical=rd32(f+68u);
  if(cpu.r[15]!=g4_plane_sp[slot]+4u||rd32(f+64u)!=g4_plane_guest_sp[slot]||rd32(g4_plane_guest_sp[slot])!=0x113feu||rd32(f+94u)||(logical!=0x11178u&&logical!=0x111e2u&&logical!=0x1124cu&&logical!=0x11382u))g4_errors++;
  g4_transform_returns++;g4_transform_pending[slot]=0;
 }
 if(pc==0x110d4u&&g4_helper_pending[slot]==2u){
  if(g4_native[slot]||g4_transform_pending[slot]||cpu.r[15]!=helper_sp-18u||rd32(cpu.r[15])!=0x113feu)g4_errors++;
  g4_transform_pending[slot]=2;g4_original_plane_entries++;
 }
 if(g4_transform_pending[slot]==2u&&pc>=0x110d4u&&pc<0x11384u)g4_original_plane_steps++;
 if(g4_transform_pending[slot]==2u&&pc==0x113feu){
  if(cpu.r[15]!=helper_sp-14u)g4_errors++;
  g4_original_plane_returns++;g4_transform_pending[slot]=0;
 }
 unsigned tag=g4_helper_pending[slot];
 if(g4_native[slot]&&tag&&tag<=5u&&pc==g4_service_ret[slot]){
  uint32_t logical=rd32(f+68u);
  if((tag==1u&&logical!=0x1098eu)||(tag==2u&&logical!=0x1142cu)||(tag==3u&&logical!=0x10bb2u&&logical!=0x10c16u)||(tag==4u&&logical!=0x11760u)||(tag==5u&&logical!=0x10966u))g4_errors++;
  if(cpu.r[15]!=g4_service_sp[slot]+4u||!g4_marker_seen[slot]||g4_transform_pending[slot]||g5_gpu_pending[slot]||rd32(f+94u)||rd32(f+64u)!=helper_sp||rd32(helper_sp)!=g4_logical_returns[tag-1u])g4_errors++;
  if(tag==5u&&(g6_pending[slot]||g6_calls[slot]!=(g6_active[slot]?16u:0u)||rd32(f+90u)!=2u||rd32(f+82u)!=1535378u||rd32(f+86u)!=f))g4_errors++;
  g4_helper_returns[tag-1u]++;g4_helper_pending[slot]=0;g4_order[slot]++;
 }
 for(unsigned h=0;h<5;h++)if(pc==g4_targets[h]&&cpu.r[15]==helper_sp){
  uint32_t ret=rd32(helper_sp);
  if(ret==1500426u||ret==g4_logical_returns[h]){
   if(g4_helper_pending[slot]||g4_order[slot]!=h||g4_native[slot])g4_errors++;
   g4_helper_pending[slot]=h+1u;g4_helpers[h]++;
   if(h==4u){g6_calls[slot]=0;g6_active[slot]=rd16(0x403ccu)!=0u;if(g6_active[slot])g6_active_entries++;else g6_inactive_entries++;}
   if(rd16(helper_sp+4u)!=1u||rd16(helper_sp+6u)!=7u)g4_errors++;
  }
 }
 tag=g4_helper_pending[slot];
 if(tag&&!g4_native[slot]&&(pc==1500426u||pc==g4_logical_returns[tag-1u])){
  if(tag==5u&&(g6_pending[slot]||g6_calls[slot]!=(g6_active[slot]?16u:0u)))g4_errors++;
  g4_helper_returns[tag-1u]++;g4_helper_pending[slot]=0;g4_order[slot]++;
  if(cpu.r[15]!=helper_sp+4u)g4_errors++;
 }
 if(pc==0x11b4au||pc==1499116u){
  g4_returns++;g4_pending[slot]=0;
  if(g4_helper_pending[slot]||g4_transform_pending[slot]||g5_gpu_pending[slot]||g4_order[slot]!=5u||cpu.r[15]!=g4_incoming[slot].r[15]||rd32(cpu.r[15])!=g4_return_word[slot])g4_errors++;
  if(cpu.r[2]!=g4_incoming[slot].r[2]||cpu.r[3]!=g4_incoming[slot].r[3])g4_errors++;
  if(g4_return_word[slot]==0x11ee4u||(g4_return_word[slot]==1539206u&&rd32(1647808u+slot*576u+122u)==g4_incoming[slot].r[15]&&rd32(1647808u+slot*576u+126u)==0x11ee4u))g4_parent_returns++;else g4_errors++;
  g4_native[slot]=0;
 }
}
static int32_t o6_retained_observe(uint32_t pc){g4_watch(pc);return g4_retained_observe(pc);}
static int o6_retained_quiescent(void){return g4_retained_quiescent()&&!g4_pending_total();}
int geometry_dump(const char *path){
 FILE *f=fopen(path,"w");if(!f)return 1;
 fprintf(f,"{\"entries\":%llu,\"returns\":%llu,\"original_body_steps\":%llu,\"errors\":%llu,\"pending\":%u,\"matched_outer_parent_returns\":%llu,\"transform_entries\":%llu,\"transform_returns\":%llu",(unsigned long long)g4_entries,(unsigned long long)g4_returns,(unsigned long long)g4_body_steps,(unsigned long long)g4_errors,g4_pending_total(),(unsigned long long)g4_parent_returns,(unsigned long long)g4_transform_entries,(unsigned long long)g4_transform_returns);
 fprintf(f,",\"original_transform_entries\":%llu,\"original_transform_returns\":%llu,\"original_transform_steps\":%llu",(unsigned long long)g4_original_plane_entries,(unsigned long long)g4_original_plane_returns,(unsigned long long)g4_original_plane_steps);
 fprintf(f,",\"native_GPU_entries\":%llu,\"native_GPU_returns\":%llu,\"original_GPU_entries\":%llu,\"original_GPU_returns\":%llu,\"original_faces_body_steps\":%llu",(unsigned long long)g5_native_gpu_entries,(unsigned long long)g5_native_gpu_returns,(unsigned long long)g5_original_gpu_entries,(unsigned long long)g5_original_gpu_returns,(unsigned long long)g5_original_faces_steps);
 fprintf(f,",\"native_debug_dependency_entries\":%llu,\"native_debug_dependency_returns\":%llu,\"original_debug_dependency_entries\":%llu,\"original_debug_dependency_returns\":%llu,\"original_debug_body_steps\":%llu,\"debug_active_entries\":%llu,\"debug_inactive_entries\":%llu",(unsigned long long)g6_native_calls,(unsigned long long)g6_native_returns,(unsigned long long)g6_original_calls,(unsigned long long)g6_original_returns,(unsigned long long)g6_original_body_steps,(unsigned long long)g6_active_entries,(unsigned long long)g6_inactive_entries);
 const uint64_t *arrays[]={g4_helpers,g4_helper_returns,g4_compiled,g4_markers};const char *keys[]={"helper_entries","helper_returns","compiled_helper_services","compiled_helper_markers"};
 for(unsigned j=0;j<4;j++){fprintf(f,",\"%s\":[",keys[j]);for(unsigned h=0;h<5;h++)fprintf(f,"%s%llu",h?",":"",(unsigned long long)arrays[j][h]);fputc(']',f);}
 fputs("}\n",f);return fclose(f)!=0;
}

static const uint32_t o6_inner_returns[5]={1498300u,1498504u,1498708u,1498912u,1499116u};
/* O6_WATCHER_BEGIN: independently extracted by the fixture qualifier. */
static unsigned o6_mode[101],o6_helper_pending[101];
static struct cpu o6_incoming[101];
static uint32_t o6_entry_word[101],o6_call_sp[101],o6_logical_return[101];
static uint8_t o6_shadow[101][576];
static uint64_t o6_public,o6_native_entries,o6_native_returns,o6_original_returns,o6_original_steps,o6_fallbacks,o6_iterations,o6_original_iterations,o6_wait_slices,o6_errors,o6_C_outside,o6_C_observations,o6_protected_checks,o6_scheduler_boundaries;
static uint32_t o6_min=560u,o6_min_heap=0xffffffffu;
static uint64_t o6_helper_entries[13],o6_helper_returns[13];
static const uint32_t o6_targets[13]={0x10990u,0x11828u,0xe03au,0x10c6eu,0x1102au,0x11ad4u,0x16bf4u,0x10e72u,0x11d1au,0xe19eu,0xe202u,0xe098u,0x17f14u};
static const uint32_t o6_rets[13]={0x11e86u,0x11e8cu,0x11ec4u,0x11ed6u,0x11edcu,0x11ee4u,0x11f12u,0x11f32u,0x11f38u,0x11f4au,0x11f50u,0x11f5eu,0x11f64u};
static unsigned o6_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=o6_mode[i]!=0;return n;}
static unsigned o6_helper_pending_total(void){unsigned n=0;for(unsigned i=0;i<101;i++)n+=o6_helper_pending[i]!=0;return n;}
static void o6_check_commit(unsigned slot,uint32_t pc,const struct cpu *cpu){
 uint32_t f=1647808u+slot*576u+16u;
 for(unsigned i=0;i<16;i++)if(cpu->r[i]!=rd32(f+4u+4u*i))o6_errors++;
 if(cpu->sr!=rd16(f+80u))o6_errors++;
 if(pc==1538500u){if(rd32(f+114u)||rd32(f+94u)||rd32(f+68u)!=0x11f6au)o6_errors++;}
 else if(rd32(f+114u)!=1u||rd32(f+94u)!=6u||rd32(f+68u)!=(pc==1538478u?0x11e86u:0x11f50u))o6_errors++;
}
static void o6_watch(uint32_t pc){
 unsigned relevant=(pc>=0x11e6cu&&pc<0x11f6cu)||(pc>=1538176u&&pc<1543974u)||pc==0xdf60u||pc==0xdf8cu;
 for(unsigned i=0;i<13;i++)if(pc==o6_targets[i])relevant=1;
 for(unsigned i=0;i<5;i++)if(pc==o6_inner_returns[i])relevant=1;
 if(!relevant)return;
 uint32_t task=rd32(0xc0920u),delta=task-0xc0928u;
 if(delta>=0x19400u||(delta&1023u)){if(pc==0x11e6cu||pc==1538176u)o6_errors++;return;}
 unsigned slot=delta/1024u;struct cpu cpu;read_cpu(&cpu);uint32_t base=1647808u+slot*576u,f=base+16u;
 if(pc==0x11e6cu){
  o6_public++;if(o6_mode[slot]){o6_errors++;return;}
  o6_mode[slot]=2;o6_incoming[slot]=cpu;o6_entry_word[slot]=rd32(cpu.r[15]);
 }
 if(pc==1538176u){o6_native_entries++;o6_used[slot]=1;if(o6_mode[slot]!=2u)o6_errors++;o6_mode[slot]=1;}
 if(!o6_mode[slot])return;
 uint32_t heap=rd32(0x112d64u);if(heap<o6_min_heap)o6_min_heap=heap;
 if(pc==1538344u)o6_fallbacks++;
 if(pc>0x11e6cu&&pc<0x11f6cu)o6_original_steps++;
 if(pc==0xdf60u||pc==0xdf8cu)o6_scheduler_boundaries++;
 if(pc==0x11e86u&&o6_mode[slot]==2u)o6_original_iterations++;
 if(pc==1538478u||pc==1538460u){
  if(o6_mode[slot]!=1u)o6_errors++;
  if(pc==1538478u)o6_iterations++;else o6_wait_slices++;
  o6_check_commit(slot,pc,&cpu);
 }
 if(o6_mode[slot]==1u && ((pc>=1539270u&&pc<1543974u)||(pc>=1538504u&&pc<1539206u)) && cpu.r[15]>=base&&cpu.r[15]<base+576u){
  o6_C_observations++;uint32_t off=cpu.r[15]-base;if(off<o6_min)o6_min=off;if(off<144u||off>560u)o6_C_outside++;
 }
 for(unsigned h=0;h<13;h++)if(pc==o6_targets[h]){
  uint32_t ret=rd32(cpu.r[15]);unsigned direct=0;
  if(o6_mode[slot]==1u){
   if(ret==1539206u&&rd32(f+106u)==cpu.r[15]){
    uint32_t csp=rd32(f+98u),cp=rd32(f+102u),logical=rd32(f+110u);
    if(csp<base+144u||csp+60u>base+560u||cp<base+144u||cp+78u>base+560u)o6_errors++;
    else if(rd32(cp+64u)!=pc)o6_errors++;
    if(logical!=o6_rets[h]&&!(h==3u&&logical==0x11f1au))o6_errors++;
    direct=1;o6_logical_return[slot]=logical;memcpy(o6_shadow[slot],ram+base,576);
   }
  }else if(ret==o6_rets[h]||(h==3u&&ret==0x11f1au)){direct=1;o6_logical_return[slot]=ret;}
  if(direct){if(o6_helper_pending[slot])o6_errors++;o6_helper_pending[slot]=h+1u;o6_call_sp[slot]=cpu.r[15];o6_helper_entries[h]++;}
 }
 unsigned tag=o6_helper_pending[slot];
 if(tag && ((o6_mode[slot]==1u&&pc==1539206u)||(o6_mode[slot]==2u&&pc==o6_logical_return[slot]))){
  if(cpu.r[15]!=o6_call_sp[slot]+4u)o6_errors++;
  if(o6_mode[slot]==1u){if(memcmp(o6_shadow[slot],ram+base,576))o6_errors++;o6_protected_checks++;}
  o6_helper_returns[tag-1u]++;o6_helper_pending[slot]=0;
 }
 if(o6_mode[slot]==1u&&o6_helper_pending[slot])for(unsigned i=0;i<5;i++)if(pc==o6_inner_returns[i]){
  if(memcmp(o6_shadow[slot],ram+base,576))o6_errors++;o6_protected_checks++;
 }
 if(pc==1538500u||pc==0x11f6au){
  if(o6_helper_pending[slot]||cpu.r[15]!=o6_incoming[slot].r[15]||cpu.r[14]!=o6_incoming[slot].r[14]||rd32(cpu.r[15])!=o6_entry_word[slot])o6_errors++;
  if(pc==1538500u){o6_native_returns++;o6_check_commit(slot,pc,&cpu);}else o6_original_returns++;
  o6_mode[slot]=0;
 }
}
/* O6_WATCHER_END */

/* Host-only trace storage. Guest RAM/CPU and existing observers are read-only. */
struct timing_row { uint32_t frame,ordinal,pc,previous,reason,movie0,movie1,held,task,sp; };
static struct timing_row timing_rows[65536];
static uint32_t timing_count,timing_overflow,timing_frame,timing_ordinal,timing_previous;
static uint32_t timing_movie0,timing_movie1,timing_held;
static void timing_watch(uint32_t pc){
 if(frame<24565u||frame>24966u)return;
 uint32_t m0=rd16(0x47b80u),m1=rd16(0x47b82u),held=rd32(0x49ba4u);
 unsigned reason=0;
 if(timing_frame!=frame){timing_frame=frame;timing_ordinal=0;reason|=1u;}
 timing_ordinal++;
 if(m0!=timing_movie0||m1!=timing_movie1||held!=timing_held)reason|=2u;
 if(pc==0x11ad4u||pc==0x11b4au||pc==1498928u||pc==1499116u||pc==0xdf60u||pc==0xdf8cu)reason|=4u;
 if(reason){
  if(timing_count==65536u)timing_overflow++;
  else {struct cpu current;read_cpu(&current);
   timing_rows[timing_count++]=(struct timing_row){frame,timing_ordinal,pc,timing_previous,reason,m0,m1,held,rd32(0xc0920u),current.r[15]};}
 }
 timing_previous=pc;timing_movie0=m0;timing_movie1=m1;timing_held=held;
}
int timeline_dump(const char *path){
 FILE *file=fopen(path,"w");if(!file)return 1;
 fprintf(file,"{\"overflow\":%u,\"rows\":[",timing_overflow);
 for(unsigned i=0;i<timing_count;i++){
  struct timing_row *r=&timing_rows[i];
  fprintf(file,"%s[%u,%u,%u,%u,%u,%u,%u,%u,%u,%u]",i?",":"",r->frame,r->ordinal,r->pc,r->previous,r->reason,r->movie0,r->movie1,r->held,r->task,r->sp);
 }
 return fputs("]}\n",file)<0||fclose(file);
}

int32_t observe(uint32_t pc){timing_watch(pc);o6_watch(pc);return o6_retained_observe(pc);}
int observer_quiescent(void){return o6_retained_quiescent()&&!o6_pending_total()&&!o6_helper_pending_total();}
int outer_dump(const char *path){
 FILE *file=fopen(path,"w");if(!file)return 1;
 fprintf(file,"{\"public_entries\":%llu,\"native_entries\":%llu,\"native_returns\":%llu,\"original_returns\":%llu,\"original_body_steps\":%llu,\"fallbacks\":%llu,\"native_iteration_boundaries\":%llu,\"original_iteration_boundaries\":%llu,\"native_wait_slices\":%llu,\"errors\":%llu,\"pending\":%u,\"helper_pending\":%u,\"C_stack_outside\":%llu,\"C_stack_observations\":%llu,\"C_stack_low_offset\":%u,\"protected_frame_checks\":%llu,\"scheduler_boundaries_reached\":%llu,\"minimum_heap_free_while_outer_active\":%u",(unsigned long long)o6_public,(unsigned long long)o6_native_entries,(unsigned long long)o6_native_returns,(unsigned long long)o6_original_returns,(unsigned long long)o6_original_steps,(unsigned long long)o6_fallbacks,(unsigned long long)o6_iterations,(unsigned long long)o6_original_iterations,(unsigned long long)o6_wait_slices,(unsigned long long)o6_errors,o6_pending_total(),o6_helper_pending_total(),(unsigned long long)o6_C_outside,(unsigned long long)o6_C_observations,o6_min,(unsigned long long)o6_protected_checks,(unsigned long long)o6_scheduler_boundaries,o6_min_heap);
 const uint64_t *arrays[]={o6_helper_entries,o6_helper_returns};const char *keys[]={"helper_entries","helper_returns"};
 for(unsigned j=0;j<2;j++){fprintf(file,",\"%s\":[",keys[j]);for(unsigned h=0;h<13;h++)fprintf(file,"%s%llu",h?",":"",(unsigned long long)arrays[j][h]);fputc(']',file);}
 fputs("}\n",file);return fclose(file)!=0;
}
