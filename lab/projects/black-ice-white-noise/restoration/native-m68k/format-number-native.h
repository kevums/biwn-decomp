#ifndef BIWN_FORMAT_NUMBER_NATIVE_H
#define BIWN_FORMAT_NUMBER_NATIVE_H
#include <stdint.h>
#include "format-pad-native.h"
#include "unsigned-division-native.h"
/* r15 is virtual original A7 while executing, restored to entrySP on return.
 * C owns original32byte MOVEM saves and nested public math call frames.
 * The outer shim's C frame is below that public region. */
void biwn_native_format_number_body(uint32_t *r);
void biwn_native_semantic_divide_zero(uint32_t *r);
#endif
