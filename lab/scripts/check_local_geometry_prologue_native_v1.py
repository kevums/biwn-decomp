"""Actual68000 readable170A0 body with original copy/matrix helpers and GPU.

Full logical CPU/banks,2MBRAM/private guest frames and helper CPU boundaries.
Public data-bus order excludes only instruction fetch, supplied native context/
stack and the declared guest ABI stack, whose final bytes still compare.
"""
import argparse,ctypes as c,subprocess,os
from pathlib import Path
from datetime import datetime,timezone
import check_geometry_records_structured_host_v1 as host
from check_native_deck_coordinate_v1 import symbols
from check_native_scene_reset_core_bus_v1 import Event
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v35-local-record-prologue-v1'
CODE=0x180000;ARENA=0x1b0000;SLOTS=101;STRIDE=1024;OFFSET=144;LOWER=608;TOP=816;POOL=0xc0928
RANGES=[(0x170a0,0x17326),(0xe098,0xe0a6),(0xe220,0xe26c),(0xe3e0,0xe4aa)]

def pack(cpu):return b''.join(int(x).to_bytes(4,'big')for x in [*cpu.registers,cpu.pc,cpu.usp,cpu.ssp])+int(cpu.sr).to_bytes(2,'big')
def unpack(raw):
    cpu=host.CPU();cpu.registers[:]=[int.from_bytes(raw[i:i+4],'big')for i in range(0,64,4)]
    cpu.pc=int.from_bytes(raw[64:68],'big');cpu.usp=int.from_bytes(raw[68:72],'big');cpu.ssp=int.from_bytes(raw[72:76],'big');cpu.sr=int.from_bytes(raw[76:78],'big');return cpu

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
    model=read(V/'local-geometry-records-prologue-repair-v2-current.json');assert model['status']=='terminal_local_prologue_repair_v2_host_pass_native_pending_unpromoted'
    assert Path(model['accepted_composite']).read_bytes()==(SRC.parent.parent/'experimental/local-geometry-prologue-repair-v2/accepted-composite.inc').read_bytes()
    out=V/'local-geometry-prologue-native-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    state=dict(status='building',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,disc_changed=False)
    def mark():save(out/'protocol.json',state)
    mark();runtime=None
    try:
        gp=V/'geometry-records-structured-host-v1-current.json';g=read(gp);assert g['completed']==512
        for p,h in g['source_sha256'].items():assert sha(p)==h,p
        build=out/'build';q=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)],cwd=SRC,capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
        payload=(build/'native-shared.bin').read_bytes();syms=symbols(build/'symbols.txt')
        def symbol(name):
            values=[v for k,v in syms.items()if k==name or k.startswith(name+'.lto_priv.')];assert len(values)==1,(name,values);return values[0]
        entry=symbol('geometry_records_body');memory_symbol=symbol('memory');service=symbol('service_scene');assert CODE+len(payload)<ARENA
        session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'geometry-records-fullCPU-generation.json');resource=read(session/'resource-fullCPU-generation.json')
        runtime=host.Runtime(g['library'],mapping['instructions_decoded']+[x for x in resource['instructions_decoded']if 0xe3e0<=x['address']<0xe4aa]);core=runtime.core
        snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();vectors=[dict(x,body=True)for x in host.cases()]
        if args.limit:vectors=[vectors[i]for i in [0,1,32,33,64,65,96,97,128,129,130,131,159,160,161,162,163,164,192,255,256,511][:args.limit]]
        core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.vjtrace_watch_add.restype=c.c_int
        def arm():
            core.vjtrace_disarm();core.vjtrace_watch_clear()
            for lo,hi in [(0,CODE-1),(CODE+len(payload),ARENA-1),(ARENA+SLOTS*STRIDE,0x1fffff),(0xf03200,0xf0321f)]:
                if lo<=hi:assert core.vjtrace_watch_add(lo,hi,3)>=0
            start=core.vjtrace_ring_head();core.vjtrace_arm();return start
        def events(start,guest_sp):
            core.vjtrace_disarm();data=[]
            for n in range(start,core.vjtrace_ring_head()):
                e=Event();assert core.vjtrace_ring_read(n,c.byref(e))
                if e.type not in [11,12]or e.who!=6:continue
                if any(lo<=e.addr<hi for lo,hi in RANGES)or host.STOP<=e.addr<host.STOP+4:continue
                if guest_sp-512<=e.addr<guest_sp+8:continue
                # Capture/return assembly has additional ABI bookkeeping.
                if CODE<=e.pc<syms['midpoint']:continue
                data.append(['r'if e.type==11 else'w',e.addr,None if e.type==11 else e.value])
            return data
        # The originalGPU provider owns a short trace and leaves it disarmed.
        # Resume this CPU observer after that provider; fail if any CPU executes
        # outside the observer's armed interval.
        device_write=runtime.device.write;cpu_execute=core.m68k_execute
        def traced_write(address,value):
            device_write(address,value)
            if address==0xf03204 and value==0x4320:core.vjtrace_arm()
        def traced_execute(count):
            assert c.c_int.in_dll(core,'vjtrace_armed').value==1,'CPU trace unexpectedly disarmed'
            return cpu_execute(count)
        runtime.device.write=traced_write;core.m68k_execute=traced_execute
        rows=[];coverage=set();maximum=0
        for i,case in enumerate(vectors):
            slot=ARENA+(i%SLOTS)*STRIDE;ctx=slot+OFFSET;csp=slot+TOP-8;task=POOL+(i%SLOTS)*STRIDE
            initial=host.queue.make_cpu(case);memory=bytearray(host.fixture(snapshot,case));memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
            memory[0xc0920:0xc0924]=task.to_bytes(4,'big')
            memory[ctx:ctx+118]=memory_symbol.to_bytes(4,'big')+pack(initial)+service.to_bytes(4,'big')+ctx.to_bytes(4,'big')+(0xffffffff).to_bytes(4,'big')+bytes(4)+bytes(16)+(1).to_bytes(4,'big')
            memory[csp:csp+8]=host.STOP.to_bytes(4,'big')+ctx.to_bytes(4,'big');ram=bytes(memory)
            # Both lanes start observation after emulator reset and full CPU seed.
            # Reset-vector reads are setup, not instructions of either body.
            seed_cpu=host.lifecycle.seed_cpu;reference_trace=[]
            def seed_and_arm(observer,cpu):
                seed_cpu(observer,cpu);reference_trace.append(arm())
            host.lifecycle.seed_cpu=seed_and_arm
            try:left,expected,original=runtime.native(ram,case,coverage)
            finally:host.lifecycle.seed_cpu=seed_cpu
            assert len(reference_trace)==1
            original_bus=events(reference_trace[0],initial.registers[15])
            runtime.reset(ram,case,0);physical=host.queue.make_cpu(case);physical.pc=entry;physical.registers[15]=csp;physical.sr=case['SR']&0xfff0
            if physical.sr&0x2000:physical.ssp=csp
            else:physical.usp=csp
            host.lifecycle.seed_cpu(runtime,physical);start=arm();low=TOP;calls=[];stack=[];pending=None
            for steps in range(2000000):
                current=runtime.cpu();pc=current.pc;sp=current.registers[15]
                if pc==host.STOP:break
                if CODE<=pc<CODE+len(payload):
                    helper_return=syms['biwn_v4_scene_helper_return'];capture_end=syms['biwn_v4_scene_capture_end']
                    transfer={syms[name]+delta for name in ['biwn_v4_capture_scene_record_copy','biwn_v4_capture_scene_record_matrix']for delta in [40,44,48]}
                    if pc in transfer:assert sp==runtime.device.read(ctx+106,4),('guest transfer SP',hex(pc),hex(sp))
                    elif pc==helper_return:assert sp==runtime.device.read(ctx+106,4)+4,('helper RTS SP',hex(sp))
                    elif pc==helper_return+6:assert sp==task,('SP-only task lookup',hex(sp))
                    elif helper_return+12<=pc<capture_end:
                        displacement={12:0,16:0,20:64}.get(pc-helper_return,4)
                        assert sp==ctx+displacement,('captured CPU lookup SP',hex(pc),hex(sp))
                    else:
                        low=min(low,sp-slot);assert slot+LOWER<=sp<=slot+TOP,('C stack outside',i,hex(pc),sp-slot)
                else:assert pc in runtime.rows and not 0x170a0<=pc<0x17326,('Original record body executed or unexpected PC',hex(pc))
                if pc in [0xe3e0,0xe220]or pending==pc:
                    row=dict(target=pc,actual_body=True,incoming=host.cd.scheduler.cpu_dict(current));calls.append(row);stack.append(row);pending=None
                if pc in host.queue.RETURNS and stack:stack.pop()['return']=host.cd.scheduler.cpu_dict(current)
                source=runtime.rows.get(pc)
                if source and source['assembly'].startswith('jsr '):
                    target=int(source['assembly'].split('$')[1].split('.')[0],16);pending=target if target==0xe098 else None
                core.m68k_execute(1)
                if core.GPUReadLong(0xf03204,0)==0x4320:runtime.device.write(0xf03204,0x4320)
            else:raise AssertionError('Native record body instruction bound')
            native_bus=events(start,initial.registers[15]);right=runtime.device.ram();actual=unpack(right[ctx+4:ctx+82]);error=int.from_bytes(right[ctx+94:ctx+98],'big');maximum=max(maximum,TOP-low)
            def normal(raw):
                value=bytearray(raw)
                for lo,hi in [(ctx,ctx+118),(slot+LOWER,slot+TOP)]:value[lo:hi]=ram[lo:hi]
                return bytes(value)
            if error or bytes(expected)!=bytes(actual)or normal(left)!=normal(right)or original_bus!=native_bus or calls!=original['calls']:
                save(out/'counterexample.json',dict(case=case,native_error=error,expected_CPU=host.cd.scheduler.cpu_dict(expected),actual_CPU=host.cd.scheduler.cpu_dict(actual),RAM_differences=[hex(j)for j,(a,b)in enumerate(zip(normal(left),normal(right)))if a!=b][:32],original_bus=original_bus,native_bus=native_bus,original_calls=original['calls'],native_calls=calls,C_stack_bytes=TOP-low))
                raise AssertionError(out/'counterexample.json')
            assert not stack and current.registers[15]==csp+4
            rows.append(dict(case=case['id'],CCR=case['SR']&31,supervisor=bool(case['SR']&0x2000),native_instructions=steps,C_stack_bytes=TOP-low,actual_helper_calls=len(calls),public_bus_events=len(native_bus),full_CPU_nonprivate_RAM_helper_states_public_bus_match=True));state.update(status='checking',completed=len(rows));mark()
            if len(rows)%16==0:print('Native records',len(rows),'/',len(vectors),flush=True)
        save(out/'cases.json',rows)
        paths=[Path(__file__),Path(host.__file__),gp,*SRC.glob('*'),ROOT/'projects/black-ice-white-noise/restoration/experimental/local-geometry-prologue-repair-v2/accepted-composite.inc',build/'native-shared.bin',build/'symbols.txt',out/'cases.json']
        state.update(status='terminal_readable_records_native_preflight'if args.limit else'terminal_readable_records_native_CPU_RAM_helper_states_and_public_bus_pass',payload=str(build/'native-shared.bin'),payload_sha256=sha(build/'native-shared.bin'),payload_bytes=len(payload),symbols=syms,maximum_C_stack_bytes=maximum,C_stack_reserved=208,body_only=True,task_slots=len({i%SLOTS for i in range(len(rows))}),original_record_instructions_executed=0,
            source_sha256={str(p):sha(p)for p in paths if p.is_file()},scope=__doc__+' Physical CLR bus effects compare. Guest stack final bytes are checked, but extra capture/return ABI bus operations are excluded from public bus traces. Original E3E0/E220/E098 and declared synchronous originalGPU4320 provider execute; no original170A0instructions on native lane. No connected scene, final disc, asynchronous device, arbitrary IRQ or console proof.')
        mark()
        if not args.limit:save(V/'local-geometry-prologue-native-v1-current.json',state)
        print(state['status'],len(rows),'stack',maximum,'module',len(payload),flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:
        if runtime:runtime.core.vjtrace_disarm();runtime.close()

if __name__=='__main__':main()
