/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-owned streaming DSP/audio/gameplay observer derived from biwn_audio_command_probe.c. Optional existing GPU-stack experiment
 * repeats exactly one guest write after frame437; no DSP or core modifications.
 */
#include "harness/harness.h"
#include "../tools/virtualjaguar-runtime-source/src/core/vjtrace.h"
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint32_t (*gpu_pc)(void), (*dsp_pc)(void), (*dsp_control)(void);
static uint32_t (*i2s_count)(void), (*i2s_nonzero)(void);
static unsigned int (*cpu_reg)(void *, int);
static uint8_t *(*dsp_ram)(void);
static uint32_t *dsp_bank0, *dsp_bank1, *gpu_bank0;
static uint32_t (*dsp_flags)(void);
static uint16_t **left, **right;
static uint8_t **clock_divider;
static uint32_t **serial_mode;
static void (*arm_trace)(void), (*disarm_trace)(void);
static int (*watch)(uint32_t, uint32_t, unsigned);
static uint64_t (*ring_head)(void);
static int (*ring_read)(uint64_t, vjtrace_ev *);
static void (*backtrace)(int, uint32_t *, int, int *);
static FILE *frames, *banks, *history, *ram, *commands;
static uint8_t **main_ram;
static uint32_t be32(const uint8_t *p) { return ((uint32_t)p[0]<<24)|((uint32_t)p[1]<<16)|((uint32_t)p[2]<<8)|p[3]; }
static int initialize_stack, initialization_count, failed;
static FILE *events;
static uint64_t cursor, watched, max_frame_events;
static unsigned unreadable;
static uint32_t *cpu_queue, *cpu_queue_pointer;
typedef struct {
    unsigned first_frame, last_frame, observations, bytes_changed;
    uint8_t first_bytes[16];
} observed_cpu_pc;
static observed_cpu_pc cpu_seen[0x80000];

static void drain_events(void)
{
    uint64_t head=ring_head(), i;
    vjtrace_ev event;
    if (head<cursor) { failed=1; return; }
    if (head-cursor>max_frame_events) max_frame_events=head-cursor;
    for (i=cursor;i<head;i++) {
        if (!ring_read(i,&event)) { unreadable++; failed=1; continue; }
        if (event.type!=VJT_EV_WATCH_WR && event.type!=VJT_EV_WATCH_RD) continue;
        watched++;
        fprintf(events,"%llu,%u,%u,%u,%u,%06x,%06x,%08x\n",
                (unsigned long long)event.seq,event.frame,event.halfline,event.type,
                event.who,event.pc,event.addr,event.value);
    }
    cursor=head;
}

static void capture_video(void *data, const void *pixels, unsigned width, unsigned height, size_t pitch)
{
    harness_config *cfg=(harness_config *)data;
    char name[80];
    FILE *file;
    unsigned x,y;
    uint32_t pixel;
    uint8_t rgb[3];
    if (!pixels || cfg->current_frame%900) return;
    snprintf(name,sizeof(name),"frame-%06u.ppm",cfg->current_frame);
    file=fopen(name,"wb");
    if (!file) { failed=1; return; }
    fprintf(file,"P6\n%u %u\n255\n",width,height);
    for (y=0;y<height;y++) for (x=0;x<width;x++) {
        memcpy(&pixel,(const uint8_t *)pixels+y*pitch+x*4,4);
        rgb[0]=(uint8_t)(pixel>>16);rgb[1]=(uint8_t)(pixel>>8);rgb[2]=(uint8_t)pixel;
        if (fwrite(rgb,1,3,file)!=3) failed=1;
    }
    if (fclose(file)) failed=1;
}

