/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-owned bridge/oracle; pinned emulator core and old libraries unchanged.
 */
#include "biwn_inventory_device_bridge.c"
#include "../tools/virtualjaguar-runtime-source/src/core/vjtrace.h"
#include "../projects/black-ice-white-noise/restoration/biwn_movement_matrix.h"
#include "../projects/black-ice-white-noise/restoration/biwn_movement_submit.h"

static uint32_t *movement_bank0,*movement_bank1;
static void (*movement_arm)(void),(*movement_disarm)(void);
static uint64_t (*movement_head)(void);
static int (*movement_ring_read)(uint64_t,vjtrace_ev *);
static void (*movement_backtrace)(int,uint32_t *,int,int *);
static uint64_t movement_begin,movement_end;
static uint32_t movement_steps;

int lab_movement_setup(void)
{
    int (*add_watch)(uint32_t,uint32_t,unsigned);
    if(!opened)return 1;
#define RESOLVE(variable,type,symbol) variable=(type)harness_dlsym(&config,symbol);if(!variable)return 2
    RESOLVE(movement_bank0,uint32_t *,"gpu_reg_bank_0");RESOLVE(movement_bank1,uint32_t *,"gpu_reg_bank_1");
    RESOLVE(movement_arm,void (*)(void),"vjtrace_arm");RESOLVE(movement_disarm,void (*)(void),"vjtrace_disarm");
    RESOLVE(movement_head,uint64_t (*)(void),"vjtrace_ring_head");
    RESOLVE(movement_ring_read,int (*)(uint64_t,vjtrace_ev *),"vjtrace_ring_read");
    RESOLVE(movement_backtrace,void (*)(int,uint32_t *,int,int *),"vjtrace_backtrace");
    RESOLVE(add_watch,int (*)(uint32_t,uint32_t,unsigned),"vjtrace_watch_add");
#undef RESOLVE
    movement_disarm();return add_watch(0,0x1fffffu,3)<0 ? 3 : 0;
}

int lab_movement_original(uint32_t base,uint32_t angle1,uint32_t angle2,uint32_t angle3,uint32_t speed,uint32_t seed)
{
    unsigned i;
    if(!opened || !movement_bank0 || !movement_arm)return 1;
    if((*main_ram)[0x4320]!=0 || (*main_ram)[0x4321]!=0xf0 || (*main_ram)[0x4322]!=0x32 || (*main_ram)[0x4323]!=0x40 ||
       (*main_ram)[0x4324]!=0 || (*main_ram)[0x4325]!=0 || (*main_ram)[0x4326]!=0 || (*main_ram)[0x4327]!=254)return 2;
    gpu_reset();memcpy(gpu_ram()+0x240,*main_ram+0x4328,1016);
    for(i=0;i<32;i++){seed=1664525u*seed+1013904223u;movement_bank0[i]=seed;movement_bank1[i]=~seed;}
    gpu_write(0xf0320c,base,0);gpu_write(0xf03210,angle1,0);gpu_write(0xf03214,angle2,0);gpu_write(0xf03218,angle3,0);gpu_write(0xf0321c,speed,0);
    gpu_write(0xf0211c,0xa5a50001u,0);gpu_write(0xf02110,0xf03240u,0);gpu_write(0xf02114,0x2801u,0);
    movement_begin=movement_head();movement_arm();
    for(movement_steps=0;movement_steps<10000 && gpu_pc()!=0xf031beu;movement_steps++)gpu_execute(1);
    movement_disarm();movement_end=movement_head();GPU_calls+=movement_steps;
    return gpu_pc()==0xf031beu ? 0 : 3;
}

uint32_t lab_movement_register(unsigned bank,unsigned reg)
{return bank<2 && reg<32 ? (bank ? movement_bank1[reg] : movement_bank0[reg]) : 0;}
uint32_t lab_movement_steps(void){return movement_steps;}
uint64_t lab_movement_event_count(void){return movement_end-movement_begin;}
int lab_movement_event(uint64_t index,uint32_t *out)
{
    vjtrace_ev event;
    if(!out || movement_begin+index>=movement_end || !movement_ring_read(movement_begin+index,&event))return 1;
    out[0]=event.type;out[1]=event.who;out[2]=event.pc;out[3]=event.addr;out[4]=event.value;return 0;
}
int lab_movement_history(uint32_t *out)
{
    int count=0;
    if(out)movement_backtrace(3,out,1024,&count);
    return count;
}

int lab_movement_C(uint32_t base,uint32_t angle1,uint32_t angle2,uint32_t angle3,uint32_t speed,struct biwn_movement_result *result,uint32_t budget)
{
    struct biwn_movement_bus bus={lab_device_read16,lab_device_write16,NULL,budget};
    int status;
    if(!opened || !use_C_decoder)return 1;
    component=2;status=biwn_movement_matrix(&bus,base,angle1,angle2,angle3,speed,result);component=0;
    return status;
}

int lab_movement_write32(void *unused,uint32_t address,uint32_t value)
{
    uint32_t args[5],i,division;
    struct biwn_movement_result output;
    int status;
    if(address!=0xf03204u || value!=0x4320u)return lab_device_write32(unused,address,value);
    observe(1,4,address,value);gpu_write(address,value,0);
    for(i=0;i<5;i++)args[i]=gpu_read(0xf0320cu+i*4u,0);
    if(use_C_decoder)status=lab_movement_C(args[0],args[1],args[2],args[3],args[4],&output,12);
    else {
        division=gpu_read(0xf0211cu,0);
        status=lab_movement_original(args[0],args[1],args[2],args[3],args[4],0x4320u);
        gpu_write(0xf0211cu,division,0);
    }
    if(status){device_error=1;return 1;}
    /* Explicit synchronous dispatcher completion model, as in sprite bridge. */
    gpu_write(0xf03204u,0xffffffffu,0);gpu_write(0xf03200u,0,0);
    return 0;
}

int lab_movement_submit_C(uint32_t base,uint32_t a1,uint32_t a2,uint32_t a3,uint32_t speed)
{
    struct biwn_gpu_bus bus={lab_device_read32,lab_movement_write32,NULL,100000u};
    return biwn_movement_submit(&bus,base,a1,a2,a3,speed);
}
