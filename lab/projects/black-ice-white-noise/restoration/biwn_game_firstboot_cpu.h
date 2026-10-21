#ifndef BIWN_GAME_FIRSTBOOT_CPU_H
#define BIWN_GAME_FIRSTBOOT_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_game_firstboot_cpu_status {BIWN_GAME_FIRSTBOOT_CPU_OK=0,BIWN_GAME_FIRSTBOOT_CPU_BAD_ARGUMENT=1,
 BIWN_GAME_FIRSTBOOT_CPU_BUS_ERROR=2,BIWN_GAME_FIRSTBOOT_CPU_SERVICE_ERROR=3,
 BIWN_GAME_FIRSTBOOT_CPU_WORK_LIMIT=4,BIWN_GAME_FIRSTBOOT_CPU_BAD_RETURN=5,
 BIWN_GAME_FIRSTBOOT_CPU_YIELDED=6,BIWN_GAME_FIRSTBOOT_CPU_BAD_PC=7,BIWN_GAME_FIRSTBOOT_CPU_READY=8};
/* Actual game180000..180188 video/GPU copy, BIOS mode/marker setup,
 * firmware TOC selection/MSF subtraction, marker read/progress>100000,
 * I2S stop/GPU stop flag/poll and natural JMP4000. READY8 stops before
 * game4000 instruction. BIOS/controller/GPU execution, initial boot payload,
 * firmware TOC/state and event delivery are dependencies, not scripted here.
 * Service receives sourcePC before each selected instruction for trace.
 * No runtime decoder/originalCPU execution. Complete BIOS boot separate. */
enum biwn_game_firstboot_cpu_status biwn_game_firstboot_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_game_firstboot_cpu_status biwn_game_firstboot_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
