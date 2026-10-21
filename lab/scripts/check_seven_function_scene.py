"""Original caller+animation+slot clear against the linked local C bodies."""
import ctypes as c,hashlib,itertools,json,os,random,re,subprocess
from datetime import datetime,timezone
from pathlib import Path
from unicorn import Uc,UC_ARCH_M68K,UC_MODE_BIG_ENDIAN,UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.m68k_const import *
import check_local_global_animation_tick as animation
import check_local_slot_clear as slot
import check_local_scene_slots_expand as expand
import check_debug_overlay_real_dependencies as debug
DEBUG_FN=None
DRAW_FN=None
SLOT_FN=None
PREPARE_FN=None
FACE_FN=None
EXPAND_FN=None
ROOT=animation.ROOT;SP=animation.SP;STOP=animation.STOP
HELPERS=[0xe26c]
debug.SP=SP-16;debug.SCRATCH=SP-70
class Script(debug.Script):
    def __init__(self,snapshot,case):super().__init__(snapshot,case);self.debug_active=False;self.raw_E26C_fifth=[];self.expansion_entry_D2=[]
    def call(self,target,args,incoming):
        self.trace.append(['call',target,args,incoming]);self.changed=[]
        if self.fail_call==target:raise RuntimeError('Injected helper failure')
        for address,width,value in self.case['helper_effects'].get(str(target),[]):self.put(address,width,value)
        return incoming if target==0xe26c else self.case['helper_returns'][str(target)]
def original(script,case,coverage):
    cpu=Uc(UC_ARCH_M68K,UC_MODE_BIG_ENDIAN);cpu.ctl_set_cpu_model(UC_CPU_M68K_M68000);cpu.mem_map(0,0x200000);cpu.mem_map(0xf02000,0x1000);cpu.mem_write(0,bytes(script.memory));cpu.mem_write(SP,STOP.to_bytes(4,'big'))
    for reg,value in zip(animation.boundary.REGS,case['incoming']):cpu.reg_write(reg,value)
    cpu.reg_write(UC_M68K_REG_SR,0x2000);cpu.reg_write(UC_M68K_REG_A7,SP)
    for target in HELPERS:cpu.mem_write(target,b'\x4e\x75')
    steps=[]
    def code(engine,address,width,_):
        if address==0x1142e:script.expansion_entry_D2.append(engine.reg_read(UC_M68K_REG_D2))
        if address in HELPERS:
            if address==0xe26c:script.raw_E26C_fifth.append(int.from_bytes(engine.mem_read(engine.reg_read(UC_M68K_REG_A7)+20,4),'big'))
            stack=engine.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(engine.mem_read(stack+offset,width),'big')for offset,width in [(4,4),(8,4),(12,4),(16,4),(20,2)]]if address==0xe26c else[]
            result=script.call(address,args,engine.reg_read(UC_M68K_REG_D0))
            for a,w,v in script.changed:engine.mem_write(a,v.to_bytes(w,'big'))
            engine.reg_write(UC_M68K_REG_D0,result);return
        if address==0x10734:script.debug_active=True
        if address in debug.WIDTHS:
            sp=engine.reg_read(UC_M68K_REG_A7);offset=4;values=[]
            for size in debug.WIDTHS[address]:values.append(int.from_bytes(engine.mem_read(sp+offset,size),'big'));offset+=size
            if address==0x1b45a:script.formatter(values,engine.reg_read(UC_M68K_REG_D0))
            else:script.note_text(values,engine.reg_read(UC_M68K_REG_D0))
        if address in [0x10ba4,0x10968,0x11384,0x110d4,0x1142e,0x10734]:
            args=[int.from_bytes(engine.mem_read(engine.reg_read(UC_M68K_REG_A7)+off,2),'big')for off in [4,6]]if address==0x10968 else[]
            if address==0x110d4:
                sp=engine.reg_read(UC_M68K_REG_A7);args=[int.from_bytes(engine.mem_read(sp+offset,width),'big')for offset,width in [(4,4),(8,4),(12,2)]]
            script.trace.append(['call',address,args,engine.reg_read(UC_M68K_REG_D0)])
        assert 0x11ad4<=address<=0x11b4a or 0x10ba4<=address<=0x10c16 or 0x10968<=address<=0x1098e or 0x110d4<=address<=0x11760 or 0x10734<=address<=0x10966 or 0x14776<=address<0x14caa or 0xe540<=address<0xe588 or 0x1b160<=address<=0x1b476 or 0xe61c<=address<=0xe68a,hex(address)
        coverage.add(address);steps.append(address)
    def read(engine,t,a,w,v,_):
        if(SP-0x1000<=a<SP+4 and not(script.debug_active and debug.SCRATCH<=a<debug.SCRATCH+54))or 0x14800<=a<0x14842 or 0x11104<=a<0x11110 or 0x114c0<=a<0x114cc:return
        engine.mem_write(a,script.read(a,w).to_bytes(w,'big'))
    def write(engine,t,a,w,v,_):
        if SP-0x1000<=a<SP+4 and not(script.debug_active and debug.SCRATCH<=a<debug.SCRATCH+54):return
        script.write(a,w,v&((1<<(8*w))-1))
    cpu.hook_add(UC_HOOK_CODE,code);cpu.hook_add(UC_HOOK_MEM_READ,read);cpu.hook_add(UC_HOOK_MEM_WRITE,write);cpu.emu_start(0x11ad4,STOP,count=200000,timeout=5000000)
    assert cpu.reg_read(UC_M68K_REG_PC)==STOP and cpu.reg_read(UC_M68K_REG_A7)==SP+4
    memory=bytearray(cpu.mem_read(0,0x200000))
    for target in HELPERS:memory[target:target+2]=script.memory[target:target+2]
    assert memory[:SP-0x1000]==script.memory[:SP-0x1000]and memory[SP+4:]==script.memory[SP+4:]
    written={address for event in script.trace if event[0]=='w'and debug.SCRATCH<=event[1]<debug.SCRATCH+54 for address in range(event[1],event[1]+event[2])};assert all(memory[a]==script.memory[a]for a in written)
    return cpu.reg_read(UC_M68K_REG_D0),steps
