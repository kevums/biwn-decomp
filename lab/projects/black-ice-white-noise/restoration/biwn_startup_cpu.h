#ifndef BIWN_STARTUP_CPU_H
#define BIWN_STARTUP_CPU_H
#include "biwn_world_cpu.h"
#include "biwn_input_dispatch.h"
enum biwn_startup_cpu_status {BIWN_STARTUP_CPU_OK=0,BIWN_STARTUP_CPU_BAD_ARGUMENT=1,
 BIWN_STARTUP_CPU_BUS_ERROR=2,BIWN_STARTUP_CPU_SERVICE_ERROR=3,
 BIWN_STARTUP_CPU_WORK_LIMIT=4,BIWN_STARTUP_CPU_BAD_RETURN=5,
 BIWN_STARTUP_CPU_YIELDED=6,BIWN_STARTUP_CPU_BAD_PC=7,BIWN_STARTUP_CPU_READY=8};
/* Fixed source blocks for17C40startup, RNG initialization/fill/setters,
 * E2F4/21242/18BA8/DFC0/1AEDA/F0C0. Full CPU/source private frames;
 * both stack banks. Helper bodies are supplied up to their outer RTS.
 * At17DC2 commits state and returns READY8 before executing renderloop.
 * DF60/DF8C nested suspension retains helper frames and returns YIELDED6.
 * No runtime decoding/original CPU calls. Generated blocks alone do not
 * prove source boot, all helpers, scheduling, devices, or playability. */
enum biwn_startup_cpu_status biwn_startup_cpu_body(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
enum biwn_startup_cpu_status biwn_startup_cpu_call(struct biwn_world_bus *,struct biwn_task_cpu *,biwn_input_write8,biwn_world_cpu_service,void *,uint32_t,int);
#endif
