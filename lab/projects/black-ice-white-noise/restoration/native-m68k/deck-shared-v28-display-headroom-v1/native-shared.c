/* Coordinator native Deck bridge, retaining five callers and adding five deeper helper bodies.
 * Qualified algorithm files are included unchanged. No whole-game/IRQ claim. */
#include <stddef.h>
/* Preserve the qualified files verbatim, including their unused API wrappers. */
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#include "../../experimental/deck-input-source/deck-input-source.c"
#include "../../experimental/deck-scene-source/deck-scene-source.c"
#include "../../experimental/deck-face-contact/deck-face-contact.c"
/* Target-only flag primitives affect the geometry compilation below.
 * Earlier retained callers and separately compiled coordinate body are unchanged. */
#include "native-alu.h"
#define deck_nz native_deck_nz
#define deck_alu native_deck_alu
#define scene_alu16 native_scene_alu16
#define scene_shift native_scene_shift
#define deck_asl5 native_deck_asl5
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
#include "../../experimental/deck-geometry-faces-v1/coordinator-reference.c"
static inline void native_faces_push(struct biwn_deck_context *s,uint32_t v){
 s->cpu.registers[15]-=4;deck_bank(s);deeper_write(s,s->cpu.registers[15],4,v);
}
static inline uint32_t native_faces_pop(struct biwn_deck_context *s){
 uint32_t v=deeper_read(s,s->cpu.registers[15],4);s->cpu.registers[15]+=4;deck_bank(s);return v;
}
#define deck_push native_faces_push
#define deck_pop native_faces_pop
#include "native-faces-stages.inc"
#include "../../experimental/deck-debug-overlay-v1/coordinator-reference.c"
#undef deck_pop
#undef deck_push
#include "native-geometry-stages.inc"
#include "native-clear-stages.inc"
#include "native-scene-reset.inc"

/* Target input profile: the canonical structured algorithm is unchanged.
 * This always-successful native bus is identical to the installed memory
 * provider. Keep budget, service capture, guest return and logical-bank checks.
 * Portable error/callback APIs above remain historical, not the target path. */
static inline void native_input_push(struct biwn_deck_context *s,uint32_t v){
 s->cpu.registers[15]-=4;deck_bank(s);deeper_write(s,s->cpu.registers[15],4,v);
}
static inline uint32_t native_input_pop(struct biwn_deck_context *s){
 uint32_t v=deeper_read(s,s->cpu.registers[15],4);s->cpu.registers[15]+=4;deck_bank(s);return v;
}
static inline void native_input_push_word(struct biwn_deck_context *s,uint32_t v){
 s->cpu.registers[15]-=2;deck_bank(s);deeper_write(s,s->cpu.registers[15],2,v);
}
static inline void native_input_call(struct biwn_deck_context *s,uint32_t target,uint32_t ret){
 uint32_t sp,value;int status;
 if(s->error)return;
 if(!s->budget){s->error=4;return;}s->budget--;
 native_input_push(s,ret);s->cpu.pc=target;sp=s->cpu.registers[15];
 if(s->error)return;
 status=s->service(s->opaque,s->bus,&s->cpu,target);
 if(status){s->error=3;return;}
 if(s->cpu.registers[15]!=sp){s->error=5;return;}
 value=native_input_pop(s);if(s->error)return;if(value!=ret){s->error=5;return;}s->cpu.pc=ret;
}
#define deck_push native_input_push
#define deck_pop native_input_pop
#define deck_call native_input_call
#define scene_push_word native_input_push_word
#define bit native_input_bit
#define input native_input
#define biwn_deck_input_body native_input_unused_api_body
#define biwn_deck_input_call native_input_unused_api_call
#include "native-input-source.inc"
#undef biwn_deck_input_call
#undef biwn_deck_input_body
#undef input
#undef bit
#undef scene_push_word
#undef deck_call
#undef deck_pop
#undef deck_push

/* Readable full-CPU scene caller; shares the input/face guarded frame.
 * Keep the source bus callbacks for mode/completion reads. */
#undef deck_read
#undef deck_write
#define SCENE17_NATIVE_DIRECT 1
#define deck_push native_input_push
#define deck_pop native_input_pop
/* Scene scheduling and GPU completion preserve original unbounded work.
 * The input caller's independent service budget remains unchanged. */
