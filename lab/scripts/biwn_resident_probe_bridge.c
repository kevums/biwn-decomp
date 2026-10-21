/* SPDX-License-Identifier: GPL-3.0-or-later
 * Original resident entry preparation and bounded original shader observer. */
#include "biwn_draw_integer_probe_bridge.c"
static uint32_t resident_pcs[1000000],resident_count;
int lab_resident_prepare(uint32_t occurrence)
{
    uint32_t count,seen=0,previous=0;
    if(!opened||!movement_arm||!occurrence)return 1;
    memcpy(gpu_ram(),*main_ram+0x40a8,512);
    gpu_write(0xf03208,0x52e0,0);gpu_write(0xf03204,0x57a0,0);
    gpu_write(0xf02110,0xf031be,0);gpu_write(0xf02114,0x2801,0);
    for(count=0;count<1000000u;count++){
        uint32_t pc=gpu_pc();
        if((pc==0xf03440u||pc==0xf03ca0u)&&previous<0xf03440u&&++seen==occurrence){GPU_calls+=count;return 0;}
        if(pc==0xf031ceu&&gpu_read(0xf03204,0)==0xffffffffu&&gpu_read(0xf03200,0)==0){GPU_calls+=count;return 5;}
        previous=pc;gpu_execute(1);
    }
    GPU_calls+=count;return 3;
}
int lab_resident_original(void)
{
    if(!opened||!movement_arm||(gpu_pc()!=0xf03440u&&gpu_pc()!=0xf03ca0u))return 1;
    movement_begin=movement_head();movement_arm();
    for(resident_count=0;resident_count<1000000u&&gpu_pc()!=0xf031beu;resident_count++){
        resident_pcs[resident_count]=gpu_pc();gpu_execute(1);
    }
    movement_disarm();movement_end=movement_head();GPU_calls+=resident_count;
    return gpu_pc()==0xf031beu?0:3;
}
uint32_t lab_resident_steps(void){return resident_count;}
uint32_t lab_resident_PC(unsigned i){return i<resident_count?resident_pcs[i]:0;}
int lab_resident_watch(void)
{
    int (*add_watch)(uint32_t,uint32_t,unsigned);
    if(!opened)return 1;
    add_watch=(int (*)(uint32_t,uint32_t,unsigned))harness_dlsym(&config,"vjtrace_watch_add");
    return !add_watch||add_watch(0xf02200u,0xf0229cu,3)<0?2:0;
}
