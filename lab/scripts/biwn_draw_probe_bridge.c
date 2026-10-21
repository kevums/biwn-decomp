/* SPDX-License-Identifier: GPL-3.0-or-later
 * Original draw-chain observer, including original resident dispatcher.
 * No game frame, GPU reset between kernels, or C draw claim. */
#include "biwn_projection_probe_bridge.c"
static uint32_t draw_pcs[5000000],draw_count;
static uint32_t draw_commands[10000],draw_command_count;
int lab_draw_original(void)
{
    uint32_t previous=0xffffffffu;
    if(!opened || !movement_arm)return 1;
    /* OriginalresidentCPU40A8..42A8 contains dispatcherF031BE..F031FE.
     * Preserve sourcemailboxes/arguments and projection output/local data. */
    memcpy(gpu_ram(),*main_ram+0x40a8,512);
    gpu_write(0xf03208,0x52e0,0);gpu_write(0xf03204,0x57a0,0);
    gpu_write(0xf02110,0xf031be,0);gpu_write(0xf02114,0x2801,0);
    draw_command_count=0;movement_begin=movement_head();movement_arm();
    for(draw_count=0;draw_count<5000000u;draw_count++){
        uint32_t pc=gpu_pc(),command=gpu_read(0xf03204,0);
        if(pc==0xf031ceu && command==0xffffffffu && gpu_read(0xf03200,0)==0)break;
        if(pc==0xf031ceu && command!=0xffffffffu){
            if(draw_command_count>=10000u){movement_disarm();return 4;}
            draw_commands[draw_command_count++]=command;previous=command;
        }
        draw_pcs[draw_count]=pc;gpu_execute(1);
    }
    (void)previous;movement_disarm();movement_end=movement_head();GPU_calls+=draw_count;
    return draw_count<5000000u ? 0 : 3;
}
uint32_t lab_draw_steps(void){return draw_count;}
uint32_t lab_draw_PC(unsigned i){return i<draw_count ? draw_pcs[i] : 0;}
uint32_t lab_draw_command_count(void){return draw_command_count;}
uint32_t lab_draw_command(unsigned i){return i<draw_command_count ? draw_commands[i] : 0;}