static inline void native_scene17_call(struct biwn_deck_context *s,uint32_t target,uint32_t ret){
 uint32_t sp,value;int status;
 if(s->error)return;
 native_input_push(s,ret);s->cpu.pc=target;sp=s->cpu.registers[15];
 if(s->error)return;
 status=s->service(s->opaque,s->bus,&s->cpu,target);
 if(status){s->error=3;return;}
 if(s->cpu.registers[15]!=sp){s->error=5;return;}
 value=native_input_pop(s);if(s->error)return;if(value!=ret){s->error=5;return;}s->cpu.pc=ret;
}
#define deck_call native_scene17_call
#include "native-scene17-context.h"
#include "../../experimental/scene-draw-structured-v1/coordinator-reference.inc"
#define SCENE_ROTATION_BEGIN(s) __asm__ volatile(".globl biwn_v25_rotation_begin\nbiwn_v25_rotation_begin:":::"memory")
#define SCENE_ROTATION_END(s) __asm__ volatile(".globl biwn_v25_rotation_end\nbiwn_v25_rotation_end:":::"memory")
static void scene_rotation_body(struct biwn_deck_context *) __attribute__((noinline));
#include "../../experimental/scene-rotation-structured-v1/coordinator-reference.inc"
#define SCENE_CLEAR_NATIVE_DIRECT 1
#define SCENE_CLEAR_BEGIN(s) __asm__ volatile(".globl biwn_v26_clear_begin\nbiwn_v26_clear_begin:":::"memory")
#define SCENE_CLEAR_END(s) __asm__ volatile(".globl biwn_v26_clear_end\nbiwn_v26_clear_end:":::"memory")
static void scene_clear_body(struct biwn_deck_context *) __attribute__((noinline));
#include "../../experimental/scene-clear-structured-v1/coordinator-reference.inc"
/* Structured185B2 keeps the original guest table; no target work deadline.
 * Explicit MOVE stores preserve the declared data-bus operation count. */
static inline void native_display_write(struct biwn_deck_context *s,uint32_t a,unsigned w,uint32_t v){
 if(s->error)return;volatile void *p=(volatile void *)(a&0xffffffu);
 if(w==2)__asm__ volatile("move.w %1,(%0)"::"a"(p),"d"(v):"memory","cc");
 else __asm__ volatile("move.l %1,(%0)"::"a"(p),"d"(v):"memory","cc");
}
static inline int native_display_clr_long(struct biwn_deck_context *s,uint32_t a){
 if(s->error)return s->error;volatile void *p=(volatile void *)(a&0xffffffu);
 __asm__ volatile("clr.l (%0)"::"a"(p):"memory","cc");return 0;
}
#define deck_read deeper_read
#define deck_write native_display_write
#define SCENE_DISPLAY_NATIVE_DIRECT 1
#define SCENE_DISPLAY_BEGIN(s) __asm__ volatile(".globl biwn_v27_display_begin\nbiwn_v27_display_begin:":::"memory")
#define SCENE_DISPLAY_END(s) __asm__ volatile(".globl biwn_v27_display_end\nbiwn_v27_display_end:":::"memory")
static void scene_display_list_body(struct biwn_deck_context *) __attribute__((noinline));
#include "../../experimental/scene-display-list-algorithm-v3/coordinator-reference.inc"
#undef deck_write
#undef deck_read

