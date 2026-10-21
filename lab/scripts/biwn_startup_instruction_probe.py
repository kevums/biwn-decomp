"""Read-only DD40 startup instruction coverage; no timing/coverage claims."""
import ctypes as c
import collections,hashlib,json,types,struct,sys
from array import array
def big_endian(values):
    copy=array("I",values)
    if sys.byteorder=="little":copy.byteswap()
    return copy.tobytes()
import check_biwn_media_setup_cpu as media

def install(runtime,state_trace=False,cost_trace=False,label="startup"):
    counts=collections.Counter();trace=array("I");digest=hashlib.sha256();errors=[];state_digest=hashlib.sha256();state_hashes=bytearray()
    costs=array("I");actual_costs=array("I");cost_digest=hashlib.sha256()
    runtime.startup_observed_CPU_cycles=0
    runtime.startup_observed_IRQ_entries=0
    if cost_trace:
        from biwn_m68k_cycle_cost import Cost
        cost=Cost(lambda a,w:int.from_bytes(c.string_at(runtime.device.pointer+a,w),'big'))
    def observe(s):
        if runtime.mode=='native'and hasattr(runtime,'on_native_source_instruction'):runtime.on_native_source_instruction(s)
        pc=int(s.pc);counts[pc]+=1;trace.append(pc);digest.update(pc.to_bytes(4,'big'))
        if state_trace:
            data=struct.pack('>19IH',*s.registers,s.pc,s.usp,s.ssp,s.sr);state_digest.update(data);state_hashes.extend(hashlib.sha256(data).digest())
        if cost_trace:
            opcode=int.from_bytes(c.string_at(runtime.device.pointer+pc,2),'big')
            cycles,family=cost.predict(opcode,s)
            costs.extend((pc,cycles));cost_digest.update(struct.pack('>II',pc,cycles))
            runtime.startup_observed_CPU_cycles+=cycles
            if pc==0xe7d4:
                runtime.startup_observed_CPU_cycles+=56
                runtime.startup_observed_IRQ_entries+=1
    if runtime.mode=='native':
        original=runtime.core.m68k_execute;q=(c.c_uint32*1024).in_dll(runtime.core,'pcQueue');index=c.c_uint32.in_dll(runtime.core,'pcQPtr')
        ARM=c.CFUNCTYPE(None,c.c_uint32,c.c_uint32)
        if state_trace:
            def callback(previous,pc):
                try:observe(runtime.cpu())
                except BaseException as error:errors.append(repr(error))
            cb=ARM(callback);arm=runtime.core.BIWNArmCPUObserver;arm.argtypes=[c.c_uint32,ARM]
            runtime.core.M68KStateSave.argtypes=[c.c_void_p];runtime.core.M68KStateSave.restype=c.c_size_t
        def execute(budget):
            before=index.value
            if state_trace:
                s=runtime.cpu();raw=c.create_string_buffer(256);assert runtime.core.M68KStateSave(raw)==148
                deferred,queued=struct.unpack_from('=ii',raw.raw,140);level=queued if deferred else struct.unpack_from('=i',raw.raw,80)[0]
                target=0xe7d4 if level>((s.sr>>8)&7)and(level==2)and(deferred or runtime.core.TOMIRQRequestActive())else s.pc
                previous_count=len(trace);arm(target,cb)
            result=original(budget);after=index.value
            if cost_trace:actual_costs.append(result)
            assert (after-before)&1023==1,('startup probe step boundary',before,after,budget)
            pc=q[(after-1)&1023]
            runtime.last_startup_executed_PC=int(pc)
            if state_trace:
                arm(0,ARM());assert len(trace)==previous_count+1 and trace[-1]==pc,('actual startup instruction observer missed',hex(target),hex(pc))
            else:counts[pc]+=1;trace.append(pc);digest.update(pc.to_bytes(4,'big'))
            return result
        runtime.core.m68k_execute=execute
        def disable():runtime.core.m68k_execute=original
    else:
        OBS=c.CFUNCTYPE(None,c.c_void_p)
        def callback(ptr):
            try:observe(c.cast(ptr,c.POINTER(media.CPU)).contents)
            except BaseException as error:errors.append(repr(error))
        cb=OBS(callback);setter=runtime.lib.biwn_set_instruction_observer;setter.argtypes=[OBS];setter.restype=None;setter(cb)
        old_bios=runtime.bios;old_provider=runtime.startup_provider
        def bios(self,s,target):
            if target==0x304e:observe(s)
            return old_bios(s,target)
        def provider(self,s,target):
            if target in [0x303c,0x3042,0x4088]:observe(s)
            return old_provider(s,target)
        runtime.bios=types.MethodType(bios,runtime);runtime.startup_provider=types.MethodType(provider,runtime)
        def disable():setter(OBS());runtime.bios=old_bios;runtime.startup_provider=old_provider
    def finish():
        disable();assert not errors,errors
        report=dict(instructions=len(trace),unique_PCs=len(counts),PC_counts={hex(k):v for k,v in sorted(counts.items())},PC_trace_sha256=digest.hexdigest(),errors=errors,read_only=True,full_CPU_state_trace=state_trace,CPU_state_trace_sha256=state_digest.hexdigest()if state_trace else None,global_cycle_scheduling_verified=False)
        (runtime.out/(runtime.mode+'-'+label+'-instruction-probe.json')).write_text(json.dumps(report,indent=2)+'\n')
        (runtime.out/(runtime.mode+'-'+label+'-instruction-PCs.bin')).write_bytes(big_endian(trace))
        if state_trace:(runtime.out/(runtime.mode+'-'+label+'-CPU-state-hashes.bin')).write_bytes(state_hashes)
        if cost_trace:
            cost_report=dict(status='instruction_cost_probe_only',instructions=len(costs)//2,predicted_cycles=sum(costs[1::2]),PC_cost_sha256=cost_digest.hexdigest(),original_execute_cycles=sum(actual_costs)if runtime.mode=='native'else None,global_cycle_scheduling_verified=False)
            (runtime.out/(runtime.mode+'-'+label+'-instruction-costs.json')).write_text(json.dumps(cost_report,indent=2)+'\n')
            (runtime.out/(runtime.mode+'-'+label+'-instruction-costs.bin')).write_bytes(big_endian(costs))
            if actual_costs:(runtime.out/(runtime.mode+'-'+label+'-original-cycle-costs.bin')).write_bytes(big_endian(actual_costs))
        return report
    runtime.finish_startup_instruction_probe=finish
    runtime._startup_instruction_callback=cb if runtime.mode=='C'else None
