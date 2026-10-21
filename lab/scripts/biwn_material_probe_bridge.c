/* SPDX-License-Identifier: GPL-3.0-or-later
 * Original material overlays, captured after original dispatcher/list consumer. */
#include "biwn_draw_integer_probe_bridge.c"
static uint32_t material_pcs[1000000],material_count;
int lab_material_prepare(uint32_t header,uint32_t occurrence)
{
    uint32_t count,seen=0,words;
    if(!opened||!movement_arm||!occurrence)return 1;
    if(header!=0x6460u&&header!=0x6720u&&header!=0x69a0u)return 2;
    words=projection_be32(*main_ram+header+4);
    memcpy(gpu_ram(),*main_ram+0x40a8,512);
    gpu_write(0xf03208,0x52e0,0);gpu_write(0xf03204,0x57a0,0);
    gpu_write(0xf02110,0xf031be,0);gpu_write(0xf02114,0x2801,0);
    for(count=0;count<1000000u;count++){
        uint32_t pc=gpu_pc();
        if(pc==0xf03240u&&gpu_read(0xf03208,0)==header&&++seen==occurrence)
            return memcmp(gpu_ram()+0x240,*main_ram+header+8,words*4u)?4:0;
        if(pc==0xf031ceu&&gpu_read(0xf03204,0)==0xffffffffu&&gpu_read(0xf03200,0)==0)return 5;
        gpu_execute(1);
    }
    return 3;
}
int lab_material_original(void)
{
    if(!opened||!movement_arm||gpu_pc()!=0xf03240u)return 1;
    movement_begin=movement_head();movement_arm();
    for(material_count=0;material_count<1000000u&&gpu_pc()!=0xf03440u;material_count++){
        material_pcs[material_count]=gpu_pc();gpu_execute(1);
    }
    movement_disarm();movement_end=movement_head();GPU_calls+=material_count;
    return gpu_pc()==0xf03440u?0:3;
}
uint32_t lab_material_steps(void){return material_count;}
uint32_t lab_material_PC(unsigned i){return i<material_count?material_pcs[i]:0;}
