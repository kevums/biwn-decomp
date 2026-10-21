/* SPDX-License-Identifier: GPL-3.0-or-later
 * Replace checked57A0 and6380 with local-model C in the original draw chain.
 * Dispatcher and remaining material/resident programs still execute original. */
#define lab_draw_hybrid lab_draw_setup57_only_hybrid
#include "biwn_setup57_integer_hybrid_bridge.c"
#undef lab_draw_hybrid
#include "../projects/black-ice-white-noise/restoration/biwn_gpu_consumer6380.h"
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
int lab_draw_hybrid(void)
{
    if(!opened||!movement_arm)return 1;
    memcpy(gpu_ram(),*main_ram+0x40a8,512);
    gpu_write(0xf03208,0x52e0,0);gpu_write(0xf03204,0x57a0,0);
    gpu_write(0xf02110,0xf031be,0);gpu_write(0xf02114,0x2801,0);
    hybrid_count=hybrid_native_steps=hybrid_setup_calls=0;
    hybrid_consumer_calls=hybrid_consumer_PC_count=0;
    while(hybrid_count<5000000u){
        uint32_t pc=gpu_pc(),header=gpu_read(0xf03208,0);
        if(pc==0xf031ceu&&gpu_read(0xf03204,0)==0xffffffffu&&gpu_read(0xf03200,0)==0)break;
        if(pc==0xf03240u&&header==0x57a0u){int status=hybrid_setup();if(status)return 10+status;}
        else if(pc==0xf03240u&&header==0x6380u){int status=hybrid_consumer();if(status)return 20+status;}
        else{hybrid_pcs[hybrid_count++]=pc;gpu_execute(1);hybrid_native_steps++;}
    }
    GPU_calls+=hybrid_native_steps;return hybrid_count<5000000u?0:3;
}
uint32_t lab_hybrid_consumer_calls(void){return hybrid_consumer_calls;}
uint32_t lab_hybrid_consumer_PC_count(void){return hybrid_consumer_PC_count;}
