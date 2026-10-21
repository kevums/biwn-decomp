/* SPDX-License-Identifier: GPL-3.0-or-later
 * Observe original list-consumer overlay up to its source handoff boundary. */
#include "biwn_draw_integer_probe_bridge.c"
static uint32_t consumer_pcs[100000],consumer_count;
int lab_consumer6380_prepare(void)
{
    uint32_t count;
    if(!opened || !movement_arm)return 1;
    memcpy(gpu_ram(),*main_ram+0x40a8,512);
    gpu_write(0xf03208,0x52e0,0);gpu_write(0xf03204,0x57a0,0);
    gpu_write(0xf02110,0xf031be,0);gpu_write(0xf02114,0x2801,0);
    for(count=0;count<20000u;count++){
        if(gpu_pc()==0xf03240u && gpu_read(0xf03208,0)==0x6380u)
            return memcmp(gpu_ram()+0x240,*main_ram+0x6388,216) ? 4 : 0;
        gpu_execute(1);
    }
    return 3;
}
int lab_consumer6380_original(void)
{
    if(!opened || !movement_arm || gpu_pc()!=0xf03240u)return 1;
    movement_begin=movement_head();movement_arm();
    for(consumer_count=0;consumer_count<100000u;consumer_count++){
        uint32_t pc=gpu_pc();
        if(pc==0xf031beu || pc==0xf03440u || pc==0xf03ca0u)break;
        consumer_pcs[consumer_count]=pc;gpu_execute(1);
    }
    movement_disarm();movement_end=movement_head();GPU_calls+=consumer_count;
    return consumer_count<100000u ? 0 : 3;
}
uint32_t lab_consumer6380_steps(void){return consumer_count;}
uint32_t lab_consumer6380_PC(unsigned i){return i<consumer_count ? consumer_pcs[i] : 0;}
