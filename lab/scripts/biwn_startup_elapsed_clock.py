"""Candidate CPU-time budget for startup services at system-task safe points.

This removes one-pulse-per-task-visit acceleration. Event delivery is still
deferred to DDD8 and uses the existing periodic service adapter; this is not
instruction-boundary event scheduling or physical hardware timing.
"""
import json, types

def install(runtime, period_us):
    runtime.startup_outer_budget=3000000
    pulse=runtime.clock_tick
    emitted=0
    visits=0
    events=[]
    cycle_us=0.07521368396
    def clock(self):
        nonlocal emitted,visits
        visits+=1
        elapsed=self.startup_observed_CPU_cycles*cycle_us
        due=int(elapsed/period_us)
        assert due>=emitted,(due,emitted)
        # Capture due before calling the source IRQ handler: its CPU cost is
        # credited on the next safe point, avoiding recursive clock delivery.
        for _ in range(due-emitted):
            pulse();emitted+=1
            events.append(dict(pulse=emitted,observed_CPU_cycles=self.startup_observed_CPU_cycles,elapsed_us=self.startup_observed_CPU_cycles*cycle_us,service_time_us=emitted*period_us))
    runtime.clock_tick=types.MethodType(clock,runtime)
    def finish():
        report=dict(status='candidate_CPU_budgeted_periodic_services',system_task_visits=visits,service_pulses=emitted,CPU_cycles=runtime.startup_observed_CPU_cycles,IRQ_entries=runtime.startup_observed_IRQ_entries,elapsed_us=runtime.startup_observed_CPU_cycles*cycle_us,service_period_us=period_us,events=events,instruction_boundary_event_delivery=False,main_video_queue_still_held=True,global_cycle_scheduling_verified=False)
        (runtime.out/(runtime.mode+'-startup-elapsed-clock.json')).write_text(json.dumps(report,indent=2)+'\n')
        runtime.clock_tick=pulse
        return report
    runtime.finish_startup_elapsed_clock=finish
