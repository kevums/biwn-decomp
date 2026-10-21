/* Coordinator native wrapper for the unchanged recovered outer task.
 * Helpers run on the original guest stack and may suspend there. The native
 * C call stack stays in a separate per-task arena until the helper returns.
 */
#include <stddef.h>
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wmisleading-indentation"
#include "../../experimental/deck-task-source/deck-task-source.c"
#pragma GCC diagnostic pop
#undef CALL
struct frame {
 struct biwn_deck_context context;
 uint32_t c_sp;struct biwn_task_cpu *active_cpu;
 uint32_t guest_sp,guest_ret,active;
};
_Static_assert(sizeof(struct biwn_task_cpu)==78,"CPU layout");
_Static_assert(sizeof(struct frame)==118,"frame layout");
_Static_assert(offsetof(struct frame,c_sp)==98,"C SP");
_Static_assert(offsetof(struct frame,active_cpu)==102,"CPU pointer");
_Static_assert(offsetof(struct frame,active)==114,"active flag");
typedef void (*return_fn)(void);
extern void biwn_outer_helper_return(void);
#define CAPTURE(name) extern int biwn_outer_capture_##name(struct frame *,struct biwn_task_cpu *,return_fn)
CAPTURE(initialize);CAPTURE(scan);CAPTURE(clear);CAPTURE(record);
CAPTURE(reset);CAPTURE(geometry);CAPTURE(mail);CAPTURE(texture);
CAPTURE(coordinate);CAPTURE(display_begin);CAPTURE(display_submit);
CAPTURE(display_end);CAPTURE(tail);
static int r16(void *p,uint32_t a,uint16_t *v){(void)p;*v=*(volatile uint16_t *)a;return 0;}
static int r32(void *p,uint32_t a,uint32_t *v){(void)p;*v=*(volatile uint32_t *)a;return 0;}
static int w16(void *p,uint32_t a,uint16_t v){(void)p;*(volatile uint16_t *)a=v;return 0;}
static int w32(void *p,uint32_t a,uint32_t v){(void)p;*(volatile uint32_t *)a=v;return 0;}
static struct biwn_world_bus memory={0,r16,r32,w16,w32,0,0,0};
static int service(void *opaque,struct biwn_world_bus *bus,struct biwn_task_cpu *cpu,uint32_t target){
 struct frame *f=opaque;int status;(void)bus;
 #define CALL(name) biwn_outer_capture_##name(f,cpu,biwn_outer_helper_return)
 switch(target){
 case 0x10990:status=CALL(initialize);break;
 case 0x11828:status=CALL(scan);break;
 case 0xe03a:status=CALL(clear);break;
 case 0x10c6e:status=CALL(record);break;
 case 0x1102a:status=CALL(reset);break;
 case 0x11ad4:status=CALL(geometry);break;
 case 0x16bf4:status=CALL(mail);break;
 case 0x10e72:status=CALL(texture);break;
 case 0x11d1a:status=CALL(coordinate);break;
 case 0xe19e:status=CALL(display_begin);break;
 case 0xe202:status=CALL(display_submit);break;
 case 0xe098:status=CALL(display_end);break;
 case 0x17f14:status=CALL(tail);break;
 default:return 1;
 }
 #undef CALL
 /* The unmodified recovery uses a local context. Capture first into the
  * persistent frame, then copy the helper result to that exact local CPU.
  * The pointer is saved across actual helper suspension, not reconstructed.
  */
 if(!status)*cpu=f->context.cpu;
 return status;
}
#include "native-inplace-resume.inc"
void biwn_outer_body(struct frame *f){
 f->context.bus=&memory;f->context.service=service;f->context.opaque=f;
 f->context.budget=64;f->context.error=0;
 f->context.error=native_outer_resume(&f->context,64);
}
__attribute__((used,externally_visible,noinline))
void *memcpy(void *out,const void *in,size_t n){unsigned char *d=out;const unsigned char *s=in;while(n--)*d++=*s++;return out;}
