#ifndef BIWN_SCENE_CONSTRUCTOR_CPU_H
#define BIWN_SCENE_CONSTRUCTOR_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_scene_constructor_cpu_status {BIWN_SCENE_CONSTRUCTOR_CPU_OK=0,BIWN_SCENE_CONSTRUCTOR_CPU_BAD_ARGUMENT=1,
 BIWN_SCENE_CONSTRUCTOR_CPU_BUS_ERROR=2,BIWN_SCENE_CONSTRUCTOR_CPU_SERVICE_ERROR=3,
 BIWN_SCENE_CONSTRUCTOR_CPU_WORK_LIMIT=4,BIWN_SCENE_CONSTRUCTOR_CPU_BAD_RETURN=5,
 BIWN_SCENE_CONSTRUCTOR_CPU_YIELDED=6,BIWN_SCENE_CONSTRUCTOR_CPU_BAD_PC=7};
/* Fixed constructor10990,selector10A6A,reference release1AE88,
 * slot clear10968 andrecord insert11762. Both stack banks/fullCPU/private
 * frames retained. Nested source bodies/providers stop before RTS.
 * DF60/DF8C suspension commits CPU/frames for actual scheduler resumption.
 * Coordinator build-time translation,no runtime decode/originalCPU calls.
 * Generation alone does not prove constructor,disc or gameplay behavior.
 */
enum biwn_scene_constructor_cpu_status biwn_scene_constructor_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_scene_constructor_cpu_status biwn_scene_constructor_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
