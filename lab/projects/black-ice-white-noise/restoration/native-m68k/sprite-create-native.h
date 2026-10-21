#ifndef BIWN_SPRITE_CREATE_NATIVE_H
#define BIWN_SPRITE_CREATE_NATIVE_H
#include <stdint.h>
/* Original 137E0 register/packed-stack ABI, retained by the assembly boundary.
 * r[0..14] D0-D7/A0-A6; r[15] root SP; r[16] SR; r[17] continuation;
 * r[18] original allocator argument, needed in the decoder's fourth stack word.
 * Coordinator reconstruction; finite component verification is separate. */
#define SCR8(a) (*(volatile uint8_t *)(uint32_t)(a))
#define SCR16(a) (*(volatile uint16_t *)(uint32_t)(a))
#define SCR32(a) (*(volatile uint32_t *)(uint32_t)(a))
#define SCW8(a,v) (*(volatile uint8_t *)(uint32_t)(a)=(uint8_t)(v))
#define SCW16(a,v) (*(volatile uint16_t *)(uint32_t)(a)=(uint16_t)(v))
#define SCW32(a,v) (*(volatile uint32_t *)(uint32_t)(a)=(uint32_t)(v))
void biwn_native_sprite_create_body(uint32_t *r);
void biwn_native_sprite_create_position_capture(uint32_t *r);
void biwn_native_sprite_create_allocate_capture(uint32_t *r);
void biwn_native_sprite_create_decode_capture(uint32_t *r);
#endif
