/* SPDX-License-Identifier: GPL-3.0-or-later
 * Replace checked57A0/6380 plus coordinator-generated material programs.
 * Seven C components run the observed draw chain; resident still experimental. */
#define lab_draw_hybrid lab_draw_setup57_only_hybrid
#include "biwn_setup57_integer_hybrid_bridge.c"
#undef lab_draw_hybrid
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_consumer6380.h"
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_material6460.h"
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_material6720.h"
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_material69a0.h"
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_resident.h"
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_dispatcher.h"
static uint32_t hybrid_dispatcher_calls,hybrid_dispatcher_PC_count;
static uint32_t Cdraw_GPU_attempts,Cdraw_commands[10000],Cdraw_command_count;
static void (*Cdraw_saved_execute)(int32_t);
static void Cdraw_forbidden_execute(int32_t cycles){(void)cycles;Cdraw_GPU_attempts++;}

static uint32_t hybrid_resident_calls,hybrid_resident_PC_count,hybrid_resident_blits;
static uint32_t hybrid_material_calls[3],hybrid_material_PC_count;
static int material_read8(void *unused,uint32_t a,uint8_t *v){return lab_device_read8(unused,a,v);}
static int material_write16(void *unused,uint32_t a,uint16_t v){return lab_device_write16(unused,a,v);}
static uint32_t hybrid_consumer_calls,hybrid_consumer_PC_count;
static int consumer_read16(void *unused,uint32_t a,uint16_t *v){return lab_device_read16(unused,a,v);}
static int hybrid_consumer(void)
{
    size_t (*save_state)(uint8_t *),(*load_state)(const uint8_t *);
    uint8_t raw[8192];size_t size;unsigned i;int status;
    struct biwn_gpu_consumer6380_state s;
    struct biwn_gpu_consumer6380_bus bus={consumer_read16,hybrid_read,hybrid_write,hybrid_observe,NULL};
    save_state=(size_t (*)(uint8_t *))harness_dlsym(&config,"GPUStateSave");
    load_state=(size_t (*)(const uint8_t *))harness_dlsym(&config,"GPUStateLoad");
    if(!save_state||!load_state)return 1;
    size=save_state(raw);if(size<=4396u||size>sizeof(raw)||raw[4395]!=0)return 2;
    memset(&s,0,sizeof(s));s.pc=gpu_pc();s.z=raw[4136];s.n=raw[4137];s.c=raw[4138];
    for(i=0;i<32;i++){s.registers[0][i]=movement_bank0[i];s.registers[1][i]=movement_bank1[i];}
    i=hybrid_count;status=biwn_gpu_consumer6380_run(&bus,&s,100000u);if(status)return status;
    hybrid_consumer_PC_count+=hybrid_count-i;
    if(save_state(raw)!=size)return 3;
    memcpy(raw+4096,&s.pc,4);raw[4136]=(uint8_t)s.z;raw[4137]=(uint8_t)s.n;raw[4138]=(uint8_t)s.c;
    memcpy(raw+4139,s.registers,sizeof(s.registers));
    if(load_state(raw)!=size)return 4;
    hybrid_consumer_calls++;return 0;
}
static int hybrid_material(uint32_t header)
{
    size_t (*save_state)(uint8_t *),(*load_state)(const uint8_t *);
    uint8_t raw[8192];size_t size;unsigned i,old_count=hybrid_count;int status;
    save_state=(size_t (*)(uint8_t *))harness_dlsym(&config,"GPUStateSave");
    load_state=(size_t (*)(const uint8_t *))harness_dlsym(&config,"GPUStateLoad");
    if(!save_state||!load_state)return 1;
    size=save_state(raw);if(size<=4396u||size>sizeof(raw)||raw[4395]!=0)return 2;
#define RUN_MATERIAL(name,index) do { \
    struct biwn_gpu_##name##_state s; \
    struct biwn_gpu_##name##_bus bus={material_read8,consumer_read16,hybrid_read,material_write16,hybrid_write,hybrid_observe,NULL}; \
    memset(&s,0,sizeof(s));s.pc=gpu_pc();s.z=raw[4136];s.n=raw[4137];s.c=raw[4138]; \
    for(i=0;i<32;i++){s.registers[0][i]=movement_bank0[i];s.registers[1][i]=movement_bank1[i];} \
    status=biwn_gpu_##name##_run(&bus,&s,1000000u);if(status)return status; \
    if(save_state(raw)!=size)return 3; \
    memcpy(raw+4096,&s.pc,4);raw[4136]=(uint8_t)s.z;raw[4137]=(uint8_t)s.n;raw[4138]=(uint8_t)s.c; \
    memcpy(raw+4139,s.registers,sizeof(s.registers)); \
    if(load_state(raw)!=size)return 4;hybrid_material_calls[index]++; \
}while(0)
    if(header==0x6460u){RUN_MATERIAL(material6460,0);}
    else if(header==0x6720u){RUN_MATERIAL(material6720,1);}
    else if(header==0x69a0u){RUN_MATERIAL(material69a0,2);}
    else return 5;
