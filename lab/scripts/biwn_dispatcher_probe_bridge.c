/* SPDX-License-Identifier: GPL-3.0-or-later
 * Original31-instruction dispatcher observer with explicit host idle policy. */
#include "biwn_draw_integer_probe_bridge.c"
static uint32_t dispatcher_pcs[100000],dispatcher_count,dispatcher_polls,dispatcher_flags[100000];
int lab_dispatcher_prepare(uint32_t header,int cache_hit)
{
    uint32_t destination,words;
    if(!opened||!movement_arm)return 1;
    memcpy(gpu_ram(),*main_ram+0x40a8,512);
    if(header!=0xffffffffu){
        if(header>0x1ffff8u)return 2;
        destination=projection_be32(*main_ram+header);words=projection_be32(*main_ram+header+4);
        if(!words||words>1024u||destination<0xf03000u||destination+words*4u>0xf04000u)return 3;
        if(cache_hit)memcpy(gpu_ram()+destination-0xf03000u,*main_ram+header+8,words*4u);
    }
    gpu_write(0xf03208,cache_hit?header:0x52e0u,0);gpu_write(0xf03204,header,0);gpu_write(0xf03200,0x12345678u,0);
    gpu_write(0xf02110,0xf031be,0);gpu_write(0xf02114,0x2801,0);return 0;
}
int lab_dispatcher_original(unsigned yield_idle,uint32_t inject_header,unsigned wait_reads)
{
    size_t (*save_state)(uint8_t *);uint8_t raw[8192];
    if(!opened||!movement_arm||gpu_pc()!=0xf031beu||yield_idle>1)return 1;
    save_state=(size_t (*)(uint8_t *))harness_dlsym(&config,"GPUStateSave");if(!save_state)return 2;
    movement_begin=movement_head();movement_arm();dispatcher_polls=0;
    for(dispatcher_count=0;dispatcher_count<100000u;dispatcher_count++){
        uint32_t pc=gpu_pc();
        if(pc<0xf031beu||pc>=0xf03200u)break;
        if(pc==0xf031ceu){
            if(inject_header!=0xffffffffu&&dispatcher_polls++==wait_reads)gpu_write(0xf03204,inject_header,0);
            if(yield_idle&&gpu_read(0xf03204,0)==0xffffffffu&&gpu_read(0xf03200,0)==0)break;
        }
        dispatcher_pcs[dispatcher_count]=pc;if(save_state(raw)<4396u){movement_disarm();return 2;}
        dispatcher_flags[dispatcher_count]=raw[4136]|((uint32_t)raw[4138]<<1)|((uint32_t)raw[4137]<<2);gpu_execute(1);
    }
    movement_disarm();movement_end=movement_head();GPU_calls+=dispatcher_count;
    return dispatcher_count<100000u?0:3;
}
uint32_t lab_dispatcher_steps(void){return dispatcher_count;}
uint32_t lab_dispatcher_PC(unsigned i){return i<dispatcher_count?dispatcher_pcs[i]:0;}
uint32_t lab_dispatcher_polls(void){return dispatcher_polls;}

uint32_t lab_dispatcher_flags(unsigned i){return i<dispatcher_count?dispatcher_flags[i]:0;}
