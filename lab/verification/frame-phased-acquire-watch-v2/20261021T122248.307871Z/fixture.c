#include <stdint.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const uint8_t *ram;static struct cpu current;static unsigned arena_active[102];
static uint32_t rd32(uint32_t a){return ((uint32_t)ram[a]<<24)|((uint32_t)ram[a+1]<<16)|((uint32_t)ram[a+2]<<8)|ram[a+3];}
static void read_cpu(struct cpu *o){*o=current;}
static void emit(uint32_t pc){(void)pc;}
static unsigned task_id_valid(uint32_t task){return task>=0xc0928u&&task<0xd9d28u&&((task-0xc0928u)&0x3ffu)==0;}
static unsigned task_arena_slot(uint32_t task){return task_id_valid(task)?(task-0xc0928u)/1024u:101u;}
static uint32_t task_arena_top(uint32_t task){return 1471936u+task_arena_slot(task)*256u+240u;}
static unsigned task_original_stack_valid(uint32_t task,uint32_t sp){return task_id_valid(task)&&sp>=task+38u&&sp<=task+0x400u;}
static unsigned task_arena_stack_valid(uint32_t task,uint32_t sp){uint32_t top=task_arena_top(task);return arena_active[task_arena_slot(task)]&&sp>=top-224u&&sp<=top;}
static unsigned task_stack_valid(uint32_t task,uint32_t sp){return task_original_stack_valid(task,sp)||task_arena_stack_valid(task,sp);}static unsigned phased_frame_code(uint32_t pc){return (pc>=1451812u&&pc<1453348u)||(pc>=1569564u&&pc<1569804u);}
struct acquire_call {uint32_t task;unsigned pending;struct cpu incoming;uint32_t min_sp,return_word;};
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
    if(!acquire_pending&&pc!=0x1ac68&&!phased_frame_code(pc)&&!(pc>0x1ac68&&pc<0x1ae56))return;
    uint32_t task=rd32(0xc0920);struct acquire_call *slot=NULL;struct cpu current;
    if(pc==0x1ac68){
        slot=acquire_slot(task);if(!slot)return;
        if(slot->pending)acquire_monitor_errors++;
        read_cpu(&slot->incoming);slot->pending=1;slot->min_sp=slot->incoming.r[15];slot->return_word=rd32(slot->incoming.r[15]);acquire_entries++;acquire_pending++;emit(pc);
    }
    if(pc>0x1ac68&&pc<0x1ae56)acquire_old_steps++;
    if(pc==0x162724u)acquire_native_entries++;
    if(phased_frame_code(pc))acquire_native_steps++;
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
    if(pc==0x162860u||pc==0x1ae54){
        uint32_t s=slot->incoming.r[15];acquire_returns++;emit(pc);if(rd32(s)!=slot->return_word)acquire_monitor_errors++;
        const unsigned saved[]={2,3,4,5,6,7,10,11,12};
        for(unsigned i=0;i<9;i++)if(current.r[saved[i]]!=slot->incoming.r[saved[i]]||rd32(s-44u+4u*i)!=slot->incoming.r[saved[i]])acquire_monitor_errors++;
        if(current.r[14]!=slot->incoming.r[14]||current.r[15]!=s||rd32(s-4u)!=slot->incoming.r[14])acquire_monitor_errors++;
        uint32_t low=current.r[0]&0xffffu;uint16_t nz=(uint16_t)(low==0?4:(low&0x8000u)?8:0);
        if((current.sr&15u)!=nz||(current.sr&0xffe0u)!=(slot->incoming.sr&0xffe0u))acquire_monitor_errors++;
        if(s-slot->min_sp>acquire_max_private_depth)acquire_max_private_depth=s-slot->min_sp;
        slot->pending=0;acquire_pending--;
    }
}
void snapshot(const void *memory,const struct cpu *cpu){ram=memory;current=*cpu;}
void pc(uint32_t value){watch_acquire(value);}
void clear(void){memset(acquire_slots,0,sizeof(acquire_slots));memset(arena_active,0,sizeof(arena_active));acquire_entries=acquire_native_entries=acquire_returns=acquire_old_steps=acquire_monitor_errors=acquire_native_steps=acquire_loader_calls=acquire_user_stack_observations=acquire_user_stack_outside=0;acquire_pending=acquire_slot_count=acquire_max_private_depth=0;acquire_user_min_headroom=0xffffffffu;}
uint64_t stat(unsigned i){switch(i){case 0:return acquire_monitor_errors;case 1:return acquire_user_stack_outside;case 2:return acquire_pending;case 3:return acquire_entries;case 4:return acquire_native_entries;case 5:return acquire_returns;case 6:return acquire_loader_calls;default:return 0;}}
