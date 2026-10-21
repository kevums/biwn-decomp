#ifndef BIWN_DSP_MEDIA_AUDIO_H
#define BIWN_DSP_MEDIA_AUDIO_H
#include <stdint.h>
struct biwn_dsp_media_audio_state {
 uint64_t accumulator;
 uint32_t registers[2][32],pc,z,c,n,flags,control;
 uint32_t remainder,modulo,matrix_control,matrix_pointer,data_organization,division_control,instructions;
 uint8_t local_RAM[8192];
};
struct biwn_dsp_media_audio_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
enum biwn_dsp_media_audio_status {BIWN_DSP_MEDIA_AUDIO_OK=0,
 BIWN_DSP_MEDIA_AUDIO_BAD_ARGUMENT=1,BIWN_DSP_MEDIA_AUDIO_BUS_ERROR=2,
 BIWN_DSP_MEDIA_AUDIO_BAD_PC=3,BIWN_DSP_MEDIA_AUDIO_WORK_LIMIT=4,
 BIWN_DSP_MEDIA_AUDIO_BAD_DELAY=5,BIWN_DSP_MEDIA_AUDIO_STOPPED=6};
/* Fixed source program, bank0; no runtime instruction decoding/core calls.
 * step executes one source instruction and any taken-branch delay slot.
 * run stops at the source idle poll F1B074 with r27=0, or DSPGO clear.
 * ssi_interrupt supplies a declared external SSI event, with exact source
 * vector/private DSP frame; local valid stack required. Timing, other IRQs,
 * bank1 execution, peripherals and game/media integration are not supplied.
 * Errors retain earlier external writes and leave input state unchanged.
 * Code ends before mailbox/FIFO atF1B138. Stop/alignment filler is retained.
 */
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_step(struct biwn_dsp_media_audio_bus *,struct biwn_dsp_media_audio_state *);
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_run(struct biwn_dsp_media_audio_bus *,struct biwn_dsp_media_audio_state *,uint32_t);
enum biwn_dsp_media_audio_status biwn_dsp_media_audio_ssi_interrupt(struct biwn_dsp_media_audio_state *);
#endif
