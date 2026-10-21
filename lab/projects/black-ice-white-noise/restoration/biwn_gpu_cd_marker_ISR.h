#ifndef BIWN_GPU_CD_MARKER_ISR_H
#define BIWN_GPU_CD_MARKER_ISR_H
#include <stdint.h>
struct biwn_gpu_cd_marker_ISR_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_cd_marker_ISR_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator,hidata,flags,data_organization,control,active_bank;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_cd_marker_ISR_status {BIWN_GPU_CD_MARKER_ISR_OK=0,
 BIWN_GPU_CD_MARKER_ISR_BAD_ARGUMENT=1,BIWN_GPU_CD_MARKER_ISR_BUS_ERROR=2,
 BIWN_GPU_CD_MARKER_ISR_BAD_PC=3,BIWN_GPU_CD_MARKER_ISR_WORK_LIMIT=4,
 BIWN_GPU_CD_MARKER_ISR_BAD_DELAY=5,BIWN_GPU_CD_MARKER_ISR_HALTED=6,BIWN_GPU_CD_MARKER_ISR_LATCHED=7};
/* Resident BIOS GPU IRQ1 vector/DSA-FIFO handler and private return frame.
 * Fixed source blocks, own timer event/PC-2 frame, full logical state.
 * Handler uses bank0; event may enter from bank1 and return to it.
 * Source handles DSA/seek replies, enables I2S, drains FIFO into pointer/end buffer and stores progress. BaseF03050 descriptor/image only; Fixed3060 marker-capable handler with D2=0patch pairs, marker scanning and16-word synchronization. Other D2/encrypted variants remain unverified.
 * No runtime decoder/originalGPU calls. run stops on returned originalPC.
 * Controller data/events and their delivery/scheduling remain explicit dependencies. */
enum biwn_gpu_cd_marker_ISR_status biwn_gpu_cd_marker_ISR_run(struct biwn_gpu_cd_marker_ISR_bus *,struct biwn_gpu_cd_marker_ISR_state *,uint32_t,uint32_t);
enum biwn_gpu_cd_marker_ISR_status biwn_gpu_cd_marker_ISR_assert(struct biwn_gpu_cd_marker_ISR_bus *,struct biwn_gpu_cd_marker_ISR_state *);
#endif
