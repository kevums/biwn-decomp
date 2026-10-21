/* Read-only stable-entry dispatcher/real-child ABI oracle. The children run;
 * their captured actual outputs, not a second child algorithm, predict root
 * return. Does not predict concurrent changes to the entry pool/flags reads. */
#ifndef BIWN_ACTOR_DISPATCH_TASK
#define BIWN_ACTOR_DISPATCH_TASK() rd32(0xc0920u)
#endif
struct ad_call {uint32_t task,sp,ret,args[5],slot,min_sp;unsigned pending,actor,full,child,returned;struct cpu incoming,expected,output;};
static struct ad_call ad_calls[256];
static unsigned ad_slots,ad_pending;
static uint64_t ad_entries,ad_native_entries,ad_returns,ad_old_steps,ad_native_steps,ad_errors,ad_child_entries,ad_child_returns,ad_actor,ad_sprite,ad_full,ad_stack_observations,ad_stack_outside;
static uint32_t ad_max_depth,ad_min_headroom=0xffffffffu;
static uint32_t ad_sx(uint16_t x){return(uint32_t)(x&0x7fffu)-(uint32_t)(x&0x8000u);}
static void ad_compare(const struct cpu *a,const struct cpu *b){
    for(unsigned i=0;i<16;i++)if(a->r[i]!=b->r[i])ad_errors++;
    if(a->sr!=b->sr||a->usp!=b->usp||a->ssp!=b->ssp)ad_errors++;
}
static void ad_bank(struct cpu *c){if(c->sr&0x2000u)c->ssp=c->r[15];else c->usp=c->r[15];}
static void watch_actor_dispatch(uint32_t pc){
    if(pc==__AD_ENTRY__)ad_native_entries++;
    if(pc>0x13ae0u&&pc<0x13b5au)ad_old_steps++;
    if(pc>=__AD_START__&&pc<__AD_END__)ad_native_steps++;
    if(!ad_pending&&pc!=0x13ae0u)return;
    uint32_t task=BIWN_ACTOR_DISPATCH_TASK();struct ad_call *call=NULL;struct cpu current;
    for(unsigned i=0;i<ad_slots;i++)if(ad_calls[i].task==task){call=&ad_calls[i];break;}
    if(pc==0x13ae0u){
        if(!call){if(ad_slots==256){ad_errors++;return;}call=&ad_calls[ad_slots++];call->task=task;}
        if(call->pending)ad_errors++;
        read_cpu(&call->incoming);call->expected=call->incoming;call->sp=call->incoming.r[15];call->ret=rd32(call->sp);call->min_sp=call->sp;
        uint32_t s=call->sp;call->args[0]=rd16(s+4);call->args[1]=rd32(s+6);call->args[2]=rd16(s+10);call->args[3]=rd32(s+12);call->args[4]=rd16(s+16);
        call->pending=1;call->child=call->returned=call->full=0;ad_entries++;ad_pending++;
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
    read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];ad_stack_observations++;
        if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)ad_stack_outside++;
        else if(sp-task-38u<ad_min_headroom)ad_min_headroom=sp-task-38u;
        if(sp<call->min_sp)call->min_sp=sp;
    }
    if(pc==(call->actor?0x134dcu:0x137e0u)){
        ad_child_entries++;if(call->full||call->child)ad_errors++;call->child=1;
        ad_compare(&current,&call->expected);
        uint32_t s=current.r[15]+4u;
        if(rd16(s)!=call->args[0])ad_errors++;s+=2;
        if(call->actor){if(rd16(s)!=call->slot)ad_errors++;s+=2;}
        if(rd32(s)!=call->args[1]||rd16(s+4)!=call->args[2]||rd32(s+6)!=call->args[3]||rd16(s+10)!=call->args[4])ad_errors++;
    }
    if(pc==__AD_ACTOR_CHILD_RETURN__||pc==__AD_SPRITE_CHILD_RETURN__||pc==0x13b3au||pc==0x13b50u){
        if(call->full||!call->child||call->returned)ad_errors++;
        call->returned=1;call->output=current;ad_child_returns++;
        if(current.r[15]!=call->sp-16u-(call->actor?16u:14u))ad_errors++;
    }
    if(pc==__AD_RETURN__||pc==0x13b58u){
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
