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
    if(!scan_pending&&!(pc>=0x102c4u&&pc<0x1039cu)&&!(pc>=__SCAN_START__&&pc<__SCAN_END__))return;
    uint32_t task=scan_read32(0xc0920u);struct scan_call *s=NULL;
    if(pc==0x102c4u){
        s=scan_slot(task);if(!s)return;if(s->pending)scan_errors++;
        read_cpu(&s->incoming);s->expected=s->incoming;s->min_sp=s->incoming.r[15];s->ret=scan_read32(s->incoming.r[15]);s->object=scan_read32(s->incoming.r[15]+4u);
        scan_predict(s);s->pending=1;scan_pending++;scan_entries++;scan_iterations+=s->iterations;
        if(s->success)scan_successes++;else scan_failures++;if(s->skipped)scan_skips++;emit(pc);
    }
    if(pc>0x102c4u&&pc<0x1039cu)scan_old_steps++;
    if(pc==__SCAN_ENTRY__)scan_native_entries++;
    if(pc>=__SCAN_START__&&pc<__SCAN_END__)scan_native_steps++;
    if(!s)for(unsigned i=0;i<scan_slots;i++)if(scan_calls[i].task==task&&scan_calls[i].pending){s=&scan_calls[i];break;}
    if(!s||!s->pending)return;struct cpu current;read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];scan_user_observations++;
        if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)scan_stack_outside++;
        else if(sp-task-38u<scan_min_headroom)scan_min_headroom=sp-task-38u;
        if(sp<s->min_sp)s->min_sp=sp;
    }
    if(pc==__SCAN_RETURN__||pc==0x1039au){
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
