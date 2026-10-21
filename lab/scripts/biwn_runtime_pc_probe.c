/* SPDX-License-Identifier: GPL-3.0-or-later
 * Lab-owned observer using the pinned VirtualJaguar test harness.
 * Samples the last 1024 CPU PCs after each frame, not a complete trace.
 * RAM bytes are observed after the frame, not necessarily at execution time.
 */
#include "harness/harness.h"
#include <stdio.h>
#include <stdint.h>
#include <string.h>

typedef struct {
    unsigned first_frame;
    unsigned last_frame;
    unsigned observations;
    unsigned bytes_changed;
    uint8_t first_bytes[16];
} observed_pc;

static observed_pc seen[0x80000];
static uint32_t *queue;
static uint32_t *queue_pointer;
static uint8_t **ram_pointer;
static unsigned int (*get_register)(void *, int);
static uint32_t *gpu_pc_pointer;
static uint32_t *dsp_pc_pointer;
static FILE *frames;

static bool sample_frame(void *unused, unsigned frame)
{
    unsigned i, index;
    uint32_t pc;
    observed_pc *observation;
    uint8_t *ram = *ram_pointer;
    (void)unused;
    if (!ram) return false;
    fprintf(frames, "%u,%06x,%06x,%06x\n", frame,
            get_register(NULL, 16), *gpu_pc_pointer, *dsp_pc_pointer);
    for (i = 0; i < 0x400; i++) {
        index = (*queue_pointer - 1 - i) & 0x3ff;
        pc = queue[index];
        if (pc < 0x4000 || pc > 0xffff0 || (pc & 1)) continue;
        observation = &seen[pc >> 1];
        if (!observation->observations) {
            observation->first_frame = frame;
            memcpy(observation->first_bytes, ram + pc, 16);
        } else if (memcmp(observation->first_bytes, ram + pc, 16)) {
            observation->bytes_changed = 1;
        }
        observation->last_frame = frame;
        observation->observations++;
    }
    return true;
}

int main(int argc, char **argv)
{
    harness_config cfg = HARNESS_CONFIG_DEFAULT;
    FILE *output;
    unsigned pc, i, count = 0;
    observed_pc *observation;
    cfg.frames = 900;
    if (!harness_init_from_args(&cfg, argc, argv)) return 1;
    queue = (uint32_t *)harness_dlsym(&cfg, "pcQueue");
    queue_pointer = (uint32_t *)harness_dlsym(&cfg, "pcQPtr");
    ram_pointer = (uint8_t **)harness_dlsym(&cfg, "jaguarMainRAM");
    gpu_pc_pointer = (uint32_t *)harness_dlsym(&cfg, "gpu_pc");
    dsp_pc_pointer = (uint32_t *)harness_dlsym(&cfg, "dsp_pc");
    get_register = (unsigned int (*)(void *, int))harness_dlsym(&cfg, "m68k_get_reg");
    if (!queue || !queue_pointer || !ram_pointer || !get_register ||
        !gpu_pc_pointer || !dsp_pc_pointer) return 2;
    if (!cfg.rom_path || !harness_load_rom(&cfg)) return 3;
    frames = fopen("frame_pcs.csv", "w");
    if (!frames) return 4;
    fprintf(frames, "frame,cpu_pc,gpu_pc,dsp_pc\n");
    cfg.frame_callback = sample_frame;
    harness_run(&cfg);
    fclose(frames);
    output = fopen("observed_pcs.csv", "w");
    if (!output) return 5;
    fprintf(output, "pc,first_frame,last_frame,history_slot_observations,post_frame_bytes_changed,first_post_frame_bytes\n");
    for (pc = 0x4000; pc <= 0xffff0; pc += 2) {
        observation = &seen[pc >> 1];
        if (!observation->observations) continue;
        count++;
        fprintf(output, "%06x,%u,%u,%u,%u,", pc, observation->first_frame,
                observation->last_frame, observation->observations,
                observation->bytes_changed);
        for (i = 0; i < 16; i++) fprintf(output, "%02x", observation->first_bytes[i]);
        fprintf(output, "\n");
    }
    fclose(output);
    fprintf(stderr, "BIWN PC observer: %u frames, %u distinct game-range PCs sampled\n",
            cfg.current_frame, count);
    harness_shutdown(&cfg);
    return cfg.current_frame == cfg.frames ? 0 : 6;
}
