/* Coordinator native Deck bridge, retaining five callers and adding four deeper helper bodies.
 * Qualified algorithm files are included unchanged. No whole-game/IRQ claim. */
#include <stddef.h>
/* Preserve the qualified files verbatim, including their unused API wrappers. */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#include "../../experimental/deck-input-source/deck-input-source.c"
#include "../../experimental/deck-scene-source/deck-scene-source.c"
#include "../../experimental/deck-face-contact/deck-face-contact.c"
#include "../../experimental/deck-geometry-helpers-v1/helper-contract.h"
/* Native bus profile: these three bodies use the same always-successful
 * direct volatile RAM/MMIO accesses as memory below, avoiding host callbacks.
 * The qualified algorithm file remains unchanged. Original110D4 stays captured. */
static inline uint32_t deeper_read(struct biwn_deck_context *s,uint32_t a,unsigned w){
 if(s->error)return 0;a&=0xffffffu;
 return w==2?*(volatile uint16_t *)a:*(volatile uint32_t *)a;
}
static inline void deeper_write(struct biwn_deck_context *s,uint32_t a,unsigned w,uint32_t v){
 if(s->error)return;a&=0xffffffu;
 if(w==2)*(volatile uint16_t *)a=(uint16_t)v;else *(volatile uint32_t *)a=v;
}
static inline void deeper_clr8(struct biwn_deck_context *s,biwn_deck_write8 w,uint32_t a){
 volatile uint8_t *p=(volatile uint8_t *)(a&0xffffffu);uint8_t old;(void)w;
 if(s->error)return;old=*p;(void)old;*p=0;deck_nz(s,0,8);
}
static void clear_records(struct biwn_deck_context *,biwn_deck_write8,uint32_t) __attribute__((noinline));
static void advance_texture(struct biwn_deck_context *) __attribute__((noinline));
static void setup_matrix(struct biwn_deck_context *) __attribute__((noinline));
#define deck_read deeper_read
#define deck_write deeper_write
#define helper_clr8 deeper_clr8
#include "../../experimental/deck-geometry-helpers-v1/coordinator-reference.c"
#include "native-matrix-stages.inc"
#include "../../experimental/deck-plane-layout-v1/coordinator-reference.c"
#undef helper_clr8
#undef deck_write
#undef deck_read
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
extern int biwn_v4_capture_gpu(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_math(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_poll(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_record(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_first_texture(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_texture(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_reset(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_input(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_face(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_coordinate(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_geometry_transform(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_geometry_setup(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_geometry_objects(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_geometry_bsp(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_geometry_draw(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_geometry_finalize(struct frame *,struct biwn_task_cpu *,return_fn);
extern void biwn_v4_coordinate_helper_return(void);
extern void biwn_v4_input_helper_return(void);
extern void biwn_v4_scan_helper_return(void);
static int r8(void *p,uint32_t a,uint8_t *v){(void)p;*v=*(volatile uint8_t *)a;return 0;}
static int r16(void *p,uint32_t a,uint16_t *v){(void)p;*v=*(volatile uint16_t *)a;return 0;}
static int r32(void *p,uint32_t a,uint32_t *v){(void)p;*v=*(volatile uint32_t *)a;return 0;}
static int w8(void *p,uint32_t a,uint8_t v){(void)p;*(volatile uint8_t *)a=v;return 0;}
static int w16(void *p,uint32_t a,uint16_t v){(void)p;*(volatile uint16_t *)a=v;return 0;}
static int w32(void *p,uint32_t a,uint32_t v){(void)p;*(volatile uint32_t *)a=v;return 0;}
static struct biwn_world_bus memory={r8,r16,r32,w16,w32,0,0,0};
static int dispatch(void *opaque,struct biwn_task_cpu *cpu,uint32_t target,return_fn ret){
 if(cpu!=&((struct frame *)opaque)->context.cpu)return 1;
 if(target==0xe26c)return biwn_v4_capture_gpu(opaque,cpu,ret);
 if(target==0xe540)return biwn_v4_capture_math(opaque,cpu,ret);
 if(target==0xe4c0)return biwn_v4_capture_poll(opaque,cpu,ret);
 if(target==0x10c6e)return biwn_v4_capture_record(opaque,cpu,ret);
 if(target==0x10e72)return biwn_v4_capture_first_texture(opaque,cpu,ret);
 if(target==0x10cb6)return biwn_v4_capture_texture(opaque,cpu,ret);
 if(target==0x1102a)return biwn_v4_capture_reset(opaque,cpu,ret);
 if(target==0x11b4c)return biwn_v4_capture_input(opaque,cpu,ret);
 if(target==0x1186a)return biwn_v4_capture_face(opaque,cpu,ret);
 if(target==0x11d1a)return biwn_v4_capture_coordinate(opaque,cpu,ret);
 if(target==0x110d4)return biwn_v4_capture_geometry_transform(opaque,cpu,ret);
 if(target==0x10968)return biwn_v4_capture_geometry_setup(opaque,cpu,ret);
 if(target==0x11384)return biwn_v4_capture_geometry_objects(opaque,cpu,ret);
 if(target==0x10ba4)return biwn_v4_capture_geometry_bsp(opaque,cpu,ret);
 if(target==0x1142e)return biwn_v4_capture_geometry_draw(opaque,cpu,ret);
 if(target==0x10734)return biwn_v4_capture_geometry_finalize(opaque,cpu,ret);
 return 1;
}
static int service_coordinate(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){(void)bus;return dispatch(opaque,cpu,target,biwn_v4_coordinate_helper_return);}
void biwn_v4_coordinate_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service_coordinate;f->context.opaque=f;f->context.budget=4;f->context.error=0;
 biwn_deck_coordinate_body(&f->context);
}
static int service_input(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){(void)bus;return dispatch(opaque,cpu,target,biwn_v4_input_helper_return);}
void biwn_v4_input_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service_input;f->context.opaque=f;f->context.budget=16;f->context.error=0;
 input(&f->context);
}
static int service_scan(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){(void)bus;return dispatch(opaque,cpu,target,biwn_v4_scan_helper_return);}
void biwn_v4_scan_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service_scan;f->context.opaque=f;f->context.budget=64;f->context.error=0;
 update_active_objects(&f->context);
}
__attribute__((used,externally_visible,noinline))
void *memcpy(void *out,const void *in,size_t n){unsigned char *d=out;const unsigned char *s=in;while(n--)*d++=*s++;return out;}

extern void biwn_v4_face_helper_return(void);
static int service_face(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){(void)bus;return dispatch(opaque,cpu,target,biwn_v4_face_helper_return);}
void biwn_v4_face_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service_face;f->context.opaque=f;f->context.budget=16;f->context.error=0;
 contact(&f->context);
}

/* Geometry aliases the active-guarded coordinate frame. */
extern void biwn_v4_geometry_helper_return(void);
__attribute__((noinline,used))
static int service_geometry_original(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 struct frame *f=opaque;(void)bus;if(cpu!=&f->context.cpu||target!=0x110d4)return 1;
 biwn_plane_layout_body(&f->context);return f->context.error;
}
__attribute__((used,externally_visible,noinline))
void biwn_v5_deeper_helper_marker(struct frame *f,uint32_t target){__asm__ volatile("" : : "r"(f),"r"(target) : "memory");}
static int service_geometry(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 struct frame *f=opaque;(void)bus;
 if(cpu!=&f->context.cpu)return 1;
 if(target==0x10968||target==0x10ba4||target==0x11384){
  biwn_v5_deeper_helper_marker(f,target);
  if(target==0x10968)clear_records(&f->context,w8,65536);
  else if(target==0x10ba4)advance_texture(&f->context);
  else{
   native_matrix_before(&f->context);
   f->context.service=service_geometry_original;
   deck_call(&f->context,0x110d4,0x113fe);
   f->context.service=service_geometry;
   if(!f->context.error)native_matrix_after(&f->context);
  }
  return f->context.error;
 }
 return dispatch(opaque,cpu,target,biwn_v4_geometry_helper_return);
}
void biwn_v4_geometry_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service_geometry;f->context.opaque=f;f->context.budget=8;f->context.error=0;
 collect_geometry(&f->context);
}