def translated(fn,tick,script,case,missing=None):
    w=animation.boundary.world;errors=[];tick_calls=[]
    def read(width):
        def f(_,a,out):
            try:out[0]=script.read(a,width);return 0
            except Exception as error:errors.append(repr(error));return 1
        return f
    def write(width):
        def f(_,a,value):
            try:script.write(a,width,value);return 0
            except Exception as error:errors.append(repr(error));return 1
        return f
    def call(_,target,args,count,out):
        try:
            if target==0x10968:
                assert count==2;script.trace.append(['call',target,list(args[:count]),out[0]])
                def byte_write(_,address,value):
                    try:script.write(address,1,value);return 0
                    except Exception as error:errors.append(repr(error));return 1
                callback=slot.W8(byte_write);slot_bus=slot.Bus(callback,None);result=c.c_uint32(out[0]);status=SLOT_FN(c.byref(slot_bus),args[0],args[1],c.byref(result))
                if not status:out[0]=result.value
                return status
            if target in [0x11384,0x110d4]:
                assert count==(0 if target==0x11384 else 3);script.trace.append(['call',target,list(args[:count]),out[0]]);value=c.c_uint32(out[0])
                status=PREPARE_FN(c.byref(bus),out[0],c.byref(value))if target==0x11384 else FACE_FN(c.byref(bus),args[0],args[1],args[2],c.byref(value))
                if not status:out[0]=value.value
                return status
            if target==0x1142e:
                assert count==0;script.trace.append(['call',target,[],out[0]]);value=c.c_uint32(out[0]);seed=expand.Seed(out[0],*[case['incoming'][i]for i in [4,5,6]]);status=EXPAND_FN(c.byref(bus),c.byref(seed),c.byref(value))
                if not status:out[0]=value.value
                return status
            if target==0x10734:
                assert count==0;script.debug_active=True;script.trace.append(['call',target,[],out[0]]);incoming=list(case['incoming']);incoming[0]=out[0];nested=dict(case,incoming=incoming)
                status,value,nested_errors=debug.translated(DEBUG_FN,DRAW_FN,script,nested);errors.extend(nested_errors)
                if not status:out[0]=value
                return status
            if target==0x10ba4:
                assert count==0;script.trace.append(['call',target,[],out[0]]);value=c.c_uint32(out[0]);status=tick(c.byref(bus),out[0],c.byref(value));tick_calls.append(status)
                if not status:out[0]=value.value
                return status
            assert target in HELPERS and count==(5 if target==0xe26c else 0)
            out[0]=script.call(target,list(args[:count]),out[0]);return 0
        except Exception as error:errors.append(repr(error));return 1
    callbacks=[w.R8(),w.R16(read(2)),w.R32(read(4)),w.W16(write(2)),w.W32(write(4)),w.CALL(call)]
    if missing is not None:callbacks[missing]=type(callbacks[missing])()
    bus=w.Bus(*callbacks,None,8);value=c.c_uint32(0xa55aa55a);status=fn(c.byref(bus),case['incoming'][0],c.byref(value));return status,value.value,errors,tick_calls