#undef deck_call
#undef deck_pop
#undef deck_push

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
extern int biwn_v4_capture_debug_formatter(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_debug_text(struct frame *,struct biwn_task_cpu *,return_fn);
extern void biwn_v4_coordinate_helper_return(void);
extern void biwn_v4_input_helper_return(void);
extern void biwn_v4_scan_helper_return(void);
static int r8(void *p,uint32_t a,uint8_t *v){(void)p;*v=*(volatile uint8_t *)a;return 0;}
static int r16(void *p,uint32_t a,uint16_t *v){(void)p;*v=*(volatile uint16_t *)a;return 0;}
static int r32(void *p,uint32_t a,uint32_t *v){(void)p;*v=*(volatile uint32_t *)a;return 0;}
static int w16(void *p,uint32_t a,uint16_t v){(void)p;*(volatile uint16_t *)a=v;return 0;}
static int w32(void *p,uint32_t a,uint32_t v){(void)p;*(volatile uint32_t *)a=v;return 0;}
static struct biwn_world_bus memory={r8,r16,r32,w16,w32,0,0,0};
__attribute__((noinline,used,externally_visible))
void biwn_v18_scene_reset_marker(struct frame *f){__asm__ volatile(""::"r"(f):"memory");}
static int dispatch(void *opaque,struct biwn_task_cpu *cpu,uint32_t target,return_fn ret){
 if(cpu!=&((struct frame *)opaque)->context.cpu)return 1;
 if(target==0xe26c)return biwn_v4_capture_gpu(opaque,cpu,ret);
 if(target==0xe540)return biwn_v4_capture_math(opaque,cpu,ret);
 if(target==0xe4c0)return biwn_v4_capture_poll(opaque,cpu,ret);
 if(target==0x10c6e)return biwn_v4_capture_record(opaque,cpu,ret);
 if(target==0x10e72)return biwn_v4_capture_first_texture(opaque,cpu,ret);
 if(target==0x10cb6)return biwn_v4_capture_texture(opaque,cpu,ret);
 if(target==0x1102a){
  struct frame *f=opaque;biwn_v18_scene_reset_marker(f);
  native_scene_reset_context(&f->context);return f->context.error;
 }
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
 native_input(&f->context);
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
static int service_geometry(void *,struct biwn_world_bus *,struct biwn_task_cpu *,uint32_t);
static int service_geometry_faces_gpu(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 (void)bus;if(cpu!=&((struct frame *)opaque)->context.cpu||target!=0xe26c)return 1;
 return biwn_v4_capture_gpu(opaque,cpu,biwn_v4_geometry_helper_return);
}
__attribute__((noinline,used))
static int service_geometry_faces(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 struct frame *f=opaque;struct biwn_deck_context *s=&f->context;uint32_t parent_budget=s->budget,remaining=64;int again;(void)bus;
 if(cpu!=&s->cpu||target!=0x1142e)return 1;
 s->budget=64;s->service=service_geometry_faces_gpu;again=native_faces_begin(s);
 while(again&&!s->error){
  if(!remaining--){s->error=4;break;}
  native_faces_before(s);
  deck_call(s,0xe26c,0x11684);
  if(!s->error)again=native_faces_after(s);
 }
 if(!s->error)native_faces_end(s);
 s->budget=parent_budget;s->service=service_geometry;return s->error;
}
static int service_geometry_debug_helpers(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 struct frame *f=opaque;(void)bus;if(cpu!=&f->context.cpu)return 1;
 if(target==0x1b45a)return biwn_v4_capture_debug_formatter(f,cpu,biwn_v4_geometry_helper_return);
 if(target==0x149ae)return biwn_v4_capture_debug_text(f,cpu,biwn_v4_geometry_helper_return);
 return 1;
}
__attribute__((noinline,used))
static int service_geometry_debug(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 struct frame *f=opaque;struct biwn_deck_context *s=&f->context;uint32_t parent_budget=s->budget;(void)bus;
 if(cpu!=&s->cpu||target!=0x10734)return 1;
 s->budget=16;s->service=service_geometry_debug_helpers;
 biwn_debug_overlay_body(s);
 s->budget=parent_budget;s->service=service_geometry;return s->error;
}
static int service_geometry(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 struct frame *f=opaque;(void)bus;
 if(cpu!=&f->context.cpu)return 1;
 if(target==0x1142e)return service_geometry_faces(opaque,bus,cpu,target);
 if(target==0x10734)return service_geometry_debug(opaque,bus,cpu,target);
 if(target==0x10968||target==0x10ba4||target==0x11384){
  biwn_v5_deeper_helper_marker(f,target);
  if(target==0x10968)native_clear_records(&f->context,65536);
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
 native_geometry_begin(&f->context);
 deck_call(&f->context,0x10968,0x11ae6);
 native_geometry_angles(&f->context);
 deck_call(&f->context,0x11384,0x11b32);
 deck_call(&f->context,0x10ba4,0x11b38);
 deck_call(&f->context,0x1142e,0x11b3e);
 deck_call(&f->context,0x10734,0x11b44);
 native_geometry_end(&f->context);
}

extern void biwn_v4_scene_helper_return(void);
extern int biwn_v4_capture_scene_clear(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_scene_geometry_command(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_scene_geometry(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_scene_projection(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_scene_draw(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_scene_wait(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_scene_interior(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_scene_region(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_scene_rotation(struct frame *,struct biwn_task_cpu *,return_fn);
extern int biwn_v4_capture_scene_display_list(struct frame *,struct biwn_task_cpu *,return_fn);
static int service_scene(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 (void)bus;if(cpu!=&((struct frame *)opaque)->context.cpu)return 1;
 if(target==0xe03a){scene_clear_body(&((struct frame *)opaque)->context);return 0;}
 if(target==0xe0a6)return biwn_v4_capture_scene_geometry_command(opaque,cpu,biwn_v4_scene_helper_return);
 if(target==0x170a0)return biwn_v4_capture_scene_geometry(opaque,cpu,biwn_v4_scene_helper_return);
 if(target==0xe19e)return biwn_v4_capture_scene_projection(opaque,cpu,biwn_v4_scene_helper_return);
 if(target==0xe202)return biwn_v4_capture_scene_draw(opaque,cpu,biwn_v4_scene_helper_return);
 if(target==0xe098)return biwn_v4_capture_scene_wait(opaque,cpu,biwn_v4_scene_helper_return);
 if(target==0xe0f2)return biwn_v4_capture_scene_interior(opaque,cpu,biwn_v4_scene_helper_return);
 if(target==0xe148)return biwn_v4_capture_scene_region(opaque,cpu,biwn_v4_scene_helper_return);
 if(target==0x17f14){scene_rotation_body(&((struct frame *)opaque)->context);return 0;}
 if(target==0x185b2){scene_display_list_body(&((struct frame *)opaque)->context);return 0;}
 return 1;
}
void biwn_v4_scene_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service_scene;f->context.opaque=f;f->context.budget=0;f->context.error=0;
 scene17_body(&f->context);
}
