/* SPDX-License-Identifier: GPL-3.0-or-later
 * Original dispatcher entry and GPU57A0-only observer. No C setup code here. */
#include "biwn_draw_probe_bridge.c"
static uint32_t setup57_pcs[100000],setup57_count;
int lab_setup57_watch(void)
{
    int (*add_watch)(uint32_t,uint32_t,unsigned);
    if(!opened)return 1;
    add_watch=(int (*)(uint32_t,uint32_t,unsigned))harness_dlsym(&config,"vjtrace_watch_add");
    return !add_watch || add_watch(0xf02200u,0xf0229cu,3)<0 ? 2 : 0;
}
int lab_setup57_prepare(void)
{
    uint32_t count;
    if(!opened || !movement_arm)return 1;
    memcpy(gpu_ram(),*main_ram+0x40a8,512);
    gpu_write(0xf03208,0x52e0,0);gpu_write(0xf03204,0x57a0,0);
    gpu_write(0xf02110,0xf031be,0);gpu_write(0xf02114,0x2801,0);
    for(count=0;count<4000u && gpu_pc()!=0xf03240u;count++)gpu_execute(1);
    if(gpu_pc()!=0xf03240u)return 3;
    return memcmp(gpu_ram()+0x240,*main_ram+0x57a8,232) ? 4 : 0;
}
int lab_setup57_original(void)
{
    if(!opened || !movement_arm || gpu_pc()!=0xf03240u)return 1;
    movement_begin=movement_head();movement_arm();
    for(setup57_count=0;setup57_count<100000u && gpu_pc()!=0xf031beu;setup57_count++){
        setup57_pcs[setup57_count]=gpu_pc();gpu_execute(1);
    }
    movement_disarm();movement_end=movement_head();GPU_calls+=setup57_count;
    return gpu_pc()==0xf031beu ? 0 : 3;
}
uint32_t lab_setup57_steps(void){return setup57_count;}
uint32_t lab_setup57_PC(unsigned i){return i<setup57_count ? setup57_pcs[i] : 0;}
