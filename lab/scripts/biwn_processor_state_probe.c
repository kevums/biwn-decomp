/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-owned, read-only post-frame observation of the pinned emulator.
 * Direct diagnostic accessors avoid MMIO read side effects.
 */
#include "harness/harness.h"
#include <stdio.h>
#include <stdint.h>

static uint8_t **main_ram;
static uint8_t *(*gpu_ram)(void);
static uint8_t *(*dsp_ram)(void);
static uint32_t (*gpu_pc)(void);
static uint32_t (*dsp_pc)(void);
static uint32_t (*gpu_control)(void);
static uint32_t (*dsp_control)(void);
static uint32_t (*i2s_count)(void);
static uint32_t (*i2s_nonzero)(void);
static unsigned int (*cpu_reg)(void *, int);
static FILE *csv, *gpu_frames, *dsp_frames;
static int failed;

static uint32_t be32(const uint8_t *p)
{
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16) |
           ((uint32_t)p[2] << 8) | p[3];
}

static bool observe(void *data, unsigned frame)
{
    harness_config *cfg = (harness_config *)data;
    uint8_t *gpu = gpu_ram();
    uint8_t *dsp = dsp_ram();
    FILE *snapshot;
    char name[64];
    unsigned i;
    if (!gpu || !dsp || !*main_ram) return false;
    if (fwrite(gpu, 1, 0x1000, gpu_frames) != 0x1000 ||
        fwrite(dsp, 1, 0x2000, dsp_frames) != 0x2000) {
        failed = 1;
        return false;
    }
    fprintf(csv, "%u,%06x,%06x,%06x,%08x,%08x,%u,%u,%zu,%u,%08x",
            frame, cpu_reg(NULL, 16), gpu_pc(), dsp_pc(),
            gpu_control(), dsp_control(), i2s_count(), i2s_nonzero(),
            cfg->audio.total_samples, cfg->audio.total_nonsilent,
            cfg->last_fb_hash);
    for (i = 0; i < 8; i++) fprintf(csv, ",%08x", be32(gpu + 0x200 + i * 4));
    fprintf(csv, "\n");
    if (frame == 430 || frame == 431 || frame == 619 || frame == 620 || frame == 900) {
        snprintf(name, sizeof(name), "main-ram-frame-%u.bin", frame);
        snapshot = fopen(name, "wb");
        if (!snapshot) { failed = 1; return false; }
        if (fwrite(*main_ram, 1, 0x200000, snapshot) != 0x200000) failed = 1;
        if (fclose(snapshot)) failed = 1;
    }
    return !failed;
}

int main(int argc, char **argv)
{
    harness_config cfg = HARNESS_CONFIG_DEFAULT;
    cfg.frames = 900;
    if (!harness_init_from_args(&cfg, argc, argv)) return 1;
    main_ram = (uint8_t **)harness_dlsym(&cfg, "jaguarMainRAM");
    gpu_ram = (uint8_t *(*)(void))harness_dlsym(&cfg, "GPUGetRAM");
    dsp_ram = (uint8_t *(*)(void))harness_dlsym(&cfg, "DSPGetRAM");
    gpu_pc = (uint32_t (*)(void))harness_dlsym(&cfg, "GPUGetPC");
    dsp_pc = (uint32_t (*)(void))harness_dlsym(&cfg, "DSPGetPC");
    gpu_control = (uint32_t (*)(void))harness_dlsym(&cfg, "GPUGetControl");
    dsp_control = (uint32_t (*)(void))harness_dlsym(&cfg, "DSPGetControl");
    i2s_count = (uint32_t (*)(void))harness_dlsym(&cfg, "DACGetI2SWriteCount");
    i2s_nonzero = (uint32_t (*)(void))harness_dlsym(&cfg, "DACGetI2SNonZeroCount");
    cpu_reg = (unsigned int (*)(void *, int))harness_dlsym(&cfg, "m68k_get_reg");
    if (!main_ram || !gpu_ram || !dsp_ram || !gpu_pc || !dsp_pc ||
        !gpu_control || !dsp_control || !i2s_count || !i2s_nonzero || !cpu_reg) return 2;
    if (!cfg.rom_path || !harness_load_rom(&cfg)) return 3;
    csv = fopen("processor-state.csv", "w");
    gpu_frames = fopen("gpu-frames.bin", "wb");
    dsp_frames = fopen("dsp-frames.bin", "wb");
    if (!csv || !gpu_frames || !dsp_frames) return 4;
    fprintf(csv, "frame,cpu_pc,gpu_pc,dsp_pc,gpu_control,dsp_control,i2s_capture_count,i2s_nonzero_capture_count,audio_pairs_total,audio_nonsilent_total,framebuffer_hash");
    fprintf(csv, ",gpu_f03200,gpu_f03204,gpu_f03208,gpu_f0320c,gpu_f03210,gpu_f03214,gpu_f03218,gpu_f0321c\n");
    cfg.frame_callback = observe;
    cfg.frame_callback_data = &cfg;
    harness_run(&cfg);
    if (fclose(csv)) failed = 1;
    if (fclose(gpu_frames)) failed = 1;
    if (fclose(dsp_frames)) failed = 1;
    fprintf(stderr, "BIWN processor state: %u frames; %zu audio pairs; %u nonsilent\n",
            cfg.current_frame, cfg.audio.total_samples, cfg.audio.total_nonsilent);
    harness_shutdown(&cfg);
    return !failed && cfg.current_frame == cfg.frames ? 0 : 5;
}
