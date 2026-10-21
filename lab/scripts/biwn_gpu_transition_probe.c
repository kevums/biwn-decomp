/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-owned observer: arm existing flight recorder after frame437,
 * disarm after439. No core or guest-state writes.
 */
#include "harness/harness.h"
#include "../tools/virtualjaguar-runtime-source/src/core/vjtrace.h"
#include <stdio.h>
#include <stdint.h>

static void (*arm_trace)(void), (*disarm_trace)(void);
static int (*add_watch)(uint32_t, uint32_t, unsigned);
static int (*snapshot)(const char *), (*dump_trace)(const char *);
static uint64_t (*ring_head)(void);
static int (*ring_read)(uint64_t, vjtrace_ev *);
static void (*backtrace)(int, uint32_t *, int, int *);
static uint32_t (*gpu_pc)(void), (*gpu_control)(void), (*gpu_flags)(void);
static uint32_t (*dsp_pc)(void);
static uint32_t *bank0, *bank1, *irq0, *irq3;
static unsigned int (*cpu_reg)(void *, int);
static FILE *frames, *registers;
static int failed;

static void capture(unsigned frame)
{
    unsigned b, i;
    uint32_t pcs[1024];
    int n, j;
    char name[80];
    FILE *history;
    snprintf(name, sizeof(name), "frame-%u.vjsn", frame);
    if (snapshot(name) != 0) failed = 1;
    for (b=0; b<2; b++) {
        fprintf(registers, "%u,%u,%06x,%08x,%08x,%u,%u", frame,b,
                gpu_pc(),gpu_control(),gpu_flags(),*irq0,*irq3);
        for (i=0;i<32;i++) fprintf(registers, ",%08x", b ? bank1[i] : bank0[i]);
        fprintf(registers, "\n");
    }
    snprintf(name,sizeof(name),"gpu-history-frame-%u.csv",frame);
    history=fopen(name,"w");
    if (!history) { failed=1; return; }
    fprintf(history,"index,pc\n");
    backtrace(3,pcs,1024,&n); /* GPU enum from pinned vjag_memory.h */
    for (j=0;j<n;j++) fprintf(history,"%d,%06x\n",j,pcs[j]);
    if (fclose(history)) failed=1;
}

static bool observe(void *unused, unsigned frame)
{
    (void)unused;
    fprintf(frames,"%u,%06x,%06x,%06x\n",frame,cpu_reg(NULL,16),gpu_pc(),dsp_pc());
    if (frame==437) {
        capture(frame);
        if (add_watch(0xf02100,0xf0211f,2)<0 ||
            add_watch(0xf03000,0xf0305f,2)<0 ||
            add_watch(0xf03800,0xf03803,2)<0) failed=1;
        arm_trace();
    } else if (frame==438) capture(frame);
    else if (frame==439) { capture(frame); disarm_trace(); }
    return !failed;
}

int main(int argc,char **argv)
{
    harness_config cfg=HARNESS_CONFIG_DEFAULT;
    FILE *events;
    uint64_t head,i;
    vjtrace_ev event;
    unsigned unreadable=0,j;
    cfg.frames=900;
    if (!harness_init_from_args(&cfg,argc,argv)) return 1;
    arm_trace=(void (*)(void))harness_dlsym(&cfg,"vjtrace_arm");
    disarm_trace=(void (*)(void))harness_dlsym(&cfg,"vjtrace_disarm");
    add_watch=(int (*)(uint32_t,uint32_t,unsigned))harness_dlsym(&cfg,"vjtrace_watch_add");
    snapshot=(int (*)(const char *))harness_dlsym(&cfg,"vjtrace_snapshot");
    dump_trace=(int (*)(const char *))harness_dlsym(&cfg,"vjtrace_dump");
    ring_head=(uint64_t (*)(void))harness_dlsym(&cfg,"vjtrace_ring_head");
    ring_read=(int (*)(uint64_t,vjtrace_ev *))harness_dlsym(&cfg,"vjtrace_ring_read");
    backtrace=(void (*)(int,uint32_t *,int,int *))harness_dlsym(&cfg,"vjtrace_backtrace");
    gpu_pc=(uint32_t (*)(void))harness_dlsym(&cfg,"GPUGetPC");
    dsp_pc=(uint32_t (*)(void))harness_dlsym(&cfg,"DSPGetPC");
    gpu_control=(uint32_t (*)(void))harness_dlsym(&cfg,"GPUGetControl");
    gpu_flags=(uint32_t (*)(void))harness_dlsym(&cfg,"GPUGetFlags");
    bank0=(uint32_t *)harness_dlsym(&cfg,"gpu_reg_bank_0");
    bank1=(uint32_t *)harness_dlsym(&cfg,"gpu_reg_bank_1");
    irq0=(uint32_t *)harness_dlsym(&cfg,"gpu_irq0_count");
    irq3=(uint32_t *)harness_dlsym(&cfg,"gpu_irq3_count");
    cpu_reg=(unsigned int (*)(void *,int))harness_dlsym(&cfg,"m68k_get_reg");
    if (!arm_trace || !disarm_trace || !add_watch || !snapshot || !dump_trace ||
        !ring_head || !ring_read || !backtrace || !gpu_pc || !dsp_pc ||
        !gpu_control || !gpu_flags || !bank0 || !bank1 || !irq0 || !irq3 || !cpu_reg) return 2;
    if (!cfg.rom_path || !harness_load_rom(&cfg)) return 3;
    frames=fopen("frame-pcs.csv","w");registers=fopen("gpu-register-banks.csv","w");
    if (!frames || !registers) return 4;
    fprintf(frames,"frame,cpu_pc,gpu_pc,dsp_pc\n");
    fprintf(registers,"frame,bank,gpu_pc,gpu_control,gpu_flags_raw,irq0_count,irq3_count");
    for (j=0;j<32;j++) fprintf(registers,",r%u",j);
    fprintf(registers,"\n");
    cfg.frame_callback=observe;
    harness_run(&cfg);
    disarm_trace();
    if (dump_trace("transition.vjtr") != 0) failed=1;
    events=fopen("events.csv","w");
    if (!events) return 5;
    fprintf(events,"seq,frame,halfline,type,who,pc,addr,value\n");
    head=ring_head();
    for (i=0;i<head;i++) {
        if (!ring_read(i,&event)) { unreadable++; continue; }
        fprintf(events,"%llu,%u,%u,%u,%u,%06x,%06x,%08x\n",
                (unsigned long long)event.seq,event.frame,event.halfline,event.type,
                event.who,event.pc,event.addr,event.value);
    }
    if (fclose(events) || fclose(frames) || fclose(registers)) failed=1;
    fprintf(stderr,"BIWN transition: %u frames; %llu events; %u unreadable\n",
            cfg.current_frame,(unsigned long long)head,unreadable);
    harness_shutdown(&cfg);
    return !failed && !unreadable && cfg.current_frame==cfg.frames ? 0 : 6;
}
