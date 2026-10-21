#ifndef BIWN_FIRMWARE_DSP_AUTH_H
#define BIWN_FIRMWARE_DSP_AUTH_H
#include <stdint.h>
struct biwn_firmware_DSP_auth_state {
 uint64_t accumulator;
 uint32_t registers[2][32],pc,z,c,n,flags,control;
 uint32_t remainder,modulo,matrix_control,matrix_pointer,data_organization,division_control,instructions;
 uint8_t local_RAM[8192];
};
struct biwn_firmware_DSP_auth_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
enum biwn_firmware_DSP_auth_status {BIWN_FIRMWARE_DSP_AUTH_OK=0,
 BIWN_FIRMWARE_DSP_AUTH_BAD_ARGUMENT=1,BIWN_FIRMWARE_DSP_AUTH_BUS_ERROR=2,
 BIWN_FIRMWARE_DSP_AUTH_BAD_PC=3,BIWN_FIRMWARE_DSP_AUTH_WORK_LIMIT=4,
 BIWN_FIRMWARE_DSP_AUTH_BAD_DELAY=5,BIWN_FIRMWARE_DSP_AUTH_STOPPED=6,BIWN_FIRMWARE_DSP_AUTH_CHANGED_CODE=7};
/* Fixed observed source firmware DSP path: initial ROM-derived code
 * F1B2EC..F1B662 and code produced by its own arithmetic atF1B6AC..F1B7B4.
 * Each instruction checks live source bytes, including MOVEI immediates.
 * C must compute/decrypt/erase local data itself; no decrypted payload copy.
 * Bank0, pinned retail userROM and observed input path only. No runtime
 * decoder, emulator execution, magic-value injection, IRQs or clocks.
 * run retains state on a quantum budget return4; returns0 when sourceGO
 * clears. Error retains earlier external writes, not intermediate local
 * state. Other keys/ROMs/failure branches, firmware CPU/GPU boot/disc
 * loading/global schedule and full game remain separate. */
enum biwn_firmware_DSP_auth_status biwn_firmware_DSP_auth_step(struct biwn_firmware_DSP_auth_bus *,struct biwn_firmware_DSP_auth_state *);
enum biwn_firmware_DSP_auth_status biwn_firmware_DSP_auth_run(struct biwn_firmware_DSP_auth_bus *,struct biwn_firmware_DSP_auth_state *,uint32_t);
#endif
