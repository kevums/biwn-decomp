#ifndef BIWN_DSP_MUSIC_ENGINE_H
#define BIWN_DSP_MUSIC_ENGINE_H
#include <stdint.h>
struct biwn_dsp_music_engine_state {
 uint64_t accumulator;
 uint32_t registers[2][32],pc,z,c,n,flags,control;
 uint32_t remainder,modulo,matrix_control,matrix_pointer,data_organization,division_control,instructions;
 uint8_t local_RAM[8192];
 uint32_t bank,prestore_bank,flags_delay;
};
struct biwn_dsp_music_engine_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 int (*write16)(void *,uint32_t,uint16_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
enum biwn_dsp_music_engine_status {BIWN_DSP_MUSIC_ENGINE_OK=0,
 BIWN_DSP_MUSIC_ENGINE_BAD_ARGUMENT=1,BIWN_DSP_MUSIC_ENGINE_BUS_ERROR=2,
 BIWN_DSP_MUSIC_ENGINE_BAD_PC=3,BIWN_DSP_MUSIC_ENGINE_WORK_LIMIT=4,
 BIWN_DSP_MUSIC_ENGINE_BAD_DELAY=5,BIWN_DSP_MUSIC_ENGINE_STOPPED=6};
/* Fixed discovered bootstrap/CPU command1stop/command2reload and bank1 mixer/SSI IRQ1/timer IRQ2 blocks.
 * step uses source bank switching and branch-delay instructions, with the
 * pinned DSP flag-store retirement rule. assert_interrupt supplies declared
 * external IRQ0/1/2, including latches and source stack frame. No core calls
 * or runtime decoder. Only source discovered addresses are emitted; silent
 * startup song3BCE0/index0 is the current discovery, not complete music.
 * Physical clocks, arbitrary commands/voices/resources and fullgame remain
 * separate. Errors preserve input state with prior bus writes retained. */
enum biwn_dsp_music_engine_status biwn_dsp_music_engine_step(struct biwn_dsp_music_engine_bus *,struct biwn_dsp_music_engine_state *);
enum biwn_dsp_music_engine_status biwn_dsp_music_engine_assert_interrupt(struct biwn_dsp_music_engine_state *,uint32_t);
#endif
