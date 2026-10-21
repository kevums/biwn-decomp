#ifndef BIWN_MOVIE_GPU_H
#define BIWN_MOVIE_GPU_H
#include <stdint.h>
struct biwn_movie_GPU_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_movie_GPU_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator,hidata,flags,data_organization,control,active_bank;
 uint8_t local_RAM[4096];
};
enum biwn_movie_GPU_status {BIWN_MOVIE_GPU_OK=0,
 BIWN_MOVIE_GPU_BAD_ARGUMENT=1,BIWN_MOVIE_GPU_BUS_ERROR=2,
 BIWN_MOVIE_GPU_BAD_PC=3,BIWN_MOVIE_GPU_WORK_LIMIT=4,
 BIWN_MOVIE_GPU_BAD_DELAY=5};
/* Execution-proven blocks from six first real movie frames, bank0.
 * Relocated source image must already be installed; caller supplies exact
 * inherited banks/flags/local RAM and actual command parameters. Stops at
 * idle F032C8 after command flag clears. No runtime decoding/original GPU
 * calls. Unobserved PCs fail explicitly; no complete-program claim.
 * Core bus callback supplies external memory and GPU CPU-interrupt signal.
 * External LOAD preserves source byte address; local LOAD aligns32bit.
 * LOADB in local RAM returns the whole32bit word, as source hardware does.
 * Taken branches execute their delay; trace reports outer instruction PCs.
 * Host errors retain prior external writes and leave input state unchanged.
 * Timing, CPU wrapper/IRQ and whole movie/game remain separate. */
enum biwn_movie_GPU_status biwn_movie_GPU_run(struct biwn_movie_GPU_bus *,struct biwn_movie_GPU_state *,uint32_t);
#endif
