"""Compiled185B2body in shared module: logicalCPU,2MBRAM and scoped actual data-bus ordering.
Direct C entry only: parent scene/capture integration and final disc are separate.
"""
import argparse,ctypes as c,json,os,subprocess
from pathlib import Path
from datetime import datetime,timezone
import scene_display_list_mutation_vectors_v2 as fixtures
from check_native_scene_reset_core_bus_v1 import Event
from check_native_deck_coordinate_v1 import symbols
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
h=fixtures.parent;base=h.base
SRC=ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v37-record-loop-advance-v2'
_BUILD=read(V/'native-record-loop-image-disc-build-v1-current.json');CODE=_BUILD['shared_Deck_code_address'];ARENA=_BUILD['deck_arena_address'];SLOTS=101;STRIDE=1024;OFFSET=144;LOWER=608;TOP=816

def pack(cpu):
    return b''.join(int(x).to_bytes(4,'big')for x in list(cpu.registers)+[cpu.pc,cpu.usp,cpu.ssp])+int(cpu.sr).to_bytes(2,'big')
def unpack(raw):
    cpu=base.CPU();cpu.registers[:]=[int.from_bytes(raw[i:i+4],'big')for i in range(0,64,4)];cpu.pc=int.from_bytes(raw[64:68],'big');cpu.usp=int.from_bytes(raw[68:72],'big');cpu.ssp=int.from_bytes(raw[72:76],'big');cpu.sr=int.from_bytes(raw[76:78],'big');return cpu

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);args=ap.parse_args()
    out=V/'record-loop-image-final-display-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);pointer=V/'record-loop-image-final-display-v1-current.json';state=dict(status='building',directory=str(out),pid=os.getpid(),completed=0,new_predictions=0,new_training=False,game_image_changed=False)
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark();runtime=None
    try:
        build=out/'build';q=subprocess.run(['make','BUILD='+str(build),'ADDRESS='+hex(CODE),'ARENA_ADDRESS='+hex(ARENA)],cwd=SRC,capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
        payload=(build/'native-shared.bin').read_bytes();resident=Path(_BUILD['component']).read_bytes();assert payload==resident[CODE-_BUILD['resident_address']:CODE-_BUILD['resident_address']+len(payload)];syms=symbols(build/'symbols.txt');assert CODE+len(payload)<ARENA;entries=[v for k,v in syms.items()if k=='scene_display_list_body'or k.startswith('scene_display_list_body.lto_priv.')];assert len(entries)==1;entry=entries[0];assert CODE<=entry<CODE+len(payload)
        parent=read(V/'scene-display-list-algorithm-host-v2-current.json');assert parent['completed']==1217;session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'display-list-fullCPU-generation.json');runtime=h.Runtime(parent['library'],mapping['instructions_decoded']);core=runtime.core;snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
        # Body mode removes duplicate full-call variants from the added CCR matrix.
        vectors=base.cases(snapshot)
        for old in h.cases(snapshot)[1025:1089]:vectors.append(old)
        vectors+=fixtures.cases(snapshot);assert len(vectors)==1153
        vectors=[dict(x,body=True,read_queues=[])for x in vectors];vectors=vectors[:args.limit]if args.limit else vectors
        core.vjtrace_ring_head.restype=c.c_uint64;core.vjtrace_ring_read.argtypes=[c.c_uint64,c.POINTER(Event)];core.vjtrace_ring_read.restype=c.c_int;core.vjtrace_watch_add.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.vjtrace_watch_add.restype=c.c_int
        def arm():
            core.vjtrace_disarm();core.vjtrace_watch_clear()
            # Exclude native code fetch/literals and all private arenas at the recorder.
            for lo,hi in [(0,CODE-1),(CODE+len(payload),ARENA-1),(ARENA+SLOTS*STRIDE,0x1fffff)]:
                if lo<=hi:assert core.vjtrace_watch_add(lo,hi,3)>=0
            begin=core.vjtrace_ring_head();core.vjtrace_arm();return begin
        def events(begin,original=False):
            core.vjtrace_disarm();rows=[]
            for n in range(begin,core.vjtrace_ring_head()):
                e=Event();assert core.vjtrace_ring_read(n,c.byref(e))
                if e.type not in [11,12]or e.who!=6:continue
                if original and not 0x185b2<=e.pc<=0x18852:continue
                # Original instruction fetches are omitted; actual source-table reads remain.
                if 0x185b2<=e.addr<0x18860 and not 0x18690<=e.addr<0x1869a:continue
                if base.STOP<=e.addr<base.STOP+4:continue
                rows.append(['r'if e.type==11 else'w',e.addr,None if e.type==11 else e.value])
            return rows
        rows=[];maximum=0;coverage=set()
        for i,case in enumerate(vectors):
            slot=ARENA+(i%SLOTS)*STRIDE;ctx=slot+OFFSET;csp=slot+TOP-8;memory=bytearray(base.fixture(snapshot,case));memory[CODE:CODE+len(payload)]=payload;memory[ARENA:ARENA+SLOTS*STRIDE]=bytes([0xa5])*(SLOTS*STRIDE)
            initial=base.queue.make_cpu(case);memory[ctx:ctx+98]=next(v for k,v in syms.items()if k=='memory'or k.startswith('memory.lto_priv.')).to_bytes(4,'big')+pack(initial)+bytes(16);memory[csp:csp+8]=base.STOP.to_bytes(4,'big')+ctx.to_bytes(4,'big');ram=bytes(memory)
            begin=arm();left,expected,original=runtime.native(ram,case,coverage);original_bus=events(begin,True)
            runtime.reset(ram,case,0);physical=base.queue.make_cpu(case);physical.pc=entry;physical.registers[15]=csp;physical.sr=case['SR']&0x2000
            if physical.sr:physical.ssp=csp
            else:physical.usp=csp
            base.queue.lifecycle.seed_cpu(runtime,physical);begin=arm();low=TOP
            for steps in range(200000):
                current=runtime.cpu();pc=current.pc
                if pc==base.STOP:break
                assert CODE<=pc<CODE+len(payload),('target escapes compiled module',hex(pc))
                low=min(low,current.registers[15]-slot)
                assert current.registers[15]>=slot+LOWER,('Cstack outside',i,current.registers[15]-slot)
                core.m68k_execute(1)
            else:raise AssertionError('target body instruction limit')
            compiled_bus=events(begin);right=runtime.device.ram();actual=unpack(right[ctx+4:ctx+82]);error=int.from_bytes(right[ctx+94:ctx+98],'big');maximum=max(maximum,TOP-low)
            def normal(raw):
                value=bytearray(raw)
                for lo,hi in [(ctx,ctx+98),(slot+LOWER,slot+TOP)]:value[lo:hi]=ram[lo:hi]
                return bytes(value)
            valid=not error and bytes(expected)==bytes(actual) and normal(left)==normal(right) and original_bus==compiled_bus
            if not valid:
                save(out/'counterexample.json',dict(case=case,native_error=error,expected_CPU=base.queue.cd.scheduler.cpu_dict(expected),actual_CPU=base.queue.cd.scheduler.cpu_dict(actual),CPU_differences={k:v for k,v in base.queue.cd.scheduler.cpu_dict(actual).items()if v!=base.queue.cd.scheduler.cpu_dict(expected)[k]},original_bus=original_bus,native_bus=compiled_bus,RAM_differences=[hex(n)for n,(a,b)in enumerate(zip(normal(left),normal(right)))if a!=b][:32],C_stack_bytes=TOP-low))
                raise AssertionError(out/'counterexample.json')
            assert current.registers[15]==csp+4
            if i<8 or case.get('real_captured_descriptors')or i==len(vectors)-1:save(out/f'bus-{i}.json',dict(case=case['id'],original=original_bus,native=compiled_bus))
            rows.append(dict(case=case['id'],CCR=case['SR']&31,supervisor=bool(case['SR']&0x2000),native_instructions=steps,original_instructions=len(original['steps']),actual_data_bus_events=len(compiled_bus),C_stack_bytes=TOP-low,complete_CPU_nonprivate_RAM_data_bus_match=True))
            state.update(status='checking',completed=len(rows));mark()
            if len(rows)%64==0:print('native display',len(rows),'/',len(vectors),flush=True)
        save(out/'cases.json',rows);save(out/'vectors.json',vectors)
        paths=[V/'native-record-loop-image-disc-build-v1-current.json',Path(__file__),Path(fixtures.__file__),Path(h.__file__),V/'scene-display-list-algorithm-host-v2-current.json',V/'scene-display-list-mutations-v2-current.json',*SRC.rglob('*'),ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-display-list-algorithm-v2/coordinator-reference.inc',ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-display-list-structured-v1/primitives.inc',build/'native-shared.bin',out/'cases.json',out/'vectors.json',*out.glob('bus-*.json')]
        state.update(deployed_module_byte_identity=True,build=str(V/'native-record-loop-image-disc-build-v1-current.json'),status='terminal_native_display_list_body_preflight_pass'if args.limit else'terminal_native_display_list_full_CPU_RAM_data_bus_pass',payload=str(build/'native-shared.bin'),payload_sha256=sha(build/'native-shared.bin'),payload_bytes=len(payload),symbols=syms,maximum_C_stack_bytes=maximum,C_stack_reserved=208,body_only=True,task_slots=len({i%SLOTS for i in range(len(rows))}),source_instruction_locations=len(coverage),original_display_instructions_on_native_path=0,source_sha256={str(p):sha(p)for p in paths if p.is_file()},scope=__doc__+' Body-only native entry; complete logicalCPU/banks and all2MBRAM except the98byte supplied context and208byte privateCstack. All other arenas remain checked. Actual data-bus read address/order/count and write values compare outside native code/arenas and original instruction fetch; original source-table data reads are included. Core recorder lacks widths/readvalues: host dualCPU gate supplies those. No bridge/nesting/disc/gameplay/IRQ/console proof. Native loops have no synthetic work deadline. Declared reread-mutation cases use stable values in this target run unless a target operand fixture is separately implemented.')
        mark();print(state['status'],len(rows),maximum,len(payload),flush=True)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
    finally:
        if runtime:runtime.core.vjtrace_disarm();runtime.close()
if __name__=='__main__':main()
