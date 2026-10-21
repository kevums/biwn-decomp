/* SPDX-License-Identifier: GPL-3.0-or-later
 * Isolated diagnosis of host-supplied divider mode. Existing libraries/core
 * unchanged. Original CPU/GPU register writes inside core are untouched. */
#define lab_device_open lab_original_device_open
#include "biwn_draw_probe_bridge.c"
#undef lab_device_open
static void (*integer_original_gpu_write)(uint32_t,uint32_t,uint32_t);
static void integer_gpu_write(uint32_t address,uint32_t value,uint32_t who)
{
    integer_original_gpu_write(address,address==0xf0211cu ? 0u : value,who);
}
int lab_device_open(const char *core,const char *bios,int fast)
{
    int status=lab_original_device_open(core,bios,fast);
    if(!status){integer_original_gpu_write=gpu_write;gpu_write=integer_gpu_write;}
    return status;
}
