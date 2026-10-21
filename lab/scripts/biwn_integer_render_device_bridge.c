/* SPDX-License-Identifier: GPL-3.0-or-later
 * Source-consistent integer divider fixture for native/C scene comparisons.
 * Keeps earlier fractional fixtures/libraries intact for their declared scope. */
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_geometry.h"
static enum biwn_gpu_geometry_status integer_geometry_init(struct biwn_gpu_geometry_state *state,uint32_t seed,const uint8_t *ram)
{
    enum biwn_gpu_geometry_status status=biwn_gpu_geometry_init(state,seed,ram);
    if(!status)state->division_control=0;
    return status;
}
#define biwn_gpu_geometry_init integer_geometry_init
#define lab_device_open lab_original_device_open
#include "biwn_projection_probe_bridge.c"
#undef lab_device_open
#undef biwn_gpu_geometry_init
static void (*integer_original_gpu_write)(uint32_t,uint32_t,uint32_t);
static void integer_gpu_write(uint32_t address,uint32_t value,uint32_t who)
{
    integer_original_gpu_write(address,address==0xf0211cu?0u:value,who);
}
int lab_device_open(const char *core,const char *bios,int fast)
{
    int status=lab_original_device_open(core,bios,fast);
    if(!status){integer_original_gpu_write=gpu_write;gpu_write=integer_gpu_write;}
    return status;
}
uint32_t lab_integer_division_control(void)
{
    size_t (*save_state)(uint8_t *);uint8_t raw[8192];uint32_t value;
    save_state=(size_t (*)(uint8_t *))harness_dlsym(&config,"GPUStateSave");
    if(!save_state || save_state(raw)<=4396u)return 0xffffffffu;
    memcpy(&value,raw+4132,4);return value;
}
