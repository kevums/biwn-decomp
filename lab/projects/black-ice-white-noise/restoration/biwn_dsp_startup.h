#ifndef BIWN_DSP_STARTUP_H
#define BIWN_DSP_STARTUP_H
#include <stdint.h>

/* Analyst names for original CPU entries E942/E96C/E9EC/EA08.
 * Callbacks return zero on success. No DSP is implemented by this interface.
 * Every read consumes the added host budget, including header/payload reads.
 * Limits and callback errors are host behavior; the original has no timeout.
 * Prior writes remain on error. Status codes are not original D0 returns.
 */
typedef int (*biwn_dsp_read32)(void *, uint32_t, uint32_t *);
typedef int (*biwn_dsp_write)(void *, uint32_t, unsigned, uint32_t);
struct biwn_dsp_bus {
    biwn_dsp_read32 read32;
    biwn_dsp_write write;
    void *context;
    uint32_t read_budget;
};
struct biwn_dsp_cpu_state { uint32_t d1, a0, a1; };
enum biwn_dsp_result {
    BIWN_DSP_OK = 0, BIWN_DSP_BAD_ARGUMENT = 1,
    BIWN_DSP_READ_LIMIT = 2, BIWN_DSP_BUS_ERROR = 3
};

/* Poll F1BADC until exactly zero. */
enum biwn_dsp_result biwn_dsp_wait_mailbox(struct biwn_dsp_bus *);
/* Write mailbox1, control5, then poll. Command purpose is not inferred. */
enum biwn_dsp_result biwn_dsp_signal_one(struct biwn_dsp_bus *);
/* Read destination/length from7240/7244; copy longs from7248 using the
 * original ASR.L/SUBQ.L/DBRA count, set controls/mailbox2, then poll.
 * The low16bit DBRA counter always executes at least one copy, including
 * 65536 copies for length0..3. No length validation is added here.
 */
enum biwn_dsp_result biwn_dsp_load_start(struct biwn_dsp_bus *, struct biwn_dsp_cpu_state *);
/* Four ordered preliminary writes, then E96C. */
enum biwn_dsp_result biwn_dsp_setup(struct biwn_dsp_bus *, struct biwn_dsp_cpu_state *);
#endif
