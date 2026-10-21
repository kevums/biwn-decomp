#ifndef BIWN_DSP_MUSIC_BOOTSTRAP_H
#define BIWN_DSP_MUSIC_BOOTSTRAP_H
#include <stdint.h>
struct biwn_dsp_music_bootstrap_state {
 uint64_t accumulator;
 uint32_t registers[2][32],pc,z,c,n,flags,control;
 uint32_t remainder,modulo,matrix_control,matrix_pointer,data_organization,division_control,instructions;
 uint8_t local_RAM[8192];
};
struct biwn_dsp_music_bootstrap_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 int (*write16)(void *,uint32_t,uint16_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
enum biwn_dsp_music_bootstrap_status {BIWN_DSP_MUSIC_BOOTSTRAP_OK=0,
 BIWN_DSP_MUSIC_BOOTSTRAP_BAD_ARGUMENT=1,BIWN_DSP_MUSIC_BOOTSTRAP_BUS_ERROR=2,
 BIWN_DSP_MUSIC_BOOTSTRAP_BAD_PC=3,BIWN_DSP_MUSIC_BOOTSTRAP_WORK_LIMIT=4,
 BIWN_DSP_MUSIC_BOOTSTRAP_BAD_DELAY=5,BIWN_DSP_MUSIC_BOOTSTRAP_STOPPED=6};
/* Source F1B126 flag/register bootstrap to F1B144 idle, and CPU IRQ0
 * command2 handler to F1B148 (before the music engine starts).
 * Bank0 only; source command2 and valid song/resource tables required.
 * boundary run accepts stopPC F1B144/F1B148; own cpu_interrupt models
 * enabled IRQ0 at the idle boundary. No runtime decoder/original DSP.
 * Source SSI/music mixer/bank1 engine/other commands, actual CPU/DSP
 * interleaving period and full boot/audio are not implemented here. */
enum biwn_dsp_music_bootstrap_status biwn_dsp_music_bootstrap_step(struct biwn_dsp_music_bootstrap_bus *,struct biwn_dsp_music_bootstrap_state *);
enum biwn_dsp_music_bootstrap_status biwn_dsp_music_bootstrap_run(struct biwn_dsp_music_bootstrap_bus *,struct biwn_dsp_music_bootstrap_state *,uint32_t,uint32_t);
enum biwn_dsp_music_bootstrap_status biwn_dsp_music_bootstrap_cpu_interrupt(struct biwn_dsp_music_bootstrap_state *);
#endif
