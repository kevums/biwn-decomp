/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-owned bridge to the pinned emulator's blitter. Reconstructed game C
 * can render without executing original CPU/GPU instructions. Original GPU
 * overlay mode exists only as a separate comparison oracle. */
#include "harness/harness.h"
#include "../projects/black-ice-white-noise/restoration/biwn_inventory_pipeline.h"
#include "../projects/black-ice-white-noise/restoration/biwn_sprite_decode.h"
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

static harness_config config;
static uint8_t **main_ram,*(*gpu_ram)(void);
static void (*tom_reset)(void),(*gpu_reset)(void),(*gpu_execute)(int32_t);
static void (*gpu_write)(uint32_t,uint32_t,uint32_t),(*blitter_write)(uint32_t,uint32_t,uint32_t);
static uint32_t (*gpu_pc)(void),(*gpu_read)(uint32_t,uint32_t),(*blitter_read)(uint32_t,uint32_t);
static char core_name[4096],bios_name[4096];
static int opened,use_C_decoder,device_error;
static uint32_t GPU_calls,C_decode_calls,original_decode_calls,blit_calls;
static void (*observer)(unsigned,unsigned,uint32_t,uint32_t);
static unsigned component;

void lab_device_observe(void (*callback)(unsigned,unsigned,uint32_t,uint32_t)) { observer=callback; }
static void observe(unsigned write,unsigned width,uint32_t address,uint32_t value)
{
    if (observer) observer(component*2u+write,width,address,value);
}

int lab_device_read8(void *,uint32_t,uint8_t *);
int lab_device_read16(void *,uint32_t,uint16_t *);
int lab_device_read32(void *,uint32_t,uint32_t *);
int lab_device_write16(void *,uint32_t,uint16_t);
int lab_device_write32(void *,uint32_t,uint32_t);

int lab_device_open(const char *core,const char *bios,int fast)
{
    harness_config defaults=HARNESS_CONFIG_DEFAULT;
    if (opened || !core || !bios || strlen(core)>=sizeof(core_name) || strlen(bios)>=sizeof(bios_name)) return 1;
    strcpy(core_name,core);strcpy(bios_name,bios);config=defaults;
    config.core_path=core_name;config.system_dir=bios_name;config.quiet=1;
    harness_set_option(&config,"virtualjaguar_usefastblitter",fast ? "enabled" : "disabled");
    if (!harness_load_core(&config) || !harness_load_no_content(&config)) return 2;
#define RESOLVE(variable,type,symbol) variable=(type)harness_dlsym(&config,symbol);if (!variable) return 3
    RESOLVE(main_ram,uint8_t **,"jaguarMainRAM");RESOLVE(gpu_ram,uint8_t *(*)(void),"GPUGetRAM");
    RESOLVE(tom_reset,void (*)(void),"TOMReset");RESOLVE(gpu_reset,void (*)(void),"GPUReset");
    RESOLVE(gpu_execute,void (*)(int32_t),"GPUExec");RESOLVE(gpu_pc,uint32_t (*)(void),"GPUGetPC");
    RESOLVE(gpu_write,void (*)(uint32_t,uint32_t,uint32_t),"GPUWriteLong");RESOLVE(gpu_read,uint32_t (*)(uint32_t,uint32_t),"GPUReadLong");
    RESOLVE(blitter_write,void (*)(uint32_t,uint32_t,uint32_t),"BlitterWriteLong");RESOLVE(blitter_read,uint32_t (*)(uint32_t,uint32_t),"BlitterReadLong");
#undef RESOLVE
    opened=1;return 0;
}

void lab_device_close(void)
{
    if (opened) harness_shutdown(&config);
    opened=0;observer=NULL;
}

int lab_device_seed(const uint8_t *ram,uint32_t bytes,int C_decoder)
{
    if (!opened || !ram || bytes!=0x200000u) return 1;
    tom_reset();gpu_reset();memcpy(*main_ram,ram,bytes);
    gpu_write(0xf03200,0,0);gpu_write(0xf03204,0xffffffffu,0);
    use_C_decoder=C_decoder;device_error=0;GPU_calls=C_decode_calls=original_decode_calls=blit_calls=0;component=0;
    return 0;
}

uint8_t *lab_device_ram(void) { return opened ? *main_ram : NULL; }

int lab_device_read8(void *unused,uint32_t address,uint8_t *value)
{
    (void)unused;
    if (!opened || !value || address>=0x200000u) return 1;
    *value=(*main_ram)[address];observe(0,1,address,*value);return 0;
}

int lab_device_read16(void *unused,uint32_t address,uint16_t *value)
{
    (void)unused;
    if (!opened || !value || address>0x1ffffeu) return 1;
    *value=((uint16_t)(*main_ram)[address]<<8)|(*main_ram)[address+1];observe(0,2,address,*value);return 0;
}

