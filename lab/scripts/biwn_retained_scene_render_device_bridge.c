/* SPDX-License-Identifier: GPL-3.0-or-later
 * Scene CPU submissions drive native or C projection/dispatch/draw.
 * Explicit retained-context experiment: geometry keeps the incoming GPU
 * state and source dispatcher loads its overlay. No per-entry reset/seed.
 */
#include "biwn_C_draw_bridge.c"
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_projection.h"
static uint8_t scene_geometry_RAM[4096];
static unsigned scene_geometry_RAM_ready;
static uint64_t scene_render_stats[12],scene_PC_hash;
static uint32_t scene_last_error;
static uint8_t scene_resident_seen[1350];
/* Select implementations without changing any device/CPU/GPU state. */
int lab_retained_renderer_mode(unsigned use_C)
{if(!opened||use_C>1u)return 1;use_C_decoder=(int)use_C;return 0;}
int lab_scene_render_GPU_RAM(const uint8_t *ram,unsigned bytes)
{if(!ram||bytes!=4096u)return 1;memcpy(scene_geometry_RAM,ram,4096);scene_geometry_RAM_ready=1;return 0;}
void lab_scene_render_reset(void)
{memset(scene_render_stats,0,sizeof(scene_render_stats));memset(scene_resident_seen,0,sizeof(scene_resident_seen));scene_last_error=0;}
uint64_t lab_scene_render_stat(unsigned i){return i<12?scene_render_stats[i]:0;}
uint64_t lab_scene_render_PC_hash(void){return scene_PC_hash;}
uint32_t lab_scene_render_error(void){return scene_last_error;}
uint32_t lab_scene_resident_seen(uint32_t pc)
{return pc>=0xf03440u&&pc<0xf03ecau?scene_resident_seen[(pc-0xf03440u)/2u]:0;}
static void scene_mark_resident(uint32_t pc)
{
    uint32_t offset,word;
    if(pc<0xf03440u||pc>=0xf03ecau)return;
    offset=pc-0xf03440u;scene_resident_seen[offset/2u]=1;
    word=((uint32_t)(*main_ram)[0x58a8u+offset]<<8)|(*main_ram)[0x58a9u+offset];
    if((word>>10)==52u||(word>>10)==53u)scene_resident_seen[offset/2u+1u]=1;
}
static int scene_geometry_prepare(const uint32_t *args)
{(void)args;return 0;}
static int scene_C_geometry(void)
{
    size_t (*save_state)(uint8_t *),(*load_state)(const uint8_t *);
    uint8_t raw[8192];size_t size;unsigned i;int status;
    struct biwn_gpu_geometry_state s;
    struct biwn_gpu_geometry_bus bus={consumer_read16,hybrid_read,material_write16,hybrid_write,hybrid_observe,NULL};
    save_state=(size_t (*)(uint8_t *))harness_dlsym(&config,"GPUStateSave");load_state=(size_t (*)(const uint8_t *))harness_dlsym(&config,"GPUStateLoad");if(!save_state||!load_state)return 1;
    size=save_state(raw);if(size<=4396u||size>sizeof(raw)||raw[4395])return 2;
    memset(&s,0,sizeof(s));s.pc=gpu_pc();s.z=raw[4136];s.n=raw[4137];s.c=raw[4138];
    for(i=0;i<32;i++){s.registers[0][i]=movement_bank0[i];s.registers[1][i]=movement_bank1[i];}
    memcpy(&s.remainder,raw+4104,4);memcpy(&s.matrix_control,raw+4116,4);memcpy(&s.matrix_pointer,raw+4120,4);memcpy(&s.division_control,raw+4132,4);memcpy(s.local_RAM,raw,4096);
    component=3;status=biwn_gpu_geometry_run(&bus,&s,100000u);component=0;if(status)return status;
    if(save_state(raw)!=size)return 3;
    memcpy(raw,s.local_RAM,4096);memcpy(raw+4096,&s.pc,4);memcpy(raw+4104,&s.remainder,4);memcpy(raw+4116,&s.matrix_control,4);memcpy(raw+4120,&s.matrix_pointer,4);memcpy(raw+4132,&s.division_control,4);
    raw[4136]=(uint8_t)s.z;raw[4137]=(uint8_t)s.n;raw[4138]=(uint8_t)s.c;memcpy(raw+4139,s.registers,sizeof(s.registers));
    return load_state(raw)==size?0:4;
}
static int scene_C_projection(void)
{
    size_t (*save_state)(uint8_t *),(*load_state)(const uint8_t *);
    uint8_t raw[8192];size_t size;unsigned i;int status;
    struct biwn_gpu_projection_state s;
    struct biwn_gpu_projection_bus bus={consumer_read16,hybrid_read,material_write16,hybrid_write,hybrid_observe,NULL};
    save_state=(size_t (*)(uint8_t *))harness_dlsym(&config,"GPUStateSave");load_state=(size_t (*)(const uint8_t *))harness_dlsym(&config,"GPUStateLoad");if(!save_state||!load_state)return 1;
    size=save_state(raw);if(size<=4396u||size>sizeof(raw)||raw[4395])return 2;
    memset(&s,0,sizeof(s));s.pc=gpu_pc();s.z=raw[4136];s.n=raw[4137];s.c=raw[4138];
    for(i=0;i<32;i++){s.registers[0][i]=movement_bank0[i];s.registers[1][i]=movement_bank1[i];}
    memcpy(&s.accumulator,raw+4100,4);memcpy(&s.remainder,raw+4104,4);memcpy(&s.matrix_control,raw+4116,4);memcpy(&s.matrix_pointer,raw+4120,4);memcpy(&s.division_control,raw+4132,4);memcpy(s.local_RAM,raw,4096);
    status=biwn_gpu_projection_run(&bus,&s,1000000u);if(status)return status;
    if(save_state(raw)!=size)return 3;
    memcpy(raw,s.local_RAM,4096);memcpy(raw+4096,&s.pc,4);memcpy(raw+4100,&s.accumulator,4);memcpy(raw+4104,&s.remainder,4);memcpy(raw+4116,&s.matrix_control,4);memcpy(raw+4120,&s.matrix_pointer,4);memcpy(raw+4132,&s.division_control,4);
    raw[4136]=(uint8_t)s.z;raw[4137]=(uint8_t)s.n;raw[4138]=(uint8_t)s.c;memcpy(raw+4139,s.registers,sizeof(s.registers));
    return load_state(raw)==size?0:4;
}
int lab_scene_render_submit(void *unused,uint32_t address,uint32_t value)
{
    uint32_t args[4],i,native_steps=0;int status=0;
    void (*saved_execute)(int32_t)=gpu_execute;
    if(address!=0xf03204u||(value!=0x4d80u&&value!=0x52e0u&&value!=0x57a0u))return lab_movement_write32(unused,address,value);
    if(!opened||!movement_arm)return 1;
    observe(1,4,address,value);gpu_write(address,value,0);scene_render_stats[0]++;
    hybrid_count=hybrid_native_steps=hybrid_setup_calls=hybrid_consumer_calls=hybrid_consumer_PC_count=hybrid_material_PC_count=hybrid_resident_calls=hybrid_resident_PC_count=hybrid_resident_blits=hybrid_dispatcher_calls=hybrid_dispatcher_PC_count=0;memset(hybrid_material_calls,0,sizeof(hybrid_material_calls));Cdraw_GPU_attempts=Cdraw_command_count=0;
    if(value==0x4d80u){
        for(i=0;i<4;i++)args[i]=gpu_read(0xf0320cu+4u*i,0);
        status=scene_geometry_prepare(args);if(status)goto done;scene_render_stats[1]++;
        if(use_C_decoder)render_geometry_C_calls++;else render_geometry_original_calls++;
    }else if(value==0x52e0u)scene_render_stats[2]++;else scene_render_stats[3]++;
    if(use_C_decoder)gpu_execute=Cdraw_forbidden_execute;
    while(hybrid_count<5000000u){
        uint32_t pc=gpu_pc(),header=gpu_read(0xf03208,0),old_count=hybrid_count;
        if(pc==0xf031ceu&&gpu_read(0xf03204,0)==0xffffffffu&&gpu_read(0xf03200,0)==0)break;
        if(!use_C_decoder){
            hybrid_pcs[hybrid_count++]=pc;
            if(header!=0x4d80u&&header!=0x52e0u)scene_mark_resident(pc);
            gpu_execute(1);native_steps++;continue;
        }
        if(pc>=0xf031beu&&pc<0xf03200u)status=hybrid_dispatcher();
        else if(pc==0xf03240u&&header==0x4d80u){status=scene_C_geometry();scene_render_stats[7]++;}
        else if(pc==0xf03240u&&header==0x52e0u){status=scene_C_projection();scene_render_stats[6]++;}
        else if(pc==0xf03240u&&header==0x57a0u)status=hybrid_setup();
        else if(pc==0xf03240u&&header==0x6380u)status=hybrid_consumer();
        else if(pc==0xf03240u&&(header==0x6460u||header==0x6720u||header==0x69a0u))status=hybrid_material(header);
        else if(pc==0xf03440u||pc==0xf03ca0u){status=hybrid_resident();for(i=old_count;i<hybrid_count;i++)scene_mark_resident(hybrid_pcs[i]);}
        else status=60;
        if(status)break;
    }
    if(hybrid_count>=5000000u)status=61;
    scene_PC_hash=1469598103934665603ull;for(i=0;i<hybrid_count;i++){scene_PC_hash^=hybrid_pcs[i];scene_PC_hash*=1099511628211ull;}
    GPU_calls+=native_steps;scene_render_stats[4]+=native_steps;scene_render_stats[5]+=hybrid_dispatcher_calls;scene_render_stats[8]+=Cdraw_GPU_attempts;scene_render_stats[9]=hybrid_count;scene_render_stats[10]+=hybrid_resident_calls;scene_render_stats[11]+=hybrid_resident_blits;
    if(Cdraw_GPU_attempts)status=62;
done:
    gpu_execute=saved_execute;scene_last_error=(uint32_t)status;if(status)device_error=1;return status;
}