def main():
    global SLOT_FN,PREPARE_FN,FACE_FN,EXPAND_FN,DEBUG_FN,DRAW_FN
    prior=json.loads((ROOT/'verification/local-six-function-scene-integration-current.json').read_text());overlay=json.loads((ROOT/'verification/local-debug-overlay-component-current.json').read_text());restoration=ROOT/'projects/black-ice-white-noise/restoration';out=ROOT/'runs'/('seven-function-scene-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ'));out.mkdir();print(out,flush=True)
    source_fields=['source','tick_source','slot_source','prepare_source','face_source','expand_source'];sources=[];hashes={}
    for key in source_fields:
        source=Path(prior[key]);digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==prior[key+'_sha256'];sources.append(source);hashes[str(source)]=digest
    for name,proof in [('biwn_debug_overlay.c',overlay),('biwn_text.c',json.loads((ROOT/'verification/biwn-text-checks.json').read_text())),('biwn_formatter_cpu.c',json.loads((ROOT/'verification/biwn-formatter-cpu-checks.json').read_text()))]:
        source=restoration/name;digest=hashlib.sha256(source.read_bytes()).hexdigest();assert digest==(proof['source_sha256'][name]if isinstance(proof['source_sha256'],dict)else proof['source_sha256']);sources.append(source);hashes[str(source)]=digest
    library=out/'libseven-scene.dylib';build=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror','-I',str(restoration),*[str(p)for p in sources],'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(build.stdout+build.stderr);assert not build.returncode,build.stderr
    lib=c.CDLL(str(library));fn=lib.biwn_global_scene_prepare;tick=lib.biwn_global_animation_tick;PREPARE_FN=lib.biwn_scene_slot_prepare
    for f in [fn,tick,PREPARE_FN]:f.argtypes=[c.POINTER(animation.boundary.world.Bus),c.c_uint32,c.POINTER(c.c_uint32)];f.restype=c.c_int
    SLOT_FN=lib.biwn_slot_clear;SLOT_FN.argtypes=[c.POINTER(slot.Bus),c.c_uint16,c.c_uint16,c.POINTER(c.c_uint32)];SLOT_FN.restype=c.c_int
    FACE_FN=lib.biwn_face_coordinates;FACE_FN.argtypes=[c.POINTER(animation.boundary.world.Bus),c.c_uint32,c.c_uint32,c.c_uint16,c.POINTER(c.c_uint32)];FACE_FN.restype=c.c_int
    EXPAND_FN=lib.biwn_scene_slots_expand;EXPAND_FN.argtypes=[c.POINTER(animation.boundary.world.Bus),c.POINTER(expand.Seed),c.POINTER(c.c_uint32)];EXPAND_FN.restype=c.c_int
    DEBUG_FN=lib.biwn_debug_overlay;DEBUG_FN.argtypes=[c.POINTER(animation.boundary.world.Bus),c.c_uint32,c.c_uint32,c.POINTER(c.c_uint32)];DEBUG_FN.restype=c.c_int
    DRAW_FN=lib.biwn_text_draw;DRAW_FN.argtypes=[c.POINTER(debug.text.Bus),c.POINTER(debug.text.Args),c.POINTER(c.c_uint32)];DRAW_FN.restype=c.c_int
    debug.FORMAT_FN=lib.biwn_formatter_cpu_call;debug.FORMAT_FN.argtypes=[c.POINTER(animation.boundary.world.Bus),c.POINTER(debug.fullcpu.CPU),debug.input_cpu.W8,debug.fullcpu.SERVICE,c.c_void_p,c.c_uint32,c.c_int];debug.FORMAT_FN.restype=c.c_int;debug.FORMAT_BODY=lib.biwn_formatter_cpu_body;debug.FORMAT_BODY.argtypes=debug.FORMAT_FN.argtypes;debug.FORMAT_BODY.restype=c.c_int
    snapshot=(ROOT/'verification/zero-warm-startup-instruction-atlas.bin').read_bytes();cases=[]
    for i,row in enumerate(json.loads((Path(prior['directory'])/'fixtures.json').read_text())):
        case=row['parameters'];case['initial']+=[[0x403cc,2,i%2],[0x403ca,2,[0,1,2,31][(i//2)%4]]];case.update(blitter_status=[1],draw_counts=[0],read_queues=[])
        if i%4==1:case['initial']+=[[0x4c3e0+n,1,value]for n,value in enumerate(bytes([3,96,8,9,32,126,0x54,0]))]
        cases.append(case)
    coverage=set();rows=[];grid=set();enabled=0;raw_fifths=[];entry_D2=[]
    for i,case in enumerate(cases):
        a=Script(snapshot,case);b=Script(snapshot,case);value,steps=original(a,case,coverage);status,actual,errors,ticks=translated(fn,tick,b,case)
        match=a.memory[:SP-0x1000]==b.memory[:SP-0x1000]and a.memory[SP+4:]==b.memory[SP+4:]
        if status or errors or value!=actual or a.trace!=b.trace or not match or a.mmio!=b.mmio or ticks!=[0]:
            (out/'mismatch.json').write_text(json.dumps(dict(case=i,parameters=case,status=status,expected=value,actual=actual,original_trace=a.trace,C_trace=b.trace,errors=errors,tick_status=ticks),indent=2)+'\n');raise AssertionError(out/'mismatch.json')
        assert b.format_calls==b.text_calls==(8 if i%2 else 0);enabled+=bool(i%2);grid.update(e[1]for e in b.trace if e[0]=='r'and 0x3d7a2<=e[1]<0x3d822)
        raw_fifths.extend(a.raw_E26C_fifth);entry_D2.extend(a.expansion_entry_D2)
        rows.append(dict(raw_E26C_fifth_longs=a.raw_E26C_fifth,entry_1142E_D2=a.expansion_entry_D2,case=i,full_D0=value,formatter_calls=b.format_calls,text_calls=b.text_calls,trace_sha256=hashlib.sha256(json.dumps(b.trace).encode()).hexdigest(),trace_events=len(b.trace)))
        if i%64==0:(out/'progress.json').write_text(json.dumps(dict(completed=i+1,total=len(cases)))+'\n')
    # Exact address sets come from preserved supplied disassemblies.
    base_author=json.loads((ROOT/'verification/local-global-scene-author-current.json').read_text());evidence_dirs=[Path(base_author['directory'])]+[Path(json.loads((ROOT/'verification'/name).read_text())['directory'])for name in ['local-global-animation-checks-current.json','local-slot-clear-checks-current.json','local-scene-slot-prepare-checks-current.json','local-face-coordinates-checks-current.json','local-scene-slots-expand-checks-current.json','local-debug-overlay-checks-current.json']]
    expected={int(pc,16)for directory in evidence_dirs for pc in re.findall(r'^([0-9a-fA-F]{8}):',json.loads((directory/'evidence.json').read_text())['assembly'],re.M)};assert len(expected)==629 and expected<=coverage and len(grid)==64
    guards=[]
    for target in [0xe26c,0x1b45a,0x149ae]:
        case=cases[3];script=Script(snapshot,case);script.fail_call=target;status,value,errors,ticks=translated(fn,tick,script,case);assert status==3 and value==0xa55aa55a;guards.append(dict(target=hex(target),status=status,output_unchanged=True))
    assert raw_fifths and set(raw_fifths)=={0}and set(entry_D2)<={0,2,4,6}
    (out/'case-results.json').write_text(json.dumps(rows,indent=2)+'\n');(out/'instruction-addresses.json').write_text(json.dumps(dict(primary=sorted(expected),dependencies=sorted(coverage-expected)),indent=2)+'\n')
    report=dict(status='seven_function_scene_real_formatter_text_original_match',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),debug_enabled_cases=enabled,primary_instruction_address_coverage=[len(expected),len(expected)],observed_formatter_text_dependency_addresses=len(coverage-expected),grid_cells=len(grid),source_sha256=hashes,remaining_scripted_helpers=['E26C GPU submission: raw fifthlong0 in this caller context'],raw_E26C_fifth_long_observations=len(raw_fifths),raw_E26C_fifth_long_values=sorted(set(raw_fifths)),entry_1142E_D2_values=sorted(set(entry_D2)),formatter_scripted=False,text_scripted=False,helper_guards=guards,coordinator_corrected_primary_function='1142E',local_primary_functions_accepted=6,coordinator_corrected_primary_functions=1,new_training=False,native_Chat_verified=False,natural_gameplay_integration_verified=False,full_route_runtime_promoted=False,scope='Seven complete scene routines11AD4,10BA4,10968,11384,110D4,1142E,10734 plus existing actual C formatter/text.576 synthetic wholechain comparisons against original instructions inUnicornM68000;629/629 primaryaddresses/64gridcells,288enabled overlays. FullD0,logicaldata/helperorder,formatter-written bytes within54byte scratch and externalRAM/MMIO match. Untouched private scratch tail is excluded. E26C GPU internals and overread beyond pushedzero word remain fixtures. Text/blitter devicewrite model,frozen/synthetic fonts,bounded string indices0/1/2/31 remain. PrivateCPUstack/CCR/otherregisters,nativebusdummyreads,physicalpixels/timing,naturalgameplay/fullroute excluded. This proof adds no pinned-nativeCPU comparison beyond earlier six-function subset.')
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/seven-function-scene-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],len(rows),len(expected),len(coverage-expected),enabled,flush=True)
if __name__=='__main__':main()
