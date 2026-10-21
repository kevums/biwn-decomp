"""Complete original boundary routine versus the exact C instruction provider.

The right lane calls only the generated C step function and RAM callbacks.
The native CPU executes only the original left-hand oracle. This is a
controlled component check, not clocked gameplay or physical hardware.
"""
import ctypes as c
import json,os
from collections import Counter
from datetime import datetime,timezone
from pathlib import Path
import capstone
import check_biwn_native_geometry_outside as original
from check_local_GPU_wait_C import Bus,R8,R16,R32,W16,W32,CALL
from check_biwn_scheduler import CPU
from run_biwn_native_fast_gameplay_route import ROOT,sha,save


def read(p):
    return json.loads(Path(p).read_text())


def main():
    cp_build=ROOT/'verification/geometry-C-runtime-build-current.json'
    build=read(cp_build);assert build['status']=='terminal_geometry_C_compiled_pending_checks'
    cp=Path(build['CPU_candidate']);candidate=read(cp)
    native_build_path=ROOT/'verification/native-geometry-outside-disc-build-current.json'
    native_build=read(native_build_path)
    assert build['build_proof_sha256']==sha(native_build_path)
    for path,digest in build['source_sha256'].items():assert sha(path)==digest,path
    original.BASE=native_build['geometry_outside_start']
    length=native_build['appended_bytes']
    common=bytearray((ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes())
    payload=Path(native_build['component']).read_bytes();at=native_build['resident_address'];common[at:at+len(payload)]=payload
    program=bytearray(common)
    program[original.ENTRY:original.ENTRY+8]=b'\x4e\xf9'+native_build['geometry_outside_entry'].to_bytes(4,'big')+b'\x4e\x71'
    atlas=Path(candidate['instruction_RAM_source']).read_bytes()
    lib=c.CDLL(candidate['library']);step=getattr(lib,candidate['function'])
    step.argtypes=[c.POINTER(Bus),c.POINTER(CPU),c.c_void_p,c.c_void_p,c.c_void_p];step.restype=c.c_int
    decoder=capstone.Cs(capstone.CS_ARCH_M68K,capstone.CS_MODE_BIG_ENDIAN|capstone.CS_MODE_M68K_000)
    identities={}
    for key in candidate['selected_case_sources']:
        pc=int(key,16)
        if pc==original.ENTRY or original.BASE<=pc<original.BASE+length:
            ins=next(decoder.disasm(atlas[pc:pc+24],pc,count=1));identities[pc]=bytes(ins.bytes)
    out=ROOT/'verification/geometry-C-function'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes());print(out,flush=True)
    image=bytearray(program);events=[];errors=[]
    def internal(a,w):
        return original.SP-8192<=a and a+w<=original.SP or original.BASE<=a and a+w<=original.BASE+length
    def reader(width):
        def cb(_,a,p):
            if a>len(image)-width:errors.append(['r',a,width]);return 1
            p[0]=int.from_bytes(image[a:a+width],'big')
            if not internal(a,width):events.append(['r',a,width,int(p[0])])
            return 0
        return cb
    def writer(width):
        def cb(_,a,value):
            if a>len(image)-width:errors.append(['w',a,width]);return 1
            image[a:a+width]=int(value).to_bytes(width,'big')
            if not internal(a,width):events.append(['w',a,width,int(value)])
            return 0
        return cb
    W8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint8)
    callbacks=[R8(reader(1)),R16(reader(2)),R32(reader(4)),W16(writer(2)),W32(writer(4)),W8(writer(1))]
    bus=Bus(*callbacks[:5],CALL(),None,0)
    coverage=set();minimum=original.SP
    def translated(case,changes):
        nonlocal minimum
        image[:]=original.seed(program,case);events.clear();errors.clear()
        cpu=CPU();cpu.registers[:]=case['incoming']+[original.SP];cpu.pc=original.ENTRY;cpu.sr=case['sr']
        cpu.usp=0x1fe000 if case['sr']&0x2000 else original.SP
        cpu.ssp=original.SP if case['sr']&0x2000 else 0x1ff000
        visits=Counter();pending=list(changes);local_min=original.SP
        for count in range(10000):
            pc=cpu.pc
            if pc==original.STOP:break
            assert pc in identities,('Unknown C instruction',hex(pc))
            assert image[pc:pc+len(identities[pc])]==identities[pc],('Instruction bytes changed',hex(pc))
            visits[pc]+=1;coverage.add(pc);local_min=min(local_min,cpu.registers[15])
            if pending and [pc,visits[pc]]==pending[0][:2]:
                _,_,a,w,value=pending.pop(0);image[a:a+w]=value.to_bytes(w,'big')
            status=step(c.byref(bus),c.byref(cpu),c.cast(callbacks[5],c.c_void_p),None,None)
            assert status==0 and not errors,(hex(pc),status,errors)
        else:raise AssertionError('C function did not return within instruction limit')
        assert not pending and cpu.registers[15]==original.SP+4
        minimum=min(minimum,local_min)
        values=list(cpu.registers)+[cpu.pc,cpu.sr,cpu.usp,cpu.ssp]
        return bytes(image),values,list(events),count
    state=dict(status='running_complete_boundary_function_through_C_provider',pid=os.getpid(),directory=str(out),
               CPU_candidate=str(cp),right_lane_original_opcode_execution=False,new_training=False,whole_game_complete=False)
    def mark():
        save(out/'protocol.json',state);save(ROOT/'verification/geometry-C-function-active.json',state)
    mark();n=original.Native();stable=[];dynamic=[]
    def compare(case,index,kind):
        x=original.trace(common,case,length,True);y=original.trace(program,case,length,False)
        assert x[1]==y[1] and original.normalize(y[0],x[0],length)==x[0]
        left=original.native(n,common,case,length,True,x[2])
        right=translated(case,y[2])
        normalized=original.normalize(right[0],left[0],length)
        if left[1]!=right[1] or normalized!=left[0] or x[1]!=right[2]:
            save(out/'mismatch.json',dict(kind=kind,index=index,parameters=case,original_CPU=left[1],C_CPU=right[1],
                original_events=x[1],C_events=right[2],RAM_differences=[hex(i) for i,(a,b) in enumerate(zip(left[0],normalized)) if a!=b][:32]))
            raise AssertionError('Full original versus C-provider function mismatch')
        if kind=='stable':assert right[1][:18]==original.expected(case)
        return dict(case=index,CPU=right[1],public_ordered_events=len(right[2]),C_instruction_steps=right[3],compiled_read_updates=y[2])
    try:
        cases=original.vectors();save(out/'stable-fixtures.json',cases)
        for i,case in enumerate(cases):
            stable.append(compare(case,i,'stable'))
            if i%256==0:state['stable_completed']=len(stable);mark();print('C boundary',len(stable),'/',len(cases),flush=True)
        for mode in [0,0x2000]:
            for flags in range(32):
                for kind in range(4):
                    obj=0x80000;case=dict(object=obj,values=[0,0,0xffffff9c,100,0xffffff9c,100],incoming=[0x80000000]*15,sr=mode|flags)
                    case['read_queues']=[(obj+4,[0,101])] if kind==0 else [(obj+4,[0,0xffffff9b])] if kind==1 else [(obj+10,[0,101])] if kind==2 else [(obj+10,[0,0xffffff9b])]
                    dynamic.append(compare(case,len(dynamic),'changing'))
        save(out/'stable-results.json',stable);save(out/'changing-results.json',dynamic)
        state.update(status='terminal_complete_boundary_C_provider_CPU_RAM_ordered_pass',stable_cases=len(stable),changing_coordinate_cases=len(dynamic),
                     C_instruction_addresses_exercised=sorted(coverage),max_private_stack_bytes=original.SP-minimum,
                     source_sha256={str(p):sha(p) for p in [out/'runner-as-run.py',Path(original.__file__),cp_build,cp,Path(candidate['library']),
                         Path(candidate['instruction_RAM_source']),native_build_path,Path(native_build['component'])]},
                     scope='Complete original1028E versus final-linked212-byte boundary component executed solely bythe generated C instruction provider andRAM callbacks. FullD/A/PC/SR/USP/SSP/public2MBRAM/logical orderedaccesses;1376stable+256declared changing-coordinate cases atcorresponding PCvisit. Private8KBstack/code/entry excluded. No originalopcode execution onright. No live clocks/GPU/DSP/IRQ,arbitraryalias/fault/physicaltiming orwholegame proof;atomiccost andgameplay checks areseparate.')
        mark();save(ROOT/'verification/geometry-C-function-current.json',state);print(state['status'],len(stable),len(dynamic),len(coverage),flush=True)
    except BaseException as error:
        state.update(status='terminal_geometry_C_function_failed',error=repr(error));mark();raise
    finally:n.close()


if __name__=='__main__':main()
