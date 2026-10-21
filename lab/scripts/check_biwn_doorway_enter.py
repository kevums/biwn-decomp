"""Compare readable10430 against original opcodes, including aliases/rereads."""
import copy,ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_doorway_cpu as original
ROOT=original.ROOT;world=original.queue.world;SP=original.SP

class Memory:
    def __init__(self,raw,case,fail=None):
        self.raw=bytearray(raw);self.trace=[];self.errors=[];self.fail=fail
        self.queues={(row['address'],row['width']):list(row['values'])for row in case['read_queues']}
    def event(self,a,w,v=None):
        if self.fail==len(self.trace):raise ValueError('injected bus failure')
        if not 0<=a<=len(self.raw)-w:raise ValueError('out of RAM')
        if v is None:
            queue=self.queues.get((a,w))
            if queue:self.raw[a:a+w]=queue.pop(0).to_bytes(w,'big')
            v=int.from_bytes(self.raw[a:a+w],'big');self.trace.append(['r',a,w,v]);return v
        self.raw[a:a+w]=v.to_bytes(w,'big');self.trace.append(['w',a,w,v])

def translated(fn,raw,case,missing=None,null_bus=False,null_out=False,fail=None):
    memory=Memory(raw,case,fail)
    def reader(width):
        def callback(_,address,value):
            try:value[0]=memory.event(address,width);return 0
            except Exception as error:memory.errors.append(repr(error));return 1
        return callback
    def writer(width):
        def callback(_,address,value):
            try:memory.event(address,width,value);return 0
            except Exception as error:memory.errors.append(repr(error));return 1
        return callback
    types=[world.R8,world.R16,world.R32,world.W16,world.W32]
    callbacks=[types[0](reader(1)),types[1](reader(2)),types[2](reader(4)),types[3](writer(2)),types[4](writer(4))]
    if missing is not None:callbacks[missing]=types[missing]()
    bus=world.Bus(*callbacks,world.CALL(),None,0);value=c.c_uint32(0xa5a55a5a)
    obj=int.from_bytes(raw[SP+4:SP+8],'big')
    status=fn(None if null_bus else c.byref(bus),obj,case['index'],case['direction'],case['registers'][1],case['registers'][3],None if null_out else c.byref(value))
    return status,value.value,memory

def public(raw):
    return raw[:SP-0x1000]+raw[SP+16:]

