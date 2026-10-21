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
    if(!interior_pending&&!(pc>=0x10520u&&pc<0x10652u)&&!(pc>=__INTERIOR_START__&&pc<__INTERIOR_END__))return;
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
    if(pc==__INTERIOR_ACTOR_ENTRY__||pc==__INTERIOR_SPRITE_ENTRY__)interior_native_entries++;
    if(pc>=__INTERIOR_START__&&pc<__INTERIOR_END__)interior_native_steps++;
    if(!s)for(unsigned i=0;i<interior_slots;i++)if(interior_calls[i].task==task&&interior_calls[i].pending){s=&interior_calls[i];break;}
    if(!s||!s->pending)return;struct cpu current;read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];interior_user_observations++;
        if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)interior_stack_outside++;
        else if(sp-task-38u<interior_min_headroom)interior_min_headroom=sp-task-38u;
        if(sp<s->min_sp)s->min_sp=sp;
    }
    if(pc==__INTERIOR_RETURN__||pc==(s->kind?0x10650u:0x105d8u)){
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