int lab_device_read32(void *unused,uint32_t address,uint32_t *value)
{
    (void)unused;
    if (!opened || !value) return 1;
    if (address<=0x1ffffcu) {
        *value=((uint32_t)(*main_ram)[address]<<24)|((uint32_t)(*main_ram)[address+1]<<16)|((uint32_t)(*main_ram)[address+2]<<8)|(*main_ram)[address+3];observe(0,4,address,*value);return 0;
    }
    if (address>=0xf03200u && address<=0xf03ffcu) { *value=gpu_read(address,0);observe(0,4,address,*value);return 0; }
    if (address>=0xf02200u && address<=0xf0229cu) { *value=blitter_read(address,0);observe(0,4,address,*value);return 0; }
    return 1;
}

int lab_device_write16(void *unused,uint32_t address,uint16_t value)
{
    (void)unused;
    if (!opened || address>0x1ffffeu) return 1;
    observe(1,2,address,value);(*main_ram)[address]=(uint8_t)(value>>8);(*main_ram)[address+1]=(uint8_t)value;return 0;
}

static int original_sprite(uint32_t base,uint32_t index,uint32_t destination)
{
    uint32_t steps;
    if ((*main_ram)[0x4b00]!=0 || (*main_ram)[0x4b01]!=0xf0 || (*main_ram)[0x4b02]!=0x32 || (*main_ram)[0x4b03]!=0x40) return 1;
    gpu_reset();memcpy(gpu_ram()+0x240,*main_ram+0x4b08,608);
    gpu_write(0xf0320c,base,0);gpu_write(0xf03210,index,0);gpu_write(0xf03214,destination,0);
    gpu_write(0xf02110,0xf03240,0);gpu_write(0xf02114,0x2801,0);
    for (steps=0;steps<2500000u && gpu_pc()!=0xf031beu;steps++) gpu_execute(1);
    GPU_calls+=steps;original_decode_calls++;
    return gpu_pc()!=0xf031beu;
}

static int sprite_command(void)
{
    uint32_t base=gpu_read(0xf0320c,0),index=gpu_read(0xf03210,0),destination=gpu_read(0xf03214,0);
    struct biwn_sprite_bus bus={lab_device_read8,lab_device_read16,lab_device_read32,lab_device_write16,lab_device_write32,NULL,1000000u};
    struct biwn_sprite_result result;
    int error;
    if (use_C_decoder) { C_decode_calls++;component=1;error=biwn_sprite_decode(&bus,base,index,destination,&result)!=BIWN_SPRITE_OK;component=0; }
    else error=original_sprite(base,index,destination);
    /* Explicit synchronous host mailbox model. Original overlay returns to
     * dispatcher; dispatcher acknowledgement/idle stores are modeled here. */
    if (!error) { gpu_write(0xf03204,0xffffffffu,0);gpu_write(0xf03200,0,0); }
    return error;
}

int lab_device_write32(void *unused,uint32_t address,uint32_t value)
{
    (void)unused;
    if (!opened || device_error) return 1;
    observe(1,4,address,value);
    if (address<=0x1ffffcu) {
        (*main_ram)[address]=(uint8_t)(value>>24);(*main_ram)[address+1]=(uint8_t)(value>>16);(*main_ram)[address+2]=(uint8_t)(value>>8);(*main_ram)[address+3]=(uint8_t)value;return 0;
    }
    if (address>=0xf02200u && address<=0xf0229cu) {
        if (address==0xf02238u) blit_calls++;
        blitter_write(address,value,6);return 0;
    }
    if (address==0xf0211cu) { gpu_write(address,value,0);return 0; }
    if (address>=0xf03200u && address<=0xf03ffcu) {
        gpu_write(address,value,0);
        if (address==0xf03204u) {
            if (value!=0x4b00u || sprite_command()) { device_error=1;return 1; }
        }
        return 0;
    }
    return 1;
}

int lab_device_run_C(uint32_t read_budget)
{
    struct biwn_inventory_pipeline_bus bus={lab_device_read8,lab_device_read16,lab_device_read32,lab_device_write32,NULL,read_budget};
    if (!opened || !use_C_decoder) return 1;
    return biwn_inventory_pipeline(&bus);
}

uint32_t lab_device_stat(unsigned field)
{
    switch (field) {
    case 0:return GPU_calls;
    case 1:return C_decode_calls;
    case 2:return original_decode_calls;
    case 3:return blit_calls;
    case 4:return config.current_frame;
    case 5:return (uint32_t)device_error;
    default:return 0xffffffffu;
    }
}
