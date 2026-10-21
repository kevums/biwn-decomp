#ifndef BIWN_GPU_COMMANDS_H
#define BIWN_GPU_COMMANDS_H
#include <stdint.h>

/* Analyst names, not recovered symbols. Callbacks operate on 32-bit bus values.
 * Each callback returns zero on success. The caller owns all device behavior.
 * read_budget is consumed by every read, including the two source-RAM loads.
 * Limits, invalid-argument checks and callback errors are added host guards;
 * the original routines have no timeout or rollback. Partial writes remain.
 * Success means the CPU protocol reached its return, not GPU work completed.
 */
typedef int (*biwn_gpu_read32)(void *, uint32_t, uint32_t *);
typedef int (*biwn_gpu_write32)(void *, uint32_t, uint32_t);
struct biwn_gpu_bus {
    biwn_gpu_read32 read32;
    biwn_gpu_write32 write32;
    void *context;
    uint32_t read_budget;
};
enum biwn_gpu_result {
    BIWN_GPU_OK = 0,
    BIWN_GPU_BAD_ARGUMENT = 1,
    BIWN_GPU_READ_LIMIT = 2,
    BIWN_GPU_BUS_ERROR = 3
};

/* Original entry 0xe098: wait until F03200 reads exactly zero. */
enum biwn_gpu_result biwn_gpu_wait_idle(struct biwn_gpu_bus *bus);
/* Original entries 0xe0a6 and 0xe0f2. After ordered data writes, publish the
 * command, wait until F03204 differs from it (not necessarily zero), then wait
 * for F03200==0. These routines do not establish a D0 return value.
 */
enum biwn_gpu_result biwn_gpu_submit_4d80(struct biwn_gpu_bus *bus);
enum biwn_gpu_result biwn_gpu_submit_6ae0(struct biwn_gpu_bus *bus);
/* Original E2B8: publish three stack arguments then command4B00. No D/A
 * register results are established or changed by the original routine. */
enum biwn_gpu_result biwn_gpu_submit_4b00(struct biwn_gpu_bus *bus,
                                        uint32_t base,uint32_t index,uint32_t destination);
#endif