def main():
    source=ROOT/'projects/black-ice-white-noise/restoration'
    author=json.loads((ROOT/'verification/local-doorway-enter-workflow-current.json').read_text())
    candidate=Path(author['directory'])/'candidate.c';out=ROOT/'verification/doorway-readable'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(source),str(candidate),'-o',str(out/'libdoorway-enter.dylib')]
    built=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(built.stdout+built.stderr)
    if built.returncode:
        (out/'status.json').write_text(json.dumps(dict(status='terminal_compile_failed',compiler_exit=built.returncode))+'\n');raise RuntimeError(str(out/'compiler.log'))
    fn=c.CDLL(str(out/'libdoorway-enter.dylib')).biwn_doorway_enter
    fn.argtypes=[c.POINTER(world.Bus),c.c_uint32,c.c_uint16,c.c_uint16,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];fn.restype=c.c_int
    inventory=original.queue.read(ROOT/'verification/biwn-disc-gate-target-inventory.json');vectors=original.cases(inventory)
    snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    # Real checked state, without relocating its geometry or its portal records.
    checked=ROOT/'runs/world-controls-20261017T084146.540377Z/reference/final-RAM.bin'
    raw=bytearray(checked.read_bytes());obj=0x49c4c;raw[obj+4:obj+8]=(12991).to_bytes(4,'big');raw[obj+10:obj+14]=(42400).to_bytes(4,'big')
    actual=copy.deepcopy(vectors[0]);actual.update(id=len(vectors),kind='actual_loaded_gate_with_supplied_boundary_position',index=0,direction=3,body=False,initial=[[SP,4,original.STOP],[SP+4,4,obj],[SP+8,2,0],[SP+10,2,3]],read_queues=[])
    actual['raw_override']=bytes(raw);vectors.append(actual)
    # These deliberately overlapping records exercise source-ordered reads.
    for delta in [-16,-8,0,4,8,12,16,24,32]:
        case=copy.deepcopy(vectors[0]);case.update(id=len(vectors),kind='record_object_alias',index=0,direction=4,body=False,read_queues=[])
        case['registers'][1]=0;case['registers'][3]=0;obj=0x80000;portal=obj+delta;tile=0x82000
        case['initial']=[[SP,4,original.STOP],[SP+4,4,obj],[SP+8,2,0],[SP+10,2,4],[obj+64,2,0],[0x49bb4,4,tile],[tile+2,2,1],[tile+12,4,portal]]
        case['initial'] += [[portal+offset,2,value]for offset,value in [(18,0xfffe),(20,0x7fff),(22,0x8001),(24,5),(26,312)]]
        vectors.append(case)
    # Address coverage alone missed a negative16-bit ASR result leaking into
    # D0's high half. Exercise failing keys after negative coordinate deltas.
    for direction in [0,1,2,3,4,0xffff]:
        for magnitude in [64,0x8000]:
            case=copy.deepcopy(vectors[0]);case.update(id=len(vectors),kind='negative_key_mismatch',index=0,direction=direction,body=False,read_queues=[])
            case['registers'][1]=(-magnitude)&0xffff;case['registers'][3]=1
            obj=0x80000;portal=0x100000
            case['initial']=[[SP,4,original.STOP],[SP+4,4,obj],[SP+8,2,0],[SP+10,2,direction],[obj+64,2,0],[0x49bb4,4,0x82000],[0x82002,2,1],[0x8200c,4,portal],[portal+26,2,312]]
            if direction<4:
                left,right=[(6,78),(74,6),(82,12),(12,86)][direction]
                case['initial'] += [[obj+left,2,0],[obj+right,2,magnitude],[portal+11+direction*2,1,1]]
            vectors.append(case)
    base=copy.deepcopy(vectors[0]);base.update(id=len(vectors),kind='target_reread',index=0,direction=4,body=False)
    base['registers'][1]=0;base['registers'][3]=0;base['initial']=[[SP,4,original.STOP],[SP+4,4,0x80000],[SP+8,2,0],[SP+10,2,4],[0x80040,2,0],[0x49bb4,4,0x82000],[0x82002,2,1],[0x8200c,4,0x100000],[0x10001a,2,312]]
    base['read_queues']=[dict(address=0x10001a,width=2,values=[312,41])];vectors.append(base)
    session=Path(original.queue.read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory'])
    mapping=original.queue.read(session/'doorway-fullCPU-generation.json');prior=original.queue.read(ROOT/'verification/biwn-doorway-cpu-checks.json')
    runtime=original.Runtime(Path(prior['directory'])/'libdoorway-cpu.dylib',mapping['instructions_decoded'])
    coverage=set();results=[];native_cases=0;guards=[];successful=None
    try:
        for case in vectors:
            seed=original.fixture(case.get('raw_override',snapshot),case)
            left,cpu,reference=runtime.unicorn(seed,case,coverage)
            status,value,memory=translated(fn,seed,case)
            trace=[row for row in reference['trace']if not SP-0x1000<=row[1]<SP+16]
            if status or memory.errors or value!=cpu.registers[0]or public(left)!=public(memory.raw)or trace!=memory.trace:
                failure=dict(status=status,D0=value,expected_D0=cpu.registers[0],case_id=case['id'],kind=case.get('kind'),expected_trace=trace,actual_trace=memory.trace,errors=memory.errors)
                (out/'mismatch.json').write_text(json.dumps(failure,indent=2)+'\n');raise AssertionError(str(out/'mismatch.json'))
            if not case['read_queues']and(case['id']%32==0 or case.get('kind')):
                native,native_cpu,_=runtime.native(seed,case,set());assert native_cpu.registers[0]==value and public(native)==public(memory.raw);native_cases+=1
            if value==1 and successful is None:successful=(seed,case,trace)
            results.append(dict(case_id=case['id'],kind=case.get('kind','disc_or_synthetic'),D0=value,trace_sha256=hashlib.sha256(json.dumps(trace).encode()).hexdigest(),public_RAM_sha256=hashlib.sha256(public(memory.raw)).hexdigest()))
            if len(results)%100==0:(out/'status.json').write_text(json.dumps(dict(status='running',pid=os.getpid(),completed=len(results),total=len(vectors)))+'\n')
        assert successful is not None
        seed,case,trace=successful
        for options in [dict(missing=i)for i in range(5)]+[dict(null_bus=True),dict(null_out=True)]:
            status,value,memory=translated(fn,seed,case,**options);assert status==1 and value==0xa5a55a5a and not memory.trace and bytes(memory.raw)==seed;guards.append(options)
        for index in range(len(trace)):
            status,value,memory=translated(fn,seed,case,fail=index);assert status==2 and value==0xa5a55a5a and memory.trace==trace[:index]
            expected=bytearray(seed)
            for kind,a,w,v in trace[:index]:
                if kind=='w':expected[a:a+w]=v.to_bytes(w,'big')
            assert memory.raw==expected;guards.append(dict(fail_bus_event=index))
        assert len(coverage)==75,len(coverage)
        report=dict(status='readable_doorway_original_CPU_D0_public_RAM_bus_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(results),native_cases=native_cases,original_instruction_coverage=[len(coverage),75],guards=len(guards),source_function='0x10430',candidate_source=str(candidate),candidate_sha256=hashlib.sha256(candidate.read_bytes()).hexdigest(),header_sha256=hashlib.sha256((source/'biwn_doorway_enter.h').read_bytes()).hexdigest(),verifier_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),local_author=author['directory'],local_author_seconds=author['seconds'],model_body_repairs=author.get("model_body_repairs",0),published=False,default_runtime_promoted=False,scope='Complete75instruction source10430behavior at this high-level API: fullD0, ordered public bus reads/writes and public2MBRAM outside private caller stack match original Unicorn. NativeM68000 independently crosschecks a subset. Includes actual disc gates, signed indexes/counts/directions, one real loaded gate with a supplied boundary position, nine record/object aliases and a target-reread fixture. Added host error guards preserve prior stores and output on failure. Original private stack, caller-saved registers, CCR/cycles, scene loading/cleanup/scheduler and natural frame-runtime substitution are excluded. Coordinator supplied source contract/API and verifier; local model wrote the body. No new weights or whole-game/standalone claim.')
        (out/'cases.json').write_text(json.dumps(results,indent=2)+'\n');(out/'guards.json').write_text(json.dumps(guards,indent=2)+'\n');(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(out/'status.json').write_text(json.dumps(dict(status='terminal_pass'))+'\n');(ROOT/'verification/doorway-readable-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report),flush=True)
    except Exception as error:
        (out/'status.json').write_text(json.dumps(dict(status='terminal_failed',error=repr(error)))+'\n');raise
    finally:runtime.native_oracle.close()

if __name__=='__main__':main()
