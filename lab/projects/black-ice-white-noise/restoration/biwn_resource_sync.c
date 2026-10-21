#include "biwn_resource_sync.h"
static void bank(struct biwn_task_cpu *s)
{if(s->sr&0x2000u)s->ssp=s->registers[15];else s->usp=s->registers[15];}
static void nz(struct biwn_task_cpu *s,uint32_t v)
{s->sr=(uint16_t)((s->sr&0xfff0u)|(v?0:4)|(v&0x80000000u?8:0));}
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_SYNC_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(v)))return BIWN_SYNC_BUS_ERROR;}while(0)
static enum biwn_sync_status signal_run(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit,int full)
{
    struct biwn_task_cpu s;uint32_t value,ret;int wrapper;
    if(!bus||!state||!limit||!bus->read32||!bus->write32)return BIWN_SYNC_BAD_ARGUMENT;
    if(state->pc!=0xdf04u&&state->pc!=0xdf9cu)return BIWN_SYNC_BAD_PC;
    s=*state;wrapper=s.pc==0xdf9cu;
    if(wrapper){
        R32(s.registers[15]+4u,s.registers[0]);nz(&s,s.registers[0]);
        s.registers[15]-=4u;bank(&s);W32(s.registers[15],0xdfa4u);
    }
    R32(0xc0920u,s.registers[8]);R32(s.registers[8],s.registers[9]);
    s.registers[0]=~s.registers[0];nz(&s,s.registers[0]);
    while(s.registers[9]!=s.registers[8]){
        if(!limit--)return BIWN_SYNC_WORK_LIMIT;
        R32(s.registers[9]+26u,value);value&=s.registers[0];W32(s.registers[9]+26u,value);nz(&s,value);
        R32(s.registers[9],s.registers[9]);
    }
    /* Final CMPA.L compares the same context pointer: X unchanged, Z set. */
    s.sr=(uint16_t)((s.sr&0xfff0u)|4u);s.pc=0xdf20u;
    if(wrapper){R32(s.registers[15],ret);s.registers[15]+=4u;bank(&s);s.pc=ret;}
    if(full){R32(s.registers[15],s.pc);s.registers[15]+=4u;bank(&s);}
    *state=s;return BIWN_SYNC_OK;
}
enum biwn_sync_status biwn_resource_signal_body(struct biwn_world_bus *b,struct biwn_task_cpu *s,uint32_t n){return signal_run(b,s,n,0);}
enum biwn_sync_status biwn_resource_signal_call(struct biwn_world_bus *b,struct biwn_task_cpu *s,uint32_t n){return signal_run(b,s,n,1);}
#undef R32
#undef W32
#define R32(a,v) do{if(bus->read32(bus->context,(a),&(v)))return BIWN_SCHEDULER_BUS_ERROR;}while(0)
#define W32(a,v) do{if(bus->write32(bus->context,(a),(v)))return BIWN_SCHEDULER_BUS_ERROR;}while(0)
#define W16(a,v) do{if(bus->write16(bus->context,(a),(v)))return BIWN_SCHEDULER_BUS_ERROR;}while(0)
static int valid(struct biwn_world_bus *b,struct biwn_task_cpu *s,uint32_t n)
{return b&&s&&n&&b->read16&&b->read32&&b->write16&&b->write32;}
static enum biwn_scheduler_status wait_handler(struct biwn_world_bus *bus,struct biwn_task_cpu *s,uint32_t limit)
{
    enum biwn_scheduler_status status;uint32_t current;
    R32(0xc0920u,current);s->registers[8]=current;
    W32(current+26u,s->registers[0]);nz(s,s->registers[0]);s->pc=0xde08u;
    status=biwn_scheduler_dispatch(bus,s,limit);return status;
}
enum biwn_scheduler_status biwn_resource_wait_dispatch(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit)
{
    struct biwn_task_cpu s;enum biwn_scheduler_status status;
    if(!valid(bus,state,limit)||!(state->sr&0x2000u)||state->pc!=0xdef6u)return BIWN_SCHEDULER_BAD_ARGUMENT;
    s=*state;status=wait_handler(bus,&s,limit);if(!status)*state=s;return status;
}
enum biwn_scheduler_status biwn_resource_wait(struct biwn_world_bus *bus,struct biwn_task_cpu *state,uint32_t limit)
{
    struct biwn_task_cpu s;enum biwn_scheduler_status status;uint32_t vector;int i;
    if(!valid(bus,state,limit)||(state->sr&0x2000u)||state->pc!=0xdf8cu)return BIWN_SCHEDULER_BAD_ARGUMENT;
    s=*state;R32(s.registers[15]+4u,s.registers[0]);nz(&s,s.registers[0]);
    for(i=14;i>=2;--i){if(i==8||i==9)continue;s.registers[15]-=4u;W32(s.registers[15],s.registers[i]);}
    s.usp=s.registers[15];s.registers[15]=s.ssp;
    s.registers[15]-=4u;W32(s.registers[15],0xdf96u);
    s.registers[15]-=2u;W16(s.registers[15],s.sr);s.sr|=0x2000u;
    R32(0x90u,vector);if(vector!=0xdef6u)return BIWN_SCHEDULER_BAD_VECTOR;
    s.pc=vector;status=wait_handler(bus,&s,limit);if(status)return status;
    status=biwn_scheduler_resume_saved(bus,&s);if(status)return status;
    *state=s;return BIWN_SCHEDULER_OK;
}
