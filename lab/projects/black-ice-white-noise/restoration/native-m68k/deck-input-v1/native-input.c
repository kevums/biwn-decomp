/* Coordinator native input bridge around the qualified coordinator C body.
 * One1024-byte private arena slot per original1024-byte task slot. The
 * helper return uses SP-only address arithmetic, preserving all D/A and CCR
 * until safely captured on the private C stack. Input uses its own frame at slot144 and C stack top704.
 * Original poll/texture/record/reset helpers retain their guest ABI. No firmware/timing/IRQ accuracy claim. */
#include <stddef.h>
#include "../../experimental/deck-input-source/deck-input-source.h"
struct native_input_frame {
 struct biwn_task_cpu cpu;uint16_t padding;
 uint32_t c_sp;struct biwn_task_cpu *active_cpu;uint32_t guest_sp,guest_ret;
 int status;uint32_t active;
};
_Static_assert(sizeof(struct biwn_task_cpu)==78,"68000 CPU layout");
_Static_assert(offsetof(struct native_input_frame,c_sp)==80,"C SP layout");
_Static_assert(offsetof(struct native_input_frame,active_cpu)==84,"CPU pointer layout");
_Static_assert(offsetof(struct native_input_frame,guest_sp)==88,"guest SP layout");
_Static_assert(offsetof(struct native_input_frame,guest_ret)==92,"return layout");
_Static_assert(offsetof(struct native_input_frame,status)==96,"status layout");
_Static_assert(offsetof(struct native_input_frame,active)==100,"active layout");
extern int biwn_input_poll_capture(struct native_input_frame *,struct biwn_task_cpu *);
extern int biwn_input_record_capture(struct native_input_frame *,struct biwn_task_cpu *);
extern int biwn_input_first_texture_capture(struct native_input_frame *,struct biwn_task_cpu *);
extern int biwn_input_texture_capture(struct native_input_frame *,struct biwn_task_cpu *);
extern int biwn_input_reset_capture(struct native_input_frame *,struct biwn_task_cpu *);
static int r8(void *p,uint32_t a,uint8_t *v){(void)p;*v=*(volatile uint8_t *)a;return 0;}
static int r16(void *p,uint32_t a,uint16_t *v){(void)p;*v=*(volatile uint16_t *)a;return 0;}
static int r32(void *p,uint32_t a,uint32_t *v){(void)p;*v=*(volatile uint32_t *)a;return 0;}
static int w16(void *p,uint32_t a,uint16_t v){(void)p;*(volatile uint16_t *)a=v;return 0;}
static int w32(void *p,uint32_t a,uint32_t v){(void)p;*(volatile uint32_t *)a=v;return 0;}
static struct biwn_world_bus memory={r8,r16,r32,w16,w32,0,0,0};
static int service(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 (void)bus;
 if(target==0xe4c0)return biwn_input_poll_capture(opaque,cpu);
 if(target==0x10c6e)return biwn_input_record_capture(opaque,cpu);
 if(target==0x10e72)return biwn_input_first_texture_capture(opaque,cpu);
 if(target==0x10cb6)return biwn_input_texture_capture(opaque,cpu);
 if(target==0x1102a)return biwn_input_reset_capture(opaque,cpu);
 return 1;
}
void biwn_native_deck_input_body(struct native_input_frame *f){
 f->status=biwn_deck_input_body(&memory,&f->cpu,service,f,16);
}
/* Freestanding compiler support for struct copies. */
__attribute__((used,externally_visible,noinline))
void *memcpy(void *out,const void *in,size_t n){
 unsigned char *d=out;const unsigned char *s=in;while(n--)*d++=*s++;return out;
}
