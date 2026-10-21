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
static uint32_t select_offset(uint16_t value){uint16_t shifted=(uint16_t)((uint32_t)value<<6);return (uint32_t)(int32_t)(int16_t)shifted;}
static void watch_select(uint32_t pc){
    if(!select_pending&&!(pc>=0x1039cu&&pc<0x10430u)&&!(pc>=__SELECT_START__&&pc<__SELECT_END__))return;
    uint32_t task=rd32(0xc0920u);struct select_call *s=NULL;
    if(pc==0x1039cu){
        s=select_slot(task);if(!s)return;if(s->pending)select_errors++;
        read_cpu(&s->incoming);s->expected=s->incoming;uint32_t sp=s->incoming.r[15];s->min_sp=sp;s->ret=rd32(sp);s->object=rd32(sp+4);s->requested=rd16(sp+8);
        uint32_t object=s->object;uint16_t sector=rd16(object+64u);uint32_t shifted=(uint32_t)(int32_t)(int16_t)sector*4u;uint32_t header=rd32(0x49bb4u+shifted);uint16_t count=rd16(header);
        s->header=header;s->sector=sector;s->count=count;s->success=(int16_t)s->requested<(int16_t)count;
        s->expected.r[0]=shifted&0xffff0000u;s->expected.r[1]=(s->incoming.r[1]&0xffff0000u)|s->requested;s->expected.r[8]=header;s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|4u|((sector&0x8000u)?16u:0u));
        if(s->success){
            s->record=rd32(header+8u)+(uint32_t)((int32_t)(int16_t)s->requested*20);
            uint32_t record=s->record;s->lower_x=(rd32(object+4u)&0xfffffc00u)+select_offset(rd16(record+10u));s->lower_z=(rd32(object+10u)&0xfffffc00u)+select_offset(rd16(record+14u));s->upper_x=s->lower_x+select_offset(rd16(record+16u));uint16_t last_width=rd16(record+18u);s->upper_z=s->lower_z+select_offset(last_width);
            s->expected.r[0]=1;s->expected.r[1]=rd32(object+10u)&0xfffffc00u;s->expected.r[8]=s->upper_z;s->expected.r[9]=record;s->expected.sr=(uint16_t)((s->incoming.sr&0xffe0u)|((last_width&0x400u)?16u:0u));select_successes++;
        }else select_failures++;
        s->pending=1;select_pending++;select_entries++;emit(pc);
    }
    if(pc>0x1039cu&&pc<0x10430u)select_old_steps++;
    if(pc==__SELECT_ENTRY__)select_native_entries++;
    if(pc>=__SELECT_START__&&pc<__SELECT_END__)select_native_steps++;
    if(!s)for(unsigned i=0;i<select_slots;i++)if(select_calls[i].task==task&&select_calls[i].pending){s=&select_calls[i];break;}
    if(!s||!s->pending)return;struct cpu current;read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];select_user_observations++;
        if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)select_stack_outside++;
        else if(sp-task-38u<select_min_headroom)select_min_headroom=sp-task-38u;
        if(sp<s->min_sp)s->min_sp=sp;
    }
    if(pc==__SELECT_RETURN__||pc==0x1042eu){
        uint64_t errors_before=select_errors;select_returns++;emit(pc);for(unsigned i=0;i<16;i++)if(current.r[i]!=s->expected.r[i])select_errors++;
        if(current.sr!=s->expected.sr||current.usp!=s->incoming.usp||current.ssp!=s->incoming.ssp)select_errors++;
        uint32_t sp=s->incoming.r[15],obj=s->object;if(rd32(sp)!=s->ret||rd32(sp+4)!=obj||rd16(sp+8)!=s->requested)select_errors++;
        if(s->success&&(rd16(obj+66)!=s->requested||rd32(obj+68)!=s->record||rd32(obj+76)!=s->lower_x||rd32(obj+84)!=s->lower_z||rd32(obj+72)!=s->upper_x||rd32(obj+80)!=s->upper_z))select_errors++;
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
