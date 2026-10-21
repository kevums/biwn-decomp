#ifndef BIWN_GPU_MOVIE_EXIT_H
#define BIWN_GPU_MOVIE_EXIT_H
#include <stdint.h>
struct biwn_gpu_movie_exit_bus {
 int (*read16)(void *,uint32_t,uint16_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write16)(void *,uint32_t,uint16_t);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
struct biwn_gpu_movie_exit_state {
 uint32_t registers[2][32],pc,z,c,n;
 uint32_t matrix_control,matrix_pointer,division_control,remainder,instructions;
 uint32_t accumulator,hidata,flags,data_organization,control,active_bank;
 uint8_t local_RAM[4096];
};
enum biwn_gpu_movie_exit_status {BIWN_GPU_MOVIE_EXIT_OK=0,
 BIWN_GPU_MOVIE_EXIT_BAD_ARGUMENT=1,BIWN_GPU_MOVIE_EXIT_BUS_ERROR=2,
 BIWN_GPU_MOVIE_EXIT_BAD_PC=3,BIWN_GPU_MOVIE_EXIT_WORK_LIMIT=4,
 BIWN_GPU_MOVIE_EXIT_BAD_DELAY=5};
/*10execution-proven static GPU IRQ0 vector/exit-handler instructions, bank0.
 * EntryF03000 readsflags, acknowledgesIRQ0 and drops its sourceframe,
 * returns atF031BE dispatcher before idleloop. CPU_control5 emits its ownIRQframe. Inherited full banks/flags/
 * localRAM and peripheral callbacks; original GPU never executes. Unknown
 * PCs fail, no runtime decoder. Bank1 is unsupported; no other IRQ/main
 * boot/fullgame/physicalhardware claim. Prior bus stores survive host error,
 * inputstate commits only success. Source callbacks must not introduce a
 * another pending enabled GPU IRQ during the handler; that is a separate event. */
enum biwn_gpu_movie_exit_status biwn_gpu_movie_exit_run(struct biwn_gpu_movie_exit_bus *,struct biwn_gpu_movie_exit_state *,uint32_t);
enum biwn_gpu_movie_exit_status biwn_gpu_movie_exit_CPU_control5(struct biwn_gpu_movie_exit_bus *,struct biwn_gpu_movie_exit_state *);
#endif
