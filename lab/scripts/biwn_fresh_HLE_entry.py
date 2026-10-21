"""Game180000->4000 on a freshly loaded HLE platform, without a savestate.

The platform boot loader and CD APIs remain the existing emulator's HLE.
Original CPU/GPU opcodes are forbidden on the C game path. Event quanta are
supplied at source CD polls; this is not global cycle scheduling.
"""
import ctypes as c
import hashlib
import json
from pathlib import Path
import check_biwn_media_setup_cpu as media
import check_biwn_movie_GPU as GPU
from check_biwn_game_firstboot_GPU import Bus as GPUBus
from check_biwn_main_GPU_boot import W16

ROOT=Path(__file__).resolve().parents[1]


def run(core,ram_pointer,out,mode,cycle_clock=False):
    proof=json.loads((ROOT/'verification/header-handoff-tail-current.json').read_text())
    library=Path(proof['directory'])/'libhandoff.dylib'
    functions=c.CDLL(str(library)); errors=[]; trace=hashlib.sha256(); GPU_trace=[]; GPU_calls=[]; API_calls=[]; events=[]
    counts={'CPU_steps':0,'HLE_RTS':0,'main_events':0,'stream_ticks':0}
    for bits,typ in [(8,c.c_uint8),(16,c.c_uint16),(32,c.c_uint32)]:
        fn=getattr(core,'m68k_read_memory_'+str(bits));fn.argtypes=[c.c_uint32];fn.restype=typ
        getattr(core,'m68k_write_memory_'+str(bits)).argtypes=[c.c_uint32,c.c_uint32]
    core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    core.GPUReadWord.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadWord.restype=c.c_uint16
    core.GPUReadLong.argtypes=[c.c_uint32,c.c_uint32];core.GPUReadLong.restype=c.c_uint32
    core.GPUWriteWord.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    core.GPUExec.argtypes=[c.c_int32];core.m68k_execute.argtypes=[c.c_int32]
    core.GetTimeToNextEvent.argtypes=[c.c_int];core.GetTimeToNextEvent.restype=c.c_double
    core.HandleNextEvent.argtypes=[c.c_int]
    core.JaguarCDHLEHook.argtypes=[c.c_uint32];core.JaguarCDHLEHook.restype=c.c_bool
    prefix=(c.c_uint32*18).in_dll(core,'regs')
    def CPU():
        s=media.CPU();s.registers[:]=[core.m68k_get_reg(None,i) for i in range(16)]
        s.pc=core.m68k_get_reg(None,16);s.sr=core.m68k_get_reg(None,17)
        s.usp=prefix[16] if s.sr&0x2000 else s.registers[15]
        s.ssp=s.registers[15] if s.sr&0x2000 else prefix[17]
        return s
    def set_API_shadow(s):
        # No reset/opcode execution: existing HLE APIs read this native ABI.
        core.m68k_set_reg.argtypes=[c.c_int,c.c_uint32]
        core.m68k_set_reg(17,0x2000);core.m68k_set_reg(15,s.ssp)
        core.m68k_set_reg(17,0);core.m68k_set_reg(15,s.usp)
        core.m68k_set_reg(17,s.sr)
        for i,v in enumerate(s.registers):core.m68k_set_reg(i,v)
        core.m68k_set_reg(16,s.pc)
    def raw_gpu():
        b=c.create_string_buffer(12000);assert core.GPUStateSave(b)==4416;return b.raw[:4416]
    s=CPU();assert s.pc==0x180000,hex(s.pc);initial_CPU=bytes(s);g=GPU.state_from_raw(raw_gpu())
    initial_GPU_counter=c.c_uint32.in_dll(core,'gpu_exec_opcode_count').value
    initial_DSP_counter=c.c_uint32.in_dll(core,'dsp_exec_opcode_count').value
    def mirror():
        if mode=='C':
            raw=raw_gpu();image=GPU.logical(g)+raw[4396:];assert core.GPUStateLoad(c.create_string_buffer(image))==4416
    def adopt_GPU_changes():
        if mode=='C':
            old=g.instructions;updated=GPU.state_from_raw(raw_gpu());c.memmove(c.byref(g),c.byref(updated),c.sizeof(g));g.instructions=old
    def reader(width):
        def cb(_,a,v):
            try:
                if mode=='C' and 0xf03000<=a<=0xf04000-width:
                    v[0]=int.from_bytes(bytes(g.local_RAM[a-0xf03000:a-0xf03000+width]),'big')
                elif mode=='C' and a==0xf02114 and width==4:v[0]=g.control
                elif mode=='C' and a==0xf02100 and width==4:v[0]=g.flags&0xffffc1ff
                else:v[0]=getattr(core,'m68k_read_memory_'+str(width*8))(a)
                return 0
            except BaseException as e:errors.append(repr(e));return 1
        return cb
    def writer(width):
        def cb(_,a,v):
            try:
                getattr(core,'m68k_write_memory_'+str(width*8))(a,v)
                if mode=='C':
                    if 0xf03000<=a<=0xf04000-width:g.local_RAM[a-0xf03000:a-0xf03000+width]=v.to_bytes(width,'big')
                    if width==4:
                        if a==0xf02100:
                            g.flags=(v&~8)|((v&8)&g.flags);g.z=v&1;g.c=(v>>1)&1;g.n=(v>>2)&1;g.active_bank=0 if g.flags&8 else int(bool(v&0x4000))
                        elif a==0xf0210c:g.data_organization=v
                        elif a==0xf02110:g.pc=v
                        elif a==0xf02114:g.control=(g.control&0xf7c0)|(v&~0xf7c6)
                return 0
            except BaseException as e:errors.append(repr(e));return 1
        return cb
    world=media.scheduler.cleanup.world
    callbacks=[world.R8(reader(1)),world.R16(reader(2)),world.R32(reader(4)),world.W16(writer(2)),world.W32(writer(4)),media.W8(writer(1))]
    bus=media.Bus(*callbacks[:5],world.CALL(),None,0)
    service=media.world_cpu.SERVICE(lambda _,b,p,target:0 if target==p.contents.pc else 3)
    step=functions.biwn_handoff_game_cpu_call
    step.argtypes=[c.POINTER(media.Bus),c.POINTER(media.CPU),media.W8,media.world_cpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];step.restype=c.c_int
    gpu_callbacks=[GPU.R8(lambda _,a,v:(v.__setitem__(0,core.m68k_read_memory_8(a)),0)[1]),
        GPU.R16(lambda _,a,v:(v.__setitem__(0,core.GPUReadWord(a,3)),0)[1]),
        GPU.R32(lambda _,a,v:(v.__setitem__(0,core.GPUReadLong(a,3)),0)[1]),
        W16(lambda _,a,v:(core.GPUWriteWord(a,v,3),0)[1]),
        GPU.W32(lambda _,a,v:(core.GPUWriteLong(a,v,3),0)[1]),GPU.OBS(lambda _,pc:GPU_trace.append(pc))]
    gpu_bus=GPUBus(*gpu_callbacks,None);gpu_run=functions.biwn_game_firstboot_GPU_run
    gpu_run.argtypes=[c.POINTER(GPUBus),c.POINTER(GPU.State),c.c_uint32,c.c_uint32];gpu_run.restype=c.c_int
    core.SubtractEventTimes.argtypes=[c.c_double,c.c_int]
    cycle_total=0;elapsed_us=0.0;bus_wait_cycles=0;bus_wait_instructions=0;slice_end_bookkeeping_cycles=0
    core.m68k_cycles_run.restype=c.c_int
    if cycle_clock:
        from biwn_m68k_cycle_cost import Cost
        cost=Cost(lambda a,w:int.from_bytes(c.string_at(ram_pointer+a,w),'big'))
    def advance_cycles(cycles):
        nonlocal cycle_total,elapsed_us
        cycle_total+=cycles;remaining=cycles*(0.03760684198*2) # pinned NTSC event.h
        while remaining>0:
            due=core.GetTimeToNextEvent(0)
            assert due>=-0.001,due
            due=max(0.0,due)
            if due>remaining:
                core.SubtractEventTimes(remaining,0);elapsed_us+=remaining;break
            main_event();remaining-=due;elapsed_us+=due
    def main_event():
        mirror();due=core.GetTimeToNextEvent(0);core.HandleNextEvent(0);adopt_GPU_changes();counts['main_events']+=1
        if len(events)<16:events.append(due)
    def pump(stop):
        GPU_trace.clear();begin=g.instructions;delays=0
        if mode=='native':
            for _ in range(2000000):
                pc=core.GPUGetPC()
                if pc==stop:break
                word=core.GPUReadWord(pc,3);GPU_trace.append(pc);core.GPUExec(1)
                if word>>10 in [52,53] and core.GPUGetPC()!=pc+2:delays+=1
            else:raise AssertionError(('native GPU bound',hex(core.GPUGetPC())))
            instructions=len(GPU_trace)+delays
        else:
            status=gpu_run(c.byref(gpu_bus),c.byref(g),2000000,stop)
            assert status==0,('C GPU',status,hex(g.pc));instructions=g.instructions-begin;mirror()
        state=raw_gpu()[:4396] if mode=='native' else GPU.logical(g)
        GPU_calls.append(dict(stop=hex(stop),instructions=instructions,trace_sha256=hashlib.sha256(b''.join(p.to_bytes(4,'big') for p in GPU_trace)).hexdigest(),GPU_sha256=hashlib.sha256(state).hexdigest()))
    try:
        for _ in range(6000000 if cycle_clock else 2000000):
            pc=CPU().pc if mode=='native' else s.pc
            if pc==0x4000:break
            trace.update(pc.to_bytes(4,'big'));counts['CPU_steps']+=1
            before=CPU()if mode=='native'else s
            if cycle_clock:
                opcode=int.from_bytes(c.string_at(ram_pointer+pc,2),'big');predicted,_=cost.predict(opcode,before)
                shadow_bus_before=core.m68k_cycles_run()if mode=='C'else None
            if pc==0x1800c8:
                # A declared main-event quantum, shared by both references.
                if not cycle_clock:
                    for _ in range(4):main_event()
                pump(0xf032ce)
            if pc==0x304e and not cycle_clock:main_event()
            if pc==0x180178:
                pump(0xf03328)
            if 0x3000<=pc<=0x306b:
                counts['HLE_RTS']+=1
                if len(API_calls)<16:API_calls.append(dict(target=hex(pc),CPU_before=media.scheduler.cpu_dict(CPU() if mode=='native' else s)))
                if mode=='C':
                    shadow=CPU();mirror();set_API_shadow(s);core.JaguarCDHLEHook(pc);updated=CPU();set_API_shadow(shadow);s=updated;adopt_GPU_changes()
                    assert core.m68k_read_memory_16(pc)==0x4e75
                    s.pc=core.m68k_read_memory_32(s.registers[15]);s.registers[15]+=4
                    if s.sr&0x2000:s.ssp=s.registers[15]
                    else:s.usp=s.registers[15]
                    if cycle_clock:
                        waits=core.m68k_cycles_run()-shadow_bus_before;assert 0<=waits<=1024,('C ABI bus charge',waits)
                        bus_wait_cycles+=waits;bus_wait_instructions+=bool(waits);advance_cycles(predicted+waits)
                    continue
            if mode=='native':
                actual=core.m68k_execute(1)
                if cycle_clock:
                    bookkeeping=0
                    # GPUWriteLong(G_CTRL,GO) ends the timeslice. With a
                    # one-cycle request, m68k_end_timeslice resets remaining
                    # to0 before opcode cost subtraction, yielding base+1.
                    # That request-budget artifact is not a retired cycle.
                    if actual==predicted+1 and opcode==0x23fc and int.from_bytes(c.string_at(ram_pointer+pc+6,4),'big')==0xf02114 and int.from_bytes(c.string_at(ram_pointer+pc+2,4),'big')&1:
                        bookkeeping=1;slice_end_bookkeeping_cycles+=1
                    waits=actual-predicted-bookkeeping;assert 0<=waits<=1024,('native extra bus/exception charge',hex(pc),actual,predicted)
                    bus_wait_cycles+=waits;bus_wait_instructions+=bool(waits)
            else:
                status=step(c.byref(bus),c.byref(s),callbacks[5],service,None,1,0)
                assert status in [0,4,8] and not errors,(hex(pc),status,errors)
            if cycle_clock:
                if mode=='C':
                    waits=core.m68k_cycles_run()-shadow_bus_before;assert 0<=waits<=1024,('C instruction bus charge',hex(pc),waits)
                    bus_wait_cycles+=waits;bus_wait_instructions+=bool(waits)
                advance_cycles(predicted+waits)
        else:raise AssertionError(('CPU entry bound',hex(CPU().pc if mode=='native' else s.pc)))
        final=CPU() if mode=='native' else s;image=c.string_at(ram_pointer,0x200000)
        assert hashlib.sha256(image[0x4000:0x100000]).hexdigest()=='52dc987c755b711390dc46353e552b8038a97f9993bbab08947a85d8b033b453'
        if mode=='C':
            assert bytes(CPU())==initial_CPU
            assert c.c_uint32.in_dll(core,'gpu_exec_opcode_count').value==initial_GPU_counter
        assert c.c_uint32.in_dll(core,'dsp_exec_opcode_count').value==initial_DSP_counter
        (out/(mode+'-entry-RAM.bin')).write_bytes(image)
        core._biwn_fresh_entry_CPU=final
        core._biwn_fresh_entry_GPU=g if mode=='C' else None
        core._biwn_read_CPU=CPU
        def platform_API_body(cpu):
            shadow=CPU();set_API_shadow(cpu);core.JaguarCDHLEHook(cpu.pc)
            result=CPU();set_API_shadow(shadow);c.memmove(c.byref(cpu),c.byref(result),c.sizeof(cpu))
            return 0
        core._biwn_HLE_API_body=platform_API_body
        return dict(mode=mode,counts=counts,CPU=media.scheduler.cpu_dict(final),RAM_sha256=hashlib.sha256(image).hexdigest(),
            logical_GPU_sha256=hashlib.sha256(raw_gpu()[:4396] if mode=='native' else GPU.logical(g)).hexdigest(),
            CPU_trace_sha256=trace.hexdigest(),GPU_calls=GPU_calls,API_calls=API_calls,first_event_times=events,
            initial_capture_loaded=False,platform_HLE_retained=True,source_C_game=mode=='C',
            supplied_main_event_quanta=not cycle_clock,CPU_cycle_driven_main_events=cycle_clock,CPU_cycles=cycle_total,native_slice_end_bookkeeping_cycles_excluded=slice_end_bookkeeping_cycles,shared_bus_extra_cycles=bus_wait_cycles,shared_bus_charged_instructions=bus_wait_instructions,CPU_elapsed_us=elapsed_us,NTSC_M68K_cycle_us=0.03760684198*2 if cycle_clock else None,GPU_execution_still_synchronous=True,JERRY_events_still_held=True,ordinary_firmware_boot=False,whole_game_complete=False)
    except BaseException as e:
        (out/(mode+'-entry-failure.json')).write_text(json.dumps(dict(error=repr(e),PC=hex(CPU().pc if mode=='native' else s.pc),counts=counts,errors=errors),indent=2)+'\n')
        raise