static bool observe(void *data, unsigned frame)
{
    harness_config *cfg=(harness_config *)data;
    uint32_t pcs[1024];
    int count, i;
    unsigned b, index;
    uint32_t pc;
    observed_cpu_pc *seen;
    for (i=0;i<1024;i++) {
        index=(*cpu_queue_pointer-1-(unsigned)i)&0x3ff;
        pc=cpu_queue[index];
        if (pc<0x4000 || pc>0xffff0 || (pc&1)) continue;
        seen=&cpu_seen[pc>>1];
        if (!seen->observations) { seen->first_frame=frame; memcpy(seen->first_bytes,*main_ram+pc,16); }
        else if (memcmp(seen->first_bytes,*main_ram+pc,16)) seen->bytes_changed=1;
        seen->last_frame=frame;seen->observations++;
    }
    fprintf(commands,"%u",frame);
    for (i=0;i<3;i++) fprintf(commands,",%08x",be32(dsp_ram()+0xadc+i*4));
    for (i=0;i<40;i++) fprintf(commands,",%08x",be32(*main_ram+0x3bce0+i*4));
    fprintf(commands,"\n");
    fprintf(frames,"%u,%06x,%06x,%06x,%08x,%08x,%04x,%04x,%u,%08x,%u,%u,%zu,%u,%08x\n",
            frame,cpu_reg(NULL,16),gpu_pc(),dsp_pc(),dsp_control(),dsp_flags(),
            **left,**right,(unsigned)**clock_divider,**serial_mode,
            i2s_count(),i2s_nonzero(),cfg->audio.total_samples,
            cfg->audio.total_nonsilent,cfg->last_fb_hash);
    for (b=0;b<2;b++) {
        fprintf(banks,"%u,%u",frame,b);
        for (i=0;i<32;i++) fprintf(banks,",%08x",b?dsp_bank1[i]:dsp_bank0[i]);
        fprintf(banks,"\n");
    }
    backtrace(2,pcs,1024,&count); /* DSP enum in pinned vjag_memory.h */
    fprintf(history,"%u,%d",frame,count);
    for (i=0;i<count;i++) fprintf(history,",%06x",pcs[i]);
    fprintf(history,"\n");
    if (fwrite(dsp_ram(),1,8192,ram)!=8192) failed=1;
    if (frame==350) arm_trace();
    if (frame==437 && initialize_stack) {
        fprintf(stderr,"GPU stack experiment after437: %08x -> 00f03ff0\n",gpu_bank0[31]);
        gpu_bank0[31]=0x00f03ff0;
        initialization_count++;
    }
    drain_events();
    return !failed;
}

