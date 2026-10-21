/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-owned original GPU52E0 observer. Preserve the preceding live GPU state;
 * no reset, reconstructed projection, or dispatcher execution is claimed. */
#include "biwn_render_geometry_device_bridge.c"
static uint32_t projection_pcs[1000000],projection_count;
static uint32_t projection_be32(const uint8_t *p){return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3];}
int lab_projection_prepare(void)
{
    unsigned i;
    const uint32_t args[5]={0x47b88,0x47bc8,0,64,0x10a684};
    if(!opened || !movement_bank0 || !movement_arm)return 1;
    if(memcmp(*main_ram+0x52e0,"\x00\xf0\x32\x40\x00\x00\x01\x2c",8))return 2;
    memcpy(gpu_ram()+0x240,*main_ram+0x52e8,1200);
    for(i=0;i<5;i++)gpu_write(0xf0320cu+i*4u,i==2 ? projection_be32(*main_ram+0x49b88) : args[i],0);
    (*main_ram)[0x10a684]=(*main_ram)[0x10a685]=(*main_ram)[0x10a686]=0;(*main_ram)[0x10a687]=1;
    gpu_write(0xf03204,0x52e0,0);
    gpu_write(0xf02110,0xf03240,0);gpu_write(0xf02114,0x2801,0);
    return 0;
}
int lab_projection_original(void)
{
    if(!opened || !movement_arm || gpu_pc()!=0xf03240u)return 1;
    movement_begin=movement_head();movement_arm();
    for(projection_count=0;projection_count<1000000u && gpu_pc()!=0xf031beu;projection_count++){
        projection_pcs[projection_count]=gpu_pc();gpu_execute(1);
    }
    movement_disarm();movement_end=movement_head();GPU_calls+=projection_count;
    return gpu_pc()==0xf031beu ? 0 : 3;
}
uint32_t lab_projection_steps(void){return projection_count;}
uint32_t lab_projection_PC(unsigned i){return i<projection_count ? projection_pcs[i] : 0;}
