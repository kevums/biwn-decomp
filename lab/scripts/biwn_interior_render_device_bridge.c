/* SPDX-License-Identifier: GPL-3.0-or-later
 * Interior GPU chain extension. Mode1 bridge/source artifacts stay unchanged.
 * Per6AE0 entry reset fixture remains declared; later programs inherit state.
 */
#define lab_scene_render_submit lab_scene_render_submit_mode1
#define lab_scene_render_reset lab_scene_render_reset_mode1
#include "biwn_scene_render_device_bridge.c"
#undef lab_scene_render_submit
#undef lab_scene_render_reset
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_interior6ae0.h"
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_interior6da0.h"
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_room_consumer6e80.h"
static uint64_t interior_render_stats[4];
void lab_scene_render_reset(void)
{lab_scene_render_reset_mode1();memset(interior_render_stats,0,sizeof(interior_render_stats));}
uint64_t lab_interior_render_stat(unsigned i){return i<4?interior_render_stats[i]:0;}
static int interior_geometry_prepare(const uint32_t *args)
{
    uint32_t i,seed=0x6ae00000u;
    if(!scene_geometry_RAM_ready)return 1;
    gpu_reset();memcpy(gpu_ram(),scene_geometry_RAM,4096);
    memcpy(gpu_ram(),*main_ram+0x40a8,512);memcpy(gpu_ram()+0x240,*main_ram+0x6ae8,696);
    for(i=0;i<32;i++){seed=1664525u*seed+1013904223u;movement_bank0[i]=seed;movement_bank1[i]=~seed;}
    for(i=0;i<5;i++)gpu_write(0xf0320cu+i*4u,args[i],0);
    gpu_write(0xf03200,0xffffffffu,0);gpu_write(0xf03204,0xffffffffu,0);gpu_write(0xf03208,0x6ae0u,0);
    gpu_write(0xf0211c,0,0);gpu_write(0xf02110,0xf03240,0);gpu_write(0xf02114,0x2801,0);interior_render_stats[2]++;return 0;
}
#define INTERIOR_HANDLER(name) \
static int scene_C_##name(void) \
{ \
    size_t (*save_state)(uint8_t *),(*load_state)(const uint8_t *); \
    uint8_t raw[8192];size_t size;unsigned i;int status; \
    struct biwn_gpu_##name##_state s; \
    struct biwn_gpu_##name##_bus bus={consumer_read16,hybrid_read,material_write16,hybrid_write,hybrid_observe,NULL}; \
    save_state=(size_t (*)(uint8_t *))harness_dlsym(&config,"GPUStateSave");load_state=(size_t (*)(const uint8_t *))harness_dlsym(&config,"GPUStateLoad");if(!save_state||!load_state)return 1; \
    size=save_state(raw);if(size<=4396u||size>sizeof(raw)||raw[4395])return 2; \
    memset(&s,0,sizeof(s));s.pc=gpu_pc();s.z=raw[4136];s.n=raw[4137];s.c=raw[4138]; \
    for(i=0;i<32;i++){s.registers[0][i]=movement_bank0[i];s.registers[1][i]=movement_bank1[i];} \
    memcpy(&s.remainder,raw+4104,4);memcpy(&s.matrix_control,raw+4116,4);memcpy(&s.matrix_pointer,raw+4120,4);memcpy(&s.division_control,raw+4132,4);memcpy(s.local_RAM,raw,4096); \
    status=biwn_gpu_##name##_run(&bus,&s,200000u);if(status)return status; \
    if(save_state(raw)!=size)return 3; \
    memcpy(raw,s.local_RAM,4096);memcpy(raw+4096,&s.pc,4);memcpy(raw+4104,&s.remainder,4);memcpy(raw+4116,&s.matrix_control,4);memcpy(raw+4120,&s.matrix_pointer,4);memcpy(raw+4132,&s.division_control,4); \
    raw[4136]=(uint8_t)s.z;raw[4137]=(uint8_t)s.n;raw[4138]=(uint8_t)s.c;memcpy(raw+4139,s.registers,sizeof(s.registers)); \
    return load_state(raw)==size?0:4; \
}
INTERIOR_HANDLER(interior6ae0)
INTERIOR_HANDLER(interior6da0)
INTERIOR_HANDLER(room_consumer6e80)
int lab_scene_render_submit(void *unused,uint32_t address,uint32_t value)
{
    uint32_t args[5],i,native_steps=0;int status=0;
    void (*saved_execute)(int32_t)=gpu_execute;
    if(address!=0xf03204u||(value!=0x6ae0u&&value!=0x6da0u&&value!=0x57a0u))return lab_scene_render_submit_mode1(unused,address,value);
    if(!opened||!movement_arm)return 1;
    observe(1,4,address,value);gpu_write(address,value,0);scene_render_stats[0]++;
    hybrid_count=hybrid_native_steps=hybrid_setup_calls=hybrid_consumer_calls=hybrid_consumer_PC_count=hybrid_material_PC_count=hybrid_resident_calls=hybrid_resident_PC_count=hybrid_resident_blits=hybrid_dispatcher_calls=hybrid_dispatcher_PC_count=0;memset(hybrid_material_calls,0,sizeof(hybrid_material_calls));Cdraw_GPU_attempts=Cdraw_command_count=0;
    if(value==0x6ae0u){
        for(i=0;i<5;i++)args[i]=gpu_read(0xf0320cu+4u*i,0);
        status=interior_geometry_prepare(args);if(status)goto done;
    }
    if(value==0x57a0u)scene_render_stats[3]++;
    if(use_C_decoder)gpu_execute=Cdraw_forbidden_execute;
    while(hybrid_count<5000000u){
        uint32_t pc=gpu_pc(),header=gpu_read(0xf03208,0),old_count=hybrid_count;
        if(pc==0xf031ceu&&gpu_read(0xf03204,0)==0xffffffffu&&gpu_read(0xf03200,0)==0)break;
        if(!use_C_decoder){hybrid_pcs[hybrid_count++]=pc;if(header!=0x6ae0u&&header!=0x6da0u)scene_mark_resident(pc);gpu_execute(1);native_steps++;continue;}
        if(pc>=0xf031beu&&pc<0xf03200u)status=hybrid_dispatcher();
        else if(pc==0xf03240u&&header==0x6ae0u){status=scene_C_interior6ae0();interior_render_stats[0]++;}
        else if(pc==0xf03240u&&header==0x6da0u){status=scene_C_interior6da0();interior_render_stats[1]++;}
        else if(pc==0xf03240u&&header==0x6e80u){status=scene_C_room_consumer6e80();interior_render_stats[3]++;}
        else if(pc==0xf03240u&&header==0x57a0u)status=hybrid_setup();
        else if(pc==0xf03240u&&header==0x6380u)status=hybrid_consumer();
        else if(pc==0xf03240u&&(header==0x6460u||header==0x6720u||header==0x69a0u))status=hybrid_material(header);
        else if(pc==0xf03440u||pc==0xf03ca0u){status=hybrid_resident();for(i=old_count;i<hybrid_count;i++)scene_mark_resident(hybrid_pcs[i]);}
        else status=70;
        if(status)break;
    }
    if(hybrid_count>=5000000u)status=71;
    scene_PC_hash=1469598103934665603ull;for(i=0;i<hybrid_count;i++){scene_PC_hash^=hybrid_pcs[i];scene_PC_hash*=1099511628211ull;}
    GPU_calls+=native_steps;scene_render_stats[4]+=native_steps;scene_render_stats[5]+=hybrid_dispatcher_calls;scene_render_stats[8]+=Cdraw_GPU_attempts;scene_render_stats[9]=hybrid_count;scene_render_stats[10]+=hybrid_resident_calls;scene_render_stats[11]+=hybrid_resident_blits;
    if(Cdraw_GPU_attempts)status=72;
done:
    gpu_execute=saved_execute;scene_last_error=(uint32_t)status;if(status)device_error=1;return status;
}
