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
    if(!geometry_pending&&!(pc>=0x1028eu&&pc<0x102c4u)&&!(pc>=__GEOMETRY_START__&&pc<__GEOMETRY_END__))return;
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
    if(pc==__GEOMETRY_ENTRY__)geometry_native_entries++;
    if(pc>=__GEOMETRY_START__&&pc<__GEOMETRY_END__)geometry_native_steps++;
    if(!call){for(unsigned i=0;i<geometry_slots;i++)if(geometry_calls[i].task==task&&geometry_calls[i].pending){call=&geometry_calls[i];break;}}
    if(!call||!call->pending)return;
    struct cpu current;read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];geometry_user_observations++;
        if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)geometry_stack_outside++;
        else if(sp-task-38u<geometry_min_headroom)geometry_min_headroom=sp-task-38u;
        if(sp<call->min_sp)call->min_sp=sp;
    }
    if(pc==__GEOMETRY_RETURN__||pc==0x1029eu||pc==0x102c2u){
        geometry_returns++;emit(pc);
        for(unsigned i=0;i<16;i++)if(current.r[i]!=call->expected.r[i])geometry_errors++;
        if(current.sr!=call->expected.sr||current.usp!=call->incoming.usp||current.ssp!=call->incoming.ssp)geometry_errors++;
        uint32_t sp=call->incoming.r[15];if(rd32(sp)!=call->return_word||rd32(sp+4u)!=call->object)geometry_errors++;
        if(sp-call->min_sp>geometry_max_depth)geometry_max_depth=sp-call->min_sp;
        call->pending=0;geometry_pending--;
    }
}
