#ifndef BIWN_FIRMWARE_DSP_BOOT_PROBE_H
#define BIWN_FIRMWARE_DSP_BOOT_PROBE_H
#include <stdint.h>
struct biwn_firmware_DSP_boot_probe_state {
 uint64_t accumulator;
 uint32_t registers[2][32],pc,z,c,n,flags,control;
 uint32_t remainder,modulo,matrix_control,matrix_pointer,data_organization,division_control,instructions;
 uint8_t local_RAM[8192];
};
struct biwn_firmware_DSP_boot_probe_bus {
 int (*read8)(void *,uint32_t,uint8_t *);
 int (*read32)(void *,uint32_t,uint32_t *);
 int (*write32)(void *,uint32_t,uint32_t);
 void (*observe_PC)(void *,uint32_t);
 void *context;
};
enum biwn_firmware_DSP_boot_probe_status {BIWN_FIRMWARE_DSP_BOOT_PROBE_OK=0,
 BIWN_FIRMWARE_DSP_BOOT_PROBE_BAD_ARGUMENT=1,BIWN_FIRMWARE_DSP_BOOT_PROBE_BUS_ERROR=2,
 BIWN_FIRMWARE_DSP_BOOT_PROBE_BAD_PC=3,BIWN_FIRMWARE_DSP_BOOT_PROBE_WORK_LIMIT=4,
 BIWN_FIRMWARE_DSP_BOOT_PROBE_BAD_DELAY=5,BIWN_FIRMWARE_DSP_BOOT_PROBE_STOPPED=6,BIWN_FIRMWARE_DSP_BOOT_PROBE_CHANGED_CODE=7};
/* Diagnostic extension: original guarded DSP decryption/ROM check plus
 * exact source F1B560 MOVEI12345678 failure path. MAME-style DSP-only ROM
 * header view may be supplied by the diagnostic caller; it is NOT proved
 * hardware behavior. No source success/failure result injection, host
 * decrypted-code copy, original DSP execution or runtime opcode decoder.
 * This module alone proves no authentic disc boot or complete game. */
enum biwn_firmware_DSP_boot_probe_status biwn_firmware_DSP_boot_probe_step(struct biwn_firmware_DSP_boot_probe_bus *,struct biwn_firmware_DSP_boot_probe_state *);
enum biwn_firmware_DSP_boot_probe_status biwn_firmware_DSP_boot_probe_run(struct biwn_firmware_DSP_boot_probe_bus *,struct biwn_firmware_DSP_boot_probe_state *,uint32_t);
#endif
