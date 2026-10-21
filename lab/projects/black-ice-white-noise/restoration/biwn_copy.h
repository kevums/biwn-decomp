#ifndef BIWN_COPY_H
#define BIWN_COPY_H
#include "biwn_boot_slices.h"

struct biwn_register_command { uint32_t address, value; };

/* Analyst translation of the CPU byte path at 0xe4a2. Forward iteration is
 * intentional, including overlapping regions. Only counts 0..127 accepted.
 * Bounds errors are host guards absent from the original game. */
enum biwn_result biwn_copy_cpu_bytes(uint8_t *ram, size_t ram_size,
                                    uint32_t source, uint32_t destination,
                                    uint32_t count);

/* Describe writes from original range 0xe408..0xe4a0; never access a device.
 * Counts 128..0x7fffffff accepted. Original BMI overflow corner cases outside
 * this domain are deliberately rejected. Odd byte counts are retained even
 * though each command encodes a truncated halfword count. Device completion,
 * copied pixels/bytes, alignment validity and synchronization are unverified.
 * Address advancement wraps modulo 2^32, as in the original CPU arithmetic.
 * Output remains untouched on a host guard failure. */
enum biwn_result biwn_copy_device_commands(
    uint32_t source, uint32_t destination, uint32_t count,
    struct biwn_register_command *commands, size_t capacity,
    size_t *command_count, uint32_t *source_end, uint32_t *destination_end);

#endif
