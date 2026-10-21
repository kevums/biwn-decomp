/* Coordinator in-place contexts for three compiled Deck callers.
 * Qualified algorithm files are included unchanged. No whole-game/IRQ claim. */
#include <stddef.h>
/* Preserve the qualified files verbatim, including their unused API wrappers. */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#include "../../experimental/deck-input-source/deck-input-source.c"
#include "../../experimental/deck-scene-source/deck-scene-source.c"
#pragma GCC diagnostic pop
struct frame {
 struct biwn_deck_context context;
 uint32_t c_sp;struct biwn_task_cpu *active_cpu;uint32_t guest_sp,guest_ret,active;
};
_Static_assert(sizeof(struct biwn_task_cpu)==78,"CPU layout");
_Static_assert(sizeof(struct biwn_deck_context)==98,"context layout");
_Static_assert(offsetof(struct frame,context.cpu)==4,"CPU offset");
_Static_assert(offsetof(struct frame,context.error)==94,"error offset");
_Static_assert(offsetof(struct frame,c_sp)==98,"C SP offset");
_Static_assert(offsetof(struct frame,active_cpu)==102,"CPU pointer offset");
_Static_assert(offsetof(struct frame,guest_sp)==106,"guest SP offset");
_Static_assert(offsetof(struct frame,guest_ret)==110,"return offset");
_Static_assert(offsetof(struct frame,active)==114,"active offset");
_Static_assert(sizeof(struct frame)==118,"frame size");
typedef void (*return_fn)(void);
extern int biwn_v2_capture_gpu(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v2_capture_math(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v2_capture_poll(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v2_capture_record(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v2_capture_first_texture(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v2_capture_texture(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v2_capture_reset(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v2_capture_input(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v2_capture_face(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v2_capture_coordinate(struct frame *,struct biwn_task_cpu *,return_fn);
extern void biwn_v2_coordinate_helper_return(void);
extern void biwn_v2_input_helper_return(void);
extern void biwn_v2_scan_helper_return(void);
static int r8(void *p,uint32_t a,uint8_t *v){(void)p;*v=*(volatile uint8_t *)a;return 0;}
static int r16(void *p,uint32_t a,uint16_t *v){(void)p;*v=*(volatile uint16_t *)a;return 0;}
static int r32(void *p,uint32_t a,uint32_t *v){(void)p;*v=*(volatile uint32_t *)a;return 0;}
static int w16(void *p,uint32_t a,uint16_t v){(void)p;*(volatile uint16_t *)a=v;return 0;}
static int w32(void *p,uint32_t a,uint32_t v){(void)p;*(volatile uint32_t *)a=v;return 0;}
static struct biwn_world_bus memory={r8,r16,r32,w16,w32,0,0,0};
static int dispatch(void *opaque,struct biwn_task_cpu *cpu,uint32_t target,return_fn ret){
 if(cpu!=&((struct frame *)opaque)->context.cpu)return 1;
 if(target==0xe26c)return biwn_v2_capture_gpu(opaque,cpu,ret);
 if(target==0xe540)return biwn_v2_capture_math(opaque,cpu,ret);
 if(target==0xe4c0)return biwn_v2_capture_poll(opaque,cpu,ret);
 if(target==0x10c6e)return biwn_v2_capture_record(opaque,cpu,ret);
 if(target==0x10e72)return biwn_v2_capture_first_texture(opaque,cpu,ret);
 if(target==0x10cb6)return biwn_v2_capture_texture(opaque,cpu,ret);
 if(target==0x1102a)return biwn_v2_capture_reset(opaque,cpu,ret);
 if(target==0x11b4c)return biwn_v2_capture_input(opaque,cpu,ret);
 if(target==0x1186a)return biwn_v2_capture_face(opaque,cpu,ret);
 if(target==0x11d1a)return biwn_v2_capture_coordinate(opaque,cpu,ret);
 return 1;
}
static int service_coordinate(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){(void)bus;return dispatch(opaque,cpu,target,biwn_v2_coordinate_helper_return);}
void biwn_v2_coordinate_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service_coordinate;f->context.opaque=f;f->context.budget=4;f->context.error=0;
 biwn_deck_coordinate_body(&f->context);
}
static int service_input(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){(void)bus;return dispatch(opaque,cpu,target,biwn_v2_input_helper_return);}
void biwn_v2_input_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service_input;f->context.opaque=f;f->context.budget=16;f->context.error=0;
 input(&f->context);
}
static int service_scan(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){(void)bus;return dispatch(opaque,cpu,target,biwn_v2_scan_helper_return);}
void biwn_v2_scan_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service_scan;f->context.opaque=f;f->context.budget=64;f->context.error=0;
 update_active_objects(&f->context);
}
__attribute__((used,externally_visible,noinline))
void *memcpy(void *out,const void *in,size_t n){unsigned char *d=out;const unsigned char *s=in;while(n--)*d++=*s++;return out;}
