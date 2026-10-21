/* Read-only live checks for lookup,single release andgroup release. */
static const uint32_t leaf_original[3]=__ORIG_ENTRY__;
static const uint32_t leaf_original_end[3]=__ORIG_END__;
static const uint32_t leaf_start[3]=__CODE_START__;
static const uint32_t leaf_entry[3]=__CODE_ENTRY__;
static const uint32_t leaf_end[3]=__CODE_END__;
static const uint32_t leaf_return[3]=__CODE_RETURN__;
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
    if(pc==__HEAP_RETURN__){heap_inits++;heap_base=rd32(0x112d60u);if(heap_base!=__HEAP_FLOOR__)heap_floor_errors++;}
    if(!leaf_pending_any&&!(pc>=0x1ac3cu&&pc<0x1ac68u)&&!(pc>=0x1ae56u&&pc<0x1aedau)&&!(pc>=__ALL_CODE_START__&&pc<__ALL_CODE_END__))return;
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
                if(task!=leaf_task[k]||!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)leaf_counts[k][7]++;
                else if(sp-task-38u<leaf_min_headroom[k])leaf_min_headroom[k]=sp-task-38u;
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