int main(int argc,char **argv)
{
    harness_config cfg=HARNESS_CONFIG_DEFAULT;
    FILE *observed;
    unsigned j,pc,count=0;
    cfg.frames=9000;
    cfg.want_fb_hash=1;
    if (getenv("BIWN_EXPERIMENT_GPU_STACK")) {
        if (strcmp(getenv("BIWN_EXPERIMENT_GPU_STACK"),"F03FF0")) return 7;
        initialize_stack=1;
    }
    if (!harness_init_from_args(&cfg,argc,argv)) return 1;
#define RESOLVE(variable,type,symbol) variable=(type)harness_dlsym(&cfg,symbol); if (!variable) return 2
    RESOLVE(gpu_pc,uint32_t (*)(void),"GPUGetPC");
    RESOLVE(dsp_pc,uint32_t (*)(void),"DSPGetPC");
    RESOLVE(dsp_control,uint32_t (*)(void),"DSPGetControl");
    RESOLVE(main_ram,uint8_t **,"jaguarMainRAM");
    RESOLVE(cpu_queue,uint32_t *,"pcQueue");
    RESOLVE(cpu_queue_pointer,uint32_t *,"pcQPtr");
    RESOLVE(dsp_ram,uint8_t *(*)(void),"DSPGetRAM");
    RESOLVE(i2s_count,uint32_t (*)(void),"DACGetI2SWriteCount");
    RESOLVE(i2s_nonzero,uint32_t (*)(void),"DACGetI2SNonZeroCount");
    RESOLVE(cpu_reg,unsigned int (*)(void *,int),"m68k_get_reg");
    RESOLVE(dsp_bank0,uint32_t *,"dsp_reg_bank_0");
    RESOLVE(dsp_bank1,uint32_t *,"dsp_reg_bank_1");
    RESOLVE(gpu_bank0,uint32_t *,"gpu_reg_bank_0");
    RESOLVE(dsp_flags,uint32_t (*)(void),"DSPGetFlags");
    RESOLVE(left,uint16_t **,"ltxd");
    RESOLVE(right,uint16_t **,"rtxd");
    RESOLVE(clock_divider,uint8_t **,"sclk");
    RESOLVE(serial_mode,uint32_t **,"smode");
    RESOLVE(arm_trace,void (*)(void),"vjtrace_arm");
    RESOLVE(disarm_trace,void (*)(void),"vjtrace_disarm");
    RESOLVE(watch,int (*)(uint32_t,uint32_t,unsigned),"vjtrace_watch_add");
    RESOLVE(ring_head,uint64_t (*)(void),"vjtrace_ring_head");
    RESOLVE(ring_read,int (*)(uint64_t,vjtrace_ev *),"vjtrace_ring_read");
    RESOLVE(backtrace,void (*)(int,uint32_t *,int,int *),"vjtrace_backtrace");
#undef RESOLVE
    if (!cfg.rom_path || !harness_load_rom(&cfg)) return 3;
    disarm_trace();
    if (watch(0xf1badc,0xf1bae7,2)<0 || watch(0x3bce0,0x3bd7f,2)<0) return 4;
    events=fopen("audio-watch-events.csv","w");
    if (!events) return 5;
    fprintf(events,"seq,frame,halfline,type,who,pc,addr,value\n");
    frames=fopen("audio-path-frames.csv","w");
    banks=fopen("dsp-banks.csv","w");
    history=fopen("dsp-history.csv","w");
    ram=fopen("dsp-frames.bin","wb");
    commands=fopen("audio-command-frames.csv","w");
    if (!frames || !banks || !history || !ram || !commands) return 4;
    fprintf(commands,"frame,mailbox_command,mailbox_source,mailbox_arg");
    for (j=0;j<40;j++) fprintf(commands,",ram_%06x",0x3bce0+j*4);
    fprintf(commands,"\n");
    fprintf(frames,"frame,cpu_pc,gpu_pc,dsp_pc,dsp_control,dsp_flags_raw,left,right,sclk,smode,i2s_capture_count,i2s_nonzero_capture_count,audio_pairs_total,audio_nonsilent_total,framebuffer_hash\n");
    fprintf(banks,"frame,bank");
    for (j=0;j<32;j++) fprintf(banks,",r%u",j);
    fprintf(banks,"\n");
    cfg.video_callback=capture_video;
    cfg.video_callback_data=&cfg;
    cfg.frame_callback=observe;
    cfg.frame_callback_data=&cfg;
    harness_run(&cfg);
    disarm_trace();
    drain_events();
    observed=fopen("observed_CPU_pcs.csv","w");
    if (!observed) failed=1;
    else {
        fprintf(observed,"pc,first_frame,last_frame,history_slot_observations,post_frame_bytes_changed,first_post_frame_bytes\n");
        for (pc=0x4000;pc<=0xffff0;pc+=2) {
            observed_cpu_pc *seen=&cpu_seen[pc>>1];
            if (!seen->observations) continue;
            count++;
            fprintf(observed,"%06x,%u,%u,%u,%u,",pc,seen->first_frame,seen->last_frame,seen->observations,seen->bytes_changed);
            for (j=0;j<16;j++) fprintf(observed,"%02x",seen->first_bytes[j]);
            fprintf(observed,"\n");
        }
        if (fclose(observed)) failed=1;
    }
    if (fclose(events) || fclose(frames) || fclose(banks) || fclose(history) || fclose(ram) || fclose(commands)) failed=1;
    fprintf(stderr,"AUDIO_STREAM frames=%u ring=%llu unreadable=%u watched=%llu initialization_count=%d max_frame_events=%llu CPU_pcs=%u\n",
            cfg.current_frame,(unsigned long long)cursor,unreadable,
            (unsigned long long)watched,initialization_count,(unsigned long long)max_frame_events,count);
    harness_shutdown(&cfg);
    return !failed && !unreadable && cfg.current_frame==cfg.frames &&
        initialization_count==initialize_stack ? 0 : 6;
}
