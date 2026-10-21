/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-owned bounded device adapter. Existing pinned core/libraries unchanged. */
#define lab_movement_write32 lab_base_movement_write32
#include "biwn_geometry_probe_bridge.c"
#undef lab_movement_write32
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_geometry.h"
static struct biwn_gpu_geometry_state render_geometry_state;
static uint32_t render_geometry_original_calls,render_geometry_C_calls;
void lab_render_geometry_reset(void){render_geometry_original_calls=render_geometry_C_calls=0;}
uint32_t lab_render_geometry_stat(unsigned index){return index ? render_geometry_C_calls : render_geometry_original_calls;}
int lab_movement_write32(void *unused,uint32_t address,uint32_t value)
{
    int status;
    struct biwn_gpu_geometry_bus bus={lab_device_read16,lab_device_read32,lab_device_write16,lab_device_write32,NULL,NULL};
    if(address!=0xf03204u || value!=0x4d80u)return lab_base_movement_write32(unused,address,value);
    observe(1,4,address,value);gpu_write(address,value,0);
    if(use_C_decoder){
        render_geometry_C_calls++;
        status=biwn_gpu_geometry_init(&render_geometry_state,0x4d800000u,gpu_ram());
        component=3;
        if(!status)status=biwn_gpu_geometry_run(&bus,&render_geometry_state,100000u);
        component=0;
        if(!status){
            unsigned i;
            memcpy(gpu_ram(),render_geometry_state.local_RAM,4096);
            for(i=0;i<32;i++){movement_bank0[i]=render_geometry_state.registers[0][i];movement_bank1[i]=render_geometry_state.registers[1][i];}
            gpu_write(0xf02100u,render_geometry_state.z|(render_geometry_state.c<<1)|(render_geometry_state.n<<2),0);
            gpu_write(0xf02104u,render_geometry_state.matrix_control,0);gpu_write(0xf02108u,render_geometry_state.matrix_pointer,0);
            gpu_write(0xf0211cu,render_geometry_state.division_control,0);gpu_write(0xf02110u,render_geometry_state.pc,0);
        }
    }else{render_geometry_original_calls++;status=lab_geometry_original(0x4d800000u);}
    if(status){device_error=1;return 1;}
    /* Explicit synchronous dispatcher completion, as in existing kernels.
     * C result retains divider remainder internally; core RO remainder is
     * not written. Cross-kernel fullGPUcontext/timing is not claimed. */
    gpu_write(0xf03204u,0xffffffffu,0);gpu_write(0xf03200u,0,0);
    return 0;
}
