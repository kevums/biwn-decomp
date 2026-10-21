/* Coordinator native bridge around the qualified local/coordinator C body.
 * One1024-byte private arena slot per original1024-byte task slot. The
 * helper return uses SP-only address arithmetic, preserving all D/A and CCR
 * until safely captured on the private C stack. GPU and multiply remain
 * actual original-ABI dependencies. No firmware/timing/IRQ accuracy claim. */
#include <stddef.h>
#include "../../experimental/deck-coordinate-update-v2/deck-coordinate-contract.h"
struct native_deck_frame {
 struct biwn_task_cpu cpu;uint16_t padding;
 uint32_t c_sp;struct biwn_task_cpu *active_cpu;uint32_t guest_sp,guest_ret;
 int status;
};
_Static_assert(sizeof(struct biwn_task_cpu)==78,"68000 CPU layout");
_Static_assert(offsetof(struct native_deck_frame,c_sp)==80,"C SP layout");
_Static_assert(offsetof(struct native_deck_frame,active_cpu)==84,"CPU pointer layout");
_Static_assert(offsetof(struct native_deck_frame,guest_sp)==88,"guest SP layout");
_Static_assert(offsetof(struct native_deck_frame,guest_ret)==92,"return layout");
_Static_assert(offsetof(struct native_deck_frame,status)==96,"status layout");
extern int biwn_deck_gpu_capture(struct native_deck_frame *,struct biwn_task_cpu *);
extern int biwn_deck_math_capture(struct native_deck_frame *,struct biwn_task_cpu *);
static int r8(void *p,uint32_t a,uint8_t *v){(void)p;*v=*(volatile uint8_t *)a;return 0;}
static int r16(void *p,uint32_t a,uint16_t *v){(void)p;*v=*(volatile uint16_t *)a;return 0;}
static int r32(void *p,uint32_t a,uint32_t *v){(void)p;*v=*(volatile uint32_t *)a;return 0;}
static int w16(void *p,uint32_t a,uint16_t v){(void)p;*(volatile uint16_t *)a=v;return 0;}
static int w32(void *p,uint32_t a,uint32_t v){(void)p;*(volatile uint32_t *)a=v;return 0;}
static struct biwn_world_bus memory={r8,r16,r32,w16,w32,0,0,0};
static int service(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 (void)bus;
 if(target==0xe26c)return biwn_deck_gpu_capture(opaque,cpu);
 if(target==0xe540)return biwn_deck_math_capture(opaque,cpu);
 return 1;
}
void biwn_native_deck_coordinate_body(struct native_deck_frame *f){
 struct biwn_deck_context context={&memory,f->cpu,service,f,4,0};
 biwn_deck_coordinate_body(&context);f->cpu=context.cpu;f->status=context.error;
}
/* Freestanding compiler support for struct copies. */
__attribute__((used,externally_visible,noinline))
void *memcpy(void *out,const void *in,size_t n){
 unsigned char *d=out;const unsigned char *s=in;while(n--)*d++=*s++;return out;
}
