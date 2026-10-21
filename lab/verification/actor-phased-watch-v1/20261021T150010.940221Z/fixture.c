#include <stdint.h>
#include <string.h>
struct cpu{uint32_t r[16],pc,usp,ssp;uint16_t sr;};
static const uint8_t *ram;static struct cpu current;static unsigned arena_active[102];
static uint32_t rd16(uint32_t a){return ((uint32_t)ram[a]<<8)|ram[a+1];}
static uint32_t rd32(uint32_t a){return(rd16(a)<<16)|rd16(a+2);}
static void read_cpu(struct cpu *o){*o=current;}
static void emit(uint32_t pc){(void)pc;}
#define BIWN_ACTOR_DISPATCH_TASK() rd32(0xc0920u)
#define BIWN_ACTOR_INITIALIZE_TASK() rd32(0xc0920u)
static unsigned task_id_valid(uint32_t task){return task>=0xc0928u&&task<0xd9d28u&&((task-0xc0928u)&0x3ffu)==0;}
static unsigned task_arena_slot(uint32_t task){return task_id_valid(task)?(task-0xc0928u)/1024u:101u;}
static uint32_t task_arena_top(uint32_t task){return 1471936u+task_arena_slot(task)*256u+240u;}
static unsigned task_original_stack_valid(uint32_t task,uint32_t sp){return task_id_valid(task)&&sp>=task+38u&&sp<=task+0x400u;}
static unsigned task_arena_stack_valid(uint32_t task,uint32_t sp){uint32_t top=task_arena_top(task);return arena_active[task_arena_slot(task)]&&sp>=top-224u&&sp<=top;}
static unsigned task_stack_valid(uint32_t task,uint32_t sp){return task_original_stack_valid(task,sp)||task_arena_stack_valid(task,sp);}struct ad_call {uint32_t task,sp,ret,args[5],slot,min_sp;unsigned pending,actor,full,child,returned,native;uint32_t context[18];struct cpu incoming,expected,output;};
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
            if(call->sp>=sp&&call->sp-sp>ad_max_child_depth)ad_max_child_depth=call->sp-sp;
        }
    }
    if(pc==(call->actor?0x134dcu:0x137e0u)){
        ad_child_entries++;if(call->full||call->child)ad_errors++;call->child=1;
        ad_compare(&current,&call->expected);
        if(call->native)for(unsigned i=0;i<4;i++){call->context[i]=rd32(call->sp-16u+4u*i);if(call->context[i]!=call->incoming.r[2u+i])ad_errors++;}
        uint32_t s=current.r[15]+4u;
        if(rd16(s)!=call->args[0])ad_errors++;s+=2;
        if(call->actor){if(rd16(s)!=call->slot)ad_errors++;s+=2;}
        if(rd32(s)!=call->args[1]||rd16(s+4)!=call->args[2]||rd32(s+6)!=call->args[3]||rd16(s+10)!=call->args[4])ad_errors++;
    }
    if(pc==1456426u||pc==1456460u||pc==0x13b3au||pc==0x13b50u){
        if(call->full||!call->child||call->returned)ad_errors++;
        if(call->native){ad_context_checks++;for(unsigned i=0;i<4;i++)if(rd32(call->sp-16u+4u*i)!=call->context[i])ad_context_collisions++;}
        call->returned=1;call->output=current;ad_child_returns++;
        if(current.r[15]!=call->sp-16u-(call->actor?16u:14u))ad_errors++;
    }
    if(pc==1456482u||pc==0x13b58u){
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
   const unsigned saved[]={2,3,4,5,6,7,10,11};
   for(unsigned i=0;i<8;i++){call->context[i]=rd32(call->sp-32u+4u*i);if(call->context[i]!=call->incoming.r[saved[i]])ai_errors++;}
  }
 }
 if((call->helper==0x102c4u&&(pc==1458012u||pc==0x135f0u))||(call->helper==0x10520u&&(pc==1458038u||pc==0x13602u))||(call->helper==0xdf6cu&&(pc==1458126u||pc==0x137c6u))){
  if(!call->helper_pending)ai_errors++;
  if(call->native){ai_context_checks++;for(unsigned i=0;i<8;i++)if(rd32(call->sp-32u+4u*i)!=call->context[i])ai_context_corruptions++;}
  uint32_t bytes=call->helper==0xdf6cu?8u:4u;
  if(current.r[15]!=call->sp-32u-bytes)ai_errors++;
  call->helper_pending=0;ai_helper_returns++;
 }
 if(pc==1458148u||pc==0x137deu){
  if(call->helper_pending)ai_errors++;
  const unsigned saved[]={2,3,4,5,6,7,10,11};for(unsigned i=0;i<8;i++)if(current.r[saved[i]]!=call->incoming.r[saved[i]])ai_errors++;
  uint32_t s=call->sp;
  if(current.r[15]!=s||rd32(s)!=call->ret||rd16(s+4)!=call->args[0]||rd16(s+6)!=call->args[1]||rd32(s+8)!=call->args[2]||rd16(s+12)!=call->args[3]||rd32(s+14)!=call->args[4]||rd16(s+18)!=call->args[5])ai_errors++;
  if(s-call->min_sp>ai_max_depth)ai_max_depth=s-call->min_sp;
  ai_pending--;call->pending=0;ai_returns++;emit(pc);
 }
}
void snapshot(const void *m,const struct cpu *cpu){ram=m;current=*cpu;}
void step(uint32_t pc){watch_actor_dispatch(pc);watch_actor_initialize(pc);}
void clear(void){
memset(ad_calls,0,sizeof(ad_calls));memset(ai_calls,0,sizeof(ai_calls));memset(arena_active,0,sizeof(arena_active));
ad_slots=ad_pending=ai_slots=ai_pending=0;
ad_entries=ad_native_entries=ad_returns=ad_old_steps=ad_native_steps=ad_errors=ad_child_entries=ad_child_returns=ad_actor=ad_sprite=ad_full=ad_stack_observations=ad_stack_outside=ad_context_collisions=ad_context_checks=ad_child_below_context=ad_context_SP_inside=0;
ad_max_depth=ad_max_child_depth=0;ad_min_context_clearance=ad_min_headroom=0xffffffffu;
ai_entries=ai_native_entries=ai_returns=ai_old_steps=ai_native_steps=ai_errors=ai_helper_entries=ai_helper_returns=ai_context_checks=ai_context_corruptions=ai_stack_observations=ai_stack_outside=0;
ai_max_depth=0;ai_min_headroom=0xffffffffu;
}
uint64_t stat(unsigned i){switch(i){
case 0:return ad_errors+ad_context_collisions+ai_errors+ai_context_corruptions;
case 1:return ad_stack_outside+ai_stack_outside;
case 2:return ad_pending+ai_pending;
case 3:return ad_entries;case 4:return ad_returns;
case 5:return ai_entries;case 6:return ai_returns;
case 7:return ad_context_checks;case 8:return ai_context_checks;
default:return 0;}}
