"""Candidate shared main/JERRY event time from startup CPU costs.

CPU-owned interrupts enter architecturally then execute one source instruction
at a time. GPU/DSP services remain synchronous; this is not global scheduling.
"""
import ctypes as c,hashlib,json,struct,types
import check_biwn_movie_GPU as GPU
import check_biwn_music_DSP_engine as music
import check_biwn_media_setup_cpu as media
from probe_biwn_gpu_projection import gpu_state

def install(runtime,label="startup",stable=False):
    core=runtime.core;clock_before=runtime.clock_tick;sample_before=getattr(runtime,'sample_pending_CPU_IRQ',None)
    jerry_origin=runtime.jerry_elapsed
    elapsed=0.0;main_events=0;jerry_events=0;GPU_timers=[];asset_ticks=0;asset_first=None;events_digest=hashlib.sha256()
    def mirror():
        if runtime.mode=='C':
            raw=c.create_string_buffer(12000);assert core.GPUStateSave(raw)==4416
            assert core.GPUStateLoad(c.create_string_buffer(GPU.logical(runtime.gpu)+raw.raw[4396:4416]))==4416
    def adopt():
        if runtime.mode=='C':
            raw=c.create_string_buffer(12000);assert core.GPUStateSave(raw)==4416
            changed=GPU.state_from_raw(raw.raw);count=runtime.gpu.instructions
            c.memmove(c.byref(runtime.gpu),c.byref(changed),c.sizeof(changed));runtime.gpu.instructions=count
    def pump_timer():
        state=runtime.gpu if runtime.mode=='C'else GPU.state_from_raw(gpu_state(core)[0])
        if not(state.flags&8)or state.pc!=0xf03020:return
        return_pc=core.GPUReadLong(state.registers[0][31]&~3,3)+2
        trace=hashlib.sha256();old_trace,old_blocks=runtime.gpu_trace,runtime.gpu_blocks
        if runtime.mode=='native':
            blocks=delays=0
            for _ in range(100):
                pc=core.GPUGetPC()
                if pc==return_pc:break
                trace.update(struct.pack('>I',pc));blocks+=1;opcode=core.GPUReadWord(pc,3);core.GPUExec(1)
                if opcode>>10 in [52,53]and core.GPUGetPC()!=pc+2:delays+=1
            else:raise AssertionError(('startup GPU timer bound',hex(pc),hex(return_pc)))
            instructions=blocks+delays;raw=c.create_string_buffer(12000);assert core.GPUStateSave(raw)==4416;image=raw.raw[:4396]
        else:
            runtime.gpu_trace=trace;runtime.gpu_blocks=0;start=runtime.gpu.instructions;counter=runtime.gpu_counter.value
            assert runtime.timer_run(c.byref(runtime.boot_bus),c.byref(runtime.gpu),100,return_pc)==0
            blocks=runtime.gpu_blocks;instructions=runtime.gpu.instructions-start;image=GPU.logical(runtime.gpu);assert runtime.gpu_counter.value==counter
            c.memmove(core.GPUGetRAM(),bytes(runtime.gpu.local_RAM),4096);mirror()
        runtime.gpu_trace,runtime.gpu_blocks=old_trace,old_blocks
        GPU_timers.append(dict(time_us=elapsed,return_PC=return_pc,blocks=blocks,instructions=instructions,PC_sha256=trace.hexdigest(),GPU_sha256=hashlib.sha256(image).hexdigest()))
    def complete(s):
        nonlocal asset_ticks,asset_first
        item=runtime.asset_disc.pending
        if not item:return
        if asset_first is None:asset_first=elapsed
        progress=runtime.device.read(0xbd848,4)
        if not core.JaguarCDHLEStreamActive()and progress>=item['destination_end']:
            data=runtime.device.ram()[item['destination_start']:item['destination_end']]
            item.update(sha256=hashlib.sha256(data).hexdigest(),main_callbacks_during_transfer=asset_ticks,first_clock_us=asset_first,last_clock_us=elapsed,completion_from_actual_source_progress=True)
            runtime.asset_disc.completions.append(dict(bytes=item['bytes'],progress_address=0xbd848,progress_value=progress,completion_by_source_VBI=True,main_callbacks_during_transfer=asset_ticks))
            runtime.HLE_asset_VBIs.append(dict(CPU=media.scheduler.cpu_dict(s),progress=progress,actual_main_queue=True))
            runtime.asset_disc.pending=None;asset_ticks=0;asset_first=None
    def boundary(self,s):
        nonlocal elapsed,main_events,jerry_events,asset_ticks
        target=self.startup_observed_CPU_cycles*0.07521368396;remaining=target-elapsed;assert remaining>=-1e-6,(target,elapsed);remaining=max(0,remaining)
        while remaining>0:
            times=[max(0.0,core.GetTimeToNextEvent(kind))for kind in [0,1]];kind=0 if times[0]<=times[1]else 1;due=times[kind]
            if due>remaining:
                for queue in [0,1]:core.SubtractEventTimes(remaining,queue)
                elapsed=target if stable else elapsed+remaining
                self.jerry_elapsed=jerry_origin+elapsed if stable else self.jerry_elapsed+remaining
                break
            core.SubtractEventTimes(due,1-kind);mirror();self.jerry_current_IRQs=[]
            pending=bool(self.asset_disc.pending and core.JaguarCDHLEStreamActive())
            if kind==0 and hasattr(self,'refresh_host_video_layout'):self.refresh_host_video_layout()
            core.HandleNextEvent(kind);assert not getattr(self,'OP_GPU_owner_errors',[]),getattr(self,'OP_GPU_owner_errors',[]);adopt();remaining-=due;elapsed+=due;self.jerry_elapsed=jerry_origin+elapsed if stable else self.jerry_elapsed+due
            assert not self.jerry_owner_error,self.jerry_owner_error
            if kind==0:
                main_events+=1
                # This is an event-call count, not a claim that every main
                # callback is a CD halfline tick. Actual bytes/hash gate it.
                if pending:asset_ticks+=1
                pump_timer()
            else:
                jerry_events+=1;self.engine_pump('JERRY_event_'+str(len(self.jerry_events)))
                self.jerry_events.append(dict(time_us=self.jerry_elapsed,IRQs=list(self.jerry_current_IRQs),PCM=music.dsp.strobed_pair(self.dac()),DSP_sha256=hashlib.sha256(self.logical_DSP()).hexdigest(),DAC_sha256=hashlib.sha256(self.dac()).hexdigest()))
            events_digest.update(struct.pack('>Id',kind,elapsed))
        complete(s)
    def sample(self,s):
        if (s.sr&0x0700)>=0x0200 or not core.TOMIRQRequestActive():return False
        raw=c.create_string_buffer(256);assert core.M68KStateSave(raw)==148
        deferred,queued=struct.unpack_from('=ii',raw.raw,140);level=queued if deferred else struct.unpack_from('=i',raw.raw,80)[0]
        if level<=((s.sr>>8)&7):return False
        assert level==2,level;before=media.scheduler.cpu_dict(s)
        core.m68k_set_irq(0);core.m68k_set_irq2(0)
        assert self.lib.biwn_vbi_event(c.byref(self.bus),c.byref(s))==0
        self.pending_CPU_IRQ_events.append(dict(CPU_before=before,CPU_after=media.scheduler.cpu_dict(s),source_handler=0xe7d4,frame_only=True))
        return True
    runtime.startup_before_instruction=types.MethodType(boundary,runtime)
    runtime.clock_tick=types.MethodType(lambda self:None,runtime)
    if runtime.mode=='C':runtime.sample_pending_CPU_IRQ=types.MethodType(sample,runtime)
    def finish():
        s=runtime.cpu()if runtime.mode=='native'else runtime.C_CPU;boundary(runtime,s)
        report=dict(status='candidate_instruction_boundary_main_JERRY_events',stable_target_clock=stable,CPU_cycles=runtime.startup_observed_CPU_cycles,elapsed_us=elapsed,main_events=main_events,JERRY_events=jerry_events,GPU_timers=GPU_timers,event_order_sha256=events_digest.hexdigest(),GPU_DSP_services_synchronous=True,instruction_boundary_event_delivery=True,global_cycle_scheduling_verified=False)
        (runtime.out/(runtime.mode+'-'+label+'-boundary-events.json')).write_text(json.dumps(report,indent=2)+'\n')
        del runtime.startup_before_instruction;runtime.clock_tick=clock_before
        if sample_before is not None:runtime.sample_pending_CPU_IRQ=sample_before
    runtime.finish_startup_boundary_events=finish
