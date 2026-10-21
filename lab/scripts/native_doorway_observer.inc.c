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
    if(!door_pending&&!(pc>=0x10430u&&pc<0x10520u)&&!(pc>=__DOOR_START__&&pc<__DOOR_END__))return;
    uint32_t task=door_read(0xc0920u,4);struct door_call *s=NULL;
    if(pc==0x10430u){
        s=door_slot(task);if(!s)return;if(s->pending)door_errors++;read_cpu(&s->incoming);s->expected=s->incoming;s->min_sp=s->incoming.r[15];s->ret=door_read(s->min_sp,4);s->object=door_read(s->min_sp+4u,4);s->index=door_read(s->min_sp+8u,2);s->direction=door_read(s->min_sp+10u,2);
        door_predict(s);s->pending=1;door_pending++;door_entries++;if(s->path==0)door_count_rejects++;else if(s->path==1)door_sentinels++;else if(s->path==2)door_key_mismatches++;else door_successes++;emit(pc);
    }
    if(pc>0x10430u&&pc<0x10520u)door_old_steps++;
    if(pc==__DOOR_ENTRY__)door_native_entries++;
    if(pc>=__DOOR_START__&&pc<__DOOR_END__)door_native_steps++;
    if(!s)for(unsigned i=0;i<door_slots;i++)if(door_calls[i].task==task&&door_calls[i].pending){s=&door_calls[i];break;}
    if(!s||!s->pending)return;struct cpu current;read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];door_user_observations++;
        if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)door_stack_outside++;
        else if(sp-task-38u<door_min_headroom)door_min_headroom=sp-task-38u;
        if(sp<s->min_sp)s->min_sp=sp;
    }
    if(pc==__DOOR_RETURN__||pc==0x1051eu){
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