#undef RUN_MATERIAL
    hybrid_material_PC_count+=hybrid_count-old_count;return 0;
}
static int resident_blitter_write(void *unused,uint32_t a,uint32_t v,uint8_t *local_RAM)
{
    int status;memcpy(gpu_ram(),local_RAM,4096);status=lab_device_write32(unused,a,v);
    memcpy(local_RAM,gpu_ram(),4096);hybrid_resident_blits++;return status;
}
static int hybrid_resident(void)
{
    size_t (*save_state)(uint8_t *),(*load_state)(const uint8_t *);
    uint8_t raw[8192];size_t size;unsigned i,old_count=hybrid_count;int status;
    struct biwn_gpu_resident_state s;
    struct biwn_gpu_resident_bus bus={consumer_read16,hybrid_read,hybrid_write,resident_blitter_write,hybrid_observe,NULL};
    save_state=(size_t (*)(uint8_t *))harness_dlsym(&config,"GPUStateSave");
    load_state=(size_t (*)(const uint8_t *))harness_dlsym(&config,"GPUStateLoad");
    if(!save_state||!load_state)return 1;
    size=save_state(raw);if(size<=4396u||size>sizeof(raw)||raw[4395]!=0)return 2;
    memset(&s,0,sizeof(s));s.pc=gpu_pc();s.z=raw[4136];s.n=raw[4137];s.c=raw[4138];
    for(i=0;i<32;i++){s.registers[0][i]=movement_bank0[i];s.registers[1][i]=movement_bank1[i];}
    memcpy(&s.accumulator,raw+4100,4);memcpy(&s.remainder,raw+4104,4);
    memcpy(&s.matrix_control,raw+4116,4);memcpy(&s.matrix_pointer,raw+4120,4);memcpy(&s.division_control,raw+4132,4);memcpy(s.local_RAM,raw,4096);
    status=biwn_gpu_resident_run(&bus,&s,1000000u);if(status)return status;
    if(save_state(raw)!=size)return 3;
    memcpy(raw,s.local_RAM,4096);memcpy(raw+4096,&s.pc,4);memcpy(raw+4100,&s.accumulator,4);memcpy(raw+4104,&s.remainder,4);
    memcpy(raw+4116,&s.matrix_control,4);memcpy(raw+4120,&s.matrix_pointer,4);memcpy(raw+4132,&s.division_control,4);
    raw[4136]=(uint8_t)s.z;raw[4137]=(uint8_t)s.n;raw[4138]=(uint8_t)s.c;memcpy(raw+4139,s.registers,sizeof(s.registers));
    if(load_state(raw)!=size)return 4;
    hybrid_resident_calls++;hybrid_resident_PC_count+=hybrid_count-old_count;return 0;
}
static void dispatcher_observe(void *context,uint32_t pc,uint32_t z,uint32_t carry,uint32_t n){(void)z;(void)carry;(void)n;hybrid_observe(context,pc);}
static int hybrid_dispatcher(void)
{
    size_t (*save_state)(uint8_t *),(*load_state)(const uint8_t *);
    uint8_t raw[8192];size_t size;unsigned i,old_count=hybrid_count;int status;
    struct biwn_gpu_dispatcher_state s;
    struct biwn_gpu_dispatcher_bus bus={hybrid_read,hybrid_write,dispatcher_observe,NULL};
    save_state=(size_t (*)(uint8_t *))harness_dlsym(&config,"GPUStateSave");
    load_state=(size_t (*)(const uint8_t *))harness_dlsym(&config,"GPUStateLoad");
    if(!save_state||!load_state)return 1;
    size=save_state(raw);if(size<=4396u||size>sizeof(raw)||raw[4395]!=0)return 2;
    memset(&s,0,sizeof(s));s.pc=gpu_pc();s.z=raw[4136];s.n=raw[4137];s.c=raw[4138];
    for(i=0;i<32;i++){s.registers[0][i]=movement_bank0[i];s.registers[1][i]=movement_bank1[i];}
    {uint32_t command=gpu_read(0xf03204,0);if(command!=0xffffffffu){if(Cdraw_command_count>=10000u)return 6;Cdraw_commands[Cdraw_command_count++]=command;}}
    status=biwn_gpu_dispatcher_run(&bus,&s,100000u,1u);if(status)return status;
    if(save_state(raw)!=size)return 3;
    memcpy(raw+4096,&s.pc,4);raw[4136]=(uint8_t)s.z;raw[4137]=(uint8_t)s.n;raw[4138]=(uint8_t)s.c;memcpy(raw+4139,s.registers,sizeof(s.registers));
    if(load_state(raw)!=size)return 4;
    hybrid_dispatcher_calls++;hybrid_dispatcher_PC_count+=hybrid_count-old_count;return 0;
}
int lab_draw_hybrid(void)
{
    if(!opened||!movement_arm)return 1;
    Cdraw_GPU_attempts=Cdraw_command_count=0;Cdraw_saved_execute=gpu_execute;gpu_execute=Cdraw_forbidden_execute;
#define DRAW_RETURN(v) do{gpu_execute=Cdraw_saved_execute;return(v);}while(0)
    memcpy(gpu_ram(),*main_ram+0x40a8,512);
    gpu_write(0xf03208,0x52e0,0);gpu_write(0xf03204,0x57a0,0);
    gpu_write(0xf02110,0xf031be,0);gpu_write(0xf02114,0x2801,0);
    hybrid_count=hybrid_native_steps=hybrid_setup_calls=0;
    hybrid_consumer_calls=hybrid_consumer_PC_count=hybrid_material_PC_count=0;hybrid_resident_calls=hybrid_resident_PC_count=hybrid_resident_blits=0;hybrid_dispatcher_calls=hybrid_dispatcher_PC_count=0;memset(hybrid_material_calls,0,sizeof(hybrid_material_calls));
    while(hybrid_count<5000000u){
        uint32_t pc=gpu_pc(),header=gpu_read(0xf03208,0);
        if(pc==0xf031ceu&&gpu_read(0xf03204,0)==0xffffffffu&&gpu_read(0xf03200,0)==0)break;
        if(pc==0xf03240u&&header==0x57a0u){int status=hybrid_setup();if(status)DRAW_RETURN(10+status);}
        else if(pc==0xf03240u&&header==0x6380u){int status=hybrid_consumer();if(status)DRAW_RETURN(20+status);}
        else if(pc==0xf03240u&&(header==0x6460u||header==0x6720u||header==0x69a0u)){int status=hybrid_material(header);if(status)DRAW_RETURN(30+status);}
        else if(pc==0xf03440u||pc==0xf03ca0u){int status=hybrid_resident();if(status)DRAW_RETURN(40+status);}
        else if(pc>=0xf031beu&&pc<0xf03200u){int status=hybrid_dispatcher();if(status)DRAW_RETURN(50+status);}
        else DRAW_RETURN(60);
    }
    GPU_calls+=hybrid_native_steps;if(Cdraw_GPU_attempts)DRAW_RETURN(61);DRAW_RETURN(hybrid_count<5000000u?0:3);
#undef DRAW_RETURN
}
uint32_t lab_hybrid_consumer_calls(void){return hybrid_consumer_calls;}
uint32_t lab_hybrid_consumer_PC_count(void){return hybrid_consumer_PC_count;}

uint32_t lab_hybrid_material_calls(unsigned i){return i<3?hybrid_material_calls[i]:0;}
uint32_t lab_hybrid_material_PC_count(void){return hybrid_material_PC_count;}

uint32_t lab_hybrid_resident_calls(void){return hybrid_resident_calls;}
uint32_t lab_hybrid_resident_PC_count(void){return hybrid_resident_PC_count;}
uint32_t lab_hybrid_resident_blits(void){return hybrid_resident_blits;}

uint32_t lab_hybrid_dispatcher_calls(void){return hybrid_dispatcher_calls;}
uint32_t lab_hybrid_dispatcher_PC_count(void){return hybrid_dispatcher_PC_count;}

uint32_t lab_C_draw_GPU_attempts(void){return Cdraw_GPU_attempts;}
uint32_t lab_C_draw_command_count(void){return Cdraw_command_count;}
uint32_t lab_C_draw_command(unsigned i){return i<Cdraw_command_count?Cdraw_commands[i]:0;}
