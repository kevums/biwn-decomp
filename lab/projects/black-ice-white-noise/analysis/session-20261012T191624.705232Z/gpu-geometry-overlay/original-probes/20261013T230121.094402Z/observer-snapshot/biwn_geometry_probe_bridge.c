/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-owned original-GPU observer. No reconstructed geometry implementation.
 * Existing pinned core/device libraries are not modified or replaced. */
#include "biwn_movement_device_bridge.c"
static uint32_t geometry_pcs[100000],geometry_count;
int lab_geometry_original(uint32_t seed)
{
    unsigned i;
    if(!opened || !movement_bank0 || !movement_arm)return 1;
    if(memcmp(*main_ram+0x4d80,"\x00\xf0\x32\x40\x00\x00\x01\x54",8))return 2;
    gpu_reset();memcpy(gpu_ram()+0x240,*main_ram+0x4d88,1360);
    for(i=0;i<32;i++){seed=1664525u*seed+1013904223u;movement_bank0[i]=seed;movement_bank1[i]=~seed;}
    gpu_write(0xf0320c,0x47b88,0);gpu_write(0xf03210,0x49b8c,0);
    gpu_write(0xf03214,0x49bb4,0);gpu_write(0xf03218,0x49b88,0);
    gpu_write(0xf0211c,0xa5a50001u,0);gpu_write(0xf02110,0xf03240u,0);gpu_write(0xf02114,0x2801u,0);
    movement_begin=movement_head();movement_arm();
    for(geometry_count=0;geometry_count<100000u && gpu_pc()!=0xf031beu;geometry_count++){
        geometry_pcs[geometry_count]=gpu_pc();gpu_execute(1);
    }
    movement_disarm();movement_end=movement_head();GPU_calls+=geometry_count;
    return gpu_pc()==0xf031beu ? 0 : 3;
}
uint32_t lab_geometry_steps(void){return geometry_count;}
uint32_t lab_geometry_PC(unsigned i){return i<geometry_count ? geometry_pcs[i] : 0;}
uint32_t lab_geometry_final_PC(void){return gpu_pc();}
void *lab_geometry_gpu_RAM(void){return gpu_ram();}
