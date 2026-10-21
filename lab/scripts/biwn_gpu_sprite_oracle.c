/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-owned isolated execution of preserved GPU4B00overlay. No core edits,
 * CPU/DSP/frame execution or assertion of physical hardware accuracy. */
#include "harness/harness.h"
#include "../tools/virtualjaguar-runtime-source/src/core/vjtrace.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc,char **argv)
{
    harness_config cfg=HARNESS_CONFIG_DEFAULT;
    uint8_t **main_ram,*gpu_ram;
    uint8_t *(*get_gpu_ram)(void);
    uint32_t *bank0,*bank1;
    void (*reset)(void),(*execute)(int32_t),(*arm)(void),(*disarm)(void);
    void (*gpu_write)(uint32_t,uint32_t,uint32_t);
    uint32_t (*pc)(void),(*gpu_read)(uint32_t,uint32_t);
    int (*watch)(uint32_t,uint32_t,unsigned),(*ring_read)(uint64_t,vjtrace_ev *);
    uint64_t (*head)(void);
    uint32_t base,index,dest,seed,word,destination,count,i,steps;
    uint64_t begin,end,seq;
    unsigned unreadable=0,records=0;
    FILE *file;
    vjtrace_ev event;
    int done;
    if (argc!=10) return 10;
    cfg.core_path=argv[1];cfg.system_dir=argv[9];cfg.quiet=1;
    if (!harness_load_core(&cfg) || !harness_load_no_content(&cfg)) return 11;
#define RESOLVE(variable,type,symbol) variable=(type)harness_dlsym(&cfg,symbol);if (!variable) return 12
    RESOLVE(main_ram,uint8_t **,"jaguarMainRAM");
    RESOLVE(get_gpu_ram,uint8_t *(*)(void),"GPUGetRAM");
    RESOLVE(bank0,uint32_t *,"gpu_reg_bank_0");RESOLVE(bank1,uint32_t *,"gpu_reg_bank_1");
    RESOLVE(reset,void (*)(void),"GPUReset");RESOLVE(execute,void (*)(int32_t),"GPUExec");
    RESOLVE(gpu_write,void (*)(uint32_t,uint32_t,uint32_t),"GPUWriteLong");
    RESOLVE(gpu_read,uint32_t (*)(uint32_t,uint32_t),"GPUReadLong");RESOLVE(pc,uint32_t (*)(void),"GPUGetPC");
    RESOLVE(arm,void (*)(void),"vjtrace_arm");RESOLVE(disarm,void (*)(void),"vjtrace_disarm");
    RESOLVE(watch,int (*)(uint32_t,uint32_t,unsigned),"vjtrace_watch_add");
    RESOLVE(head,uint64_t (*)(void),"vjtrace_ring_head");RESOLVE(ring_read,int (*)(uint64_t,vjtrace_ev *),"vjtrace_ring_read");
#undef RESOLVE
    reset();gpu_ram=get_gpu_ram();
    file=fopen(argv[2],"rb");if (!file) return 13;
    if (fread(*main_ram,1,0x200000,file)!=0x200000 || fgetc(file)!=EOF || fclose(file)) return 14;
    base=(uint32_t)strtoul(argv[5],NULL,0);index=(uint32_t)strtoul(argv[6],NULL,0);dest=(uint32_t)strtoul(argv[7],NULL,0);seed=(uint32_t)strtoul(argv[8],NULL,0);
    destination=0;count=0;
    for (i=0;i<4;i++) { destination=(destination<<8)|(*main_ram)[0x4b00+i];count=(count<<8)|(*main_ram)[0x4b04+i]; }
    if (destination!=0xf03240 || count!=152) return 15;
    memcpy(gpu_ram+0x240,*main_ram+0x4b08,count*4);
    for (i=0;i<32;i++) { seed=1664525u*seed+1013904223u;bank0[i]=seed;bank1[i]=~seed; }
    gpu_write(0xf0320c,base,0);gpu_write(0xf03210,index,0);gpu_write(0xf03214,dest,0);
    gpu_write(0xf0211c,0xa5a50001u,0); /* completion store must clear sentinel */
    gpu_write(0xf02110,destination,0);gpu_write(0xf02114,0x2801,0);
    if (watch(0,0x1fffff,3)<0 || watch(0xf0211c,0xf0211f,2)<0) return 16;
    begin=head();arm();
    for (steps=0;steps<2500000 && pc()!=0xf031be;steps++) execute(1);
    disarm();end=head();done=pc()==0xf031be;
    file=fopen(argv[4],"w");if (!file) return 17;
    fprintf(file,"seq,type,who,pc,addr,value\n");
    for (seq=begin;seq<end;seq++) {
        if (!ring_read(seq,&event)) { unreadable++;continue; }
        if (event.type!=VJT_EV_WATCH_RD && event.type!=VJT_EV_WATCH_WR) continue;
        records++;
        fprintf(file,"%llu,%u,%u,%06x,%06x,%08x\n",(unsigned long long)event.seq,event.type,event.who,event.pc,event.addr,event.value);
    }
    if (fclose(file)) return 18;
    file=fopen(argv[3],"wb");if (!file || fwrite(*main_ram,1,0x200000,file)!=0x200000 || fclose(file)) return 19;
    word=gpu_read(0xf0211c,0);
    printf("{\"returned_to_dispatcher\":%s,\"PC\":%u,\"GPUExec1_calls\":%u,\"unreadable\":%u,\"watch_records\":%u,\"division_control\":%u,\"CPU_frames_executed\":%u,\"bank0\":[",done?"true":"false",pc(),steps,unreadable,records,word,cfg.current_frame);
    for (i=0;i<32;i++) printf("%s%u",i?",":"",bank0[i]);
    printf("]}\n");
    harness_shutdown(&cfg);
    return done && !unreadable && !cfg.current_frame ? 0 : 20;
}
