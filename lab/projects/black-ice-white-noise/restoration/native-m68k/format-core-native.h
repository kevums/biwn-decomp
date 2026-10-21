#ifndef BIWN_FORMAT_CORE_NATIVE_H
#define BIWN_FORMAT_CORE_NATIVE_H
#include "format-number-native.h"
void biwn_native_format_pad_body(uint32_t *r);
void biwn_native_format_string_body(uint32_t *r);
void biwn_native_format_core_body(uint32_t *r);
void biwn_native_format_variadic_body(uint32_t *r);
/* Same semantic register frame as number. Public LINK/MOVEM/arguments and
 * nested helper frames are retained. Core/variadic r15 returns to entrySP.
 * Wrapper context must lie below the deepest public138byte variadic frame. */
#endif
