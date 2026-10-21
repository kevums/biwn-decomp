"""Fixed material C versus saved original GPU: all architectural/memory effects."""
import ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
ROOT=frame.ROOT;read=lambda p:json.loads(p.read_text());save=frame.save;sha=lambda data:hashlib.sha256(data).hexdigest()
R8=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint8));R16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint16));R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32));W16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint16);W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32);TRACE=c.CFUNCTYPE(None,c.c_void_p,c.c_uint32)
class Bus(c.Structure):_fields_=[('read8',R8),('read16',R16),('read32',R32),('write16',W16),('write32',W32),('observe_PC',TRACE),('context',c.c_void_p)]
class State(c.Structure):_fields_=[('registers',(c.c_uint32*32)*2)]+[(key,c.c_uint32)for key in ['pc','z','c','n','instructions']]
def state_dict(s):return dict(registers=[list(s.registers[i])for i in range(2)],**{key:getattr(s,key)for key in ['pc','z','c','n']})
def main():
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);source=session/'gpu-material-C-candidates';proof=read(ROOT/'verification/biwn-gpu-material-original-probes.json');capture=Path(proof['directory']);native_rows=read(capture/'cases.json')
    out=ROOT/'verification/biwn-gpu-materials'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-material-probe.dylib');core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32]
    runs={};mappings={};coverage={h:set()for h in ['0x6460','0x6720','0x69a0']}
    for header in coverage:
        name='material'+header[2:];mapping=read(source/f'{name}-generation.json');mappings[header]=mapping
        for filename,digest in mapping['source_sha256'].items():assert sha((source/filename).read_bytes())==digest
        library=out/f'lib-{name}.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/f'biwn_gpu_{name}.c'),'-o',str(library)]
        compiler=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/f'{name}-compiler.txt').write_text(compiler.stdout+compiler.stderr);assert compiler.returncode==0,compiler.stderr
        lib=c.CDLL(str(library));run=getattr(lib,f'biwn_gpu_{name}_run');run.argtypes=[c.POINTER(Bus),c.POINTER(State),c.c_uint32];run.restype=c.c_int;runs[header]=run
    def translated(row,**options):
        stem=f'case-{row["case"]:02d}';device.seed((capture/f'{stem}-before-RAM.bin').read_bytes(),1);raw=(capture/f'{stem}-before-GPU-state.bin').read_bytes();buf=c.create_string_buffer(raw);assert core.GPUStateLoad(buf)==len(raw)
        state=State();gpu=row['before_GPU']
        for i in range(2):state.registers[i][:]=gpu['registers'][i]
        for key in ['pc','z','c','n']:setattr(state,key,gpu[key])
        events=[];pcs=[];errors=[]
        def reader(width):
            def call(_,address,value):
                if options.get('fail')==('read',width):return 1
                try:value[0]=device.read(address&0xffffff,width);events.append(['r',address&0xffffff,width,value[0]]);return 0
                except Exception as error:errors.append(repr(error));return 1
            return call
        def writer(width):
            def call(_,address,value):
                if options.get('fail')==('write',width):return 1
                try:
                    address&=0xffffff
                    if address<0x200000:device.direct(address,width,value)
                    elif width==4 and 0xf03000<=address<=0xf03ffc:core.GPUWriteLong(address,value,0)
                    else:raise AssertionError(('unsupported_write',hex(address),width))
                    events.append(['w',address,width,value]);return 0
                except Exception as error:errors.append(repr(error));return 1
            return call
        def trace(_,pc):pcs.append(pc)
        callbacks=[R8(reader(1)),R16(reader(2)),R32(reader(4)),W16(writer(2)),W32(writer(4)),TRACE(trace)]
        if 'missing'in options:callbacks[options['missing']]=type(callbacks[options['missing']])()
        if options.get('no_trace'):callbacks[5]=TRACE()
        if options.get('bad_pc'):state.pc=0
        if 'bad_flag'in options:setattr(state,options['bad_flag'],2)
        before=bytes(state);bus=Bus(*callbacks,None);status=runs[row['CPU_header']](None if options.get('null_bus')else c.byref(bus),None if options.get('null_state')else c.byref(state),options.get('budget',1000000));raw,hardware=gpu_state(core)
        return device.ram(),raw,state,dict(status=status,state_unchanged=before==bytes(state),events=events,PC_samples=pcs,errors=errors,hardware=hardware,device=device.stats())
    rows=[];guards=[]
    try:
        for row in native_rows:
            header=row['CPU_header'];decoded={r['address']:r for r in mappings[header]['instructions_decoded']};stem=f'case-{row["case"]:02d}';save(out/'status.json',dict(status='running',case=row['case']))
            expected_RAM=(capture/f'{stem}-after-RAM.bin').read_bytes();expected_GPU=(capture/f'{stem}-after-GPU-state.bin').read_bytes();assert sha(expected_RAM)==row['after_RAM_sha256']and sha(expected_GPU)==row['after_GPU_state_sha256']
            actual_RAM,actual_GPU,state,result=translated(row);actual=state_dict(state);expected={key:row['after_GPU'][key]for key in actual}
            native_events=[]
            for ev in row['events']:
                op=int(decoded[ev[2]-2]['bytes'][:4],16)>>10;width={39:1,40:2,41:4,46:2,47:4}[op];native_events.append(['r'if ev[0]==11 else'w',ev[3],width,ev[4]])
            visible=[event for event in result['events']if event[1]<0x200000];shape=[event[:3]for event in native_events]==[event[:3]for event in visible];stores=[event for event in native_events if event[0]=='w']==[event for event in visible if event[0]=='w']
            keys=['accumulator','remainder','hidata','matrix_control','matrix_pointer','division_control','data_organization','control','active_bank'];controls=all(result['hardware'][key]==row['after_GPU'][key]for key in keys)
            if result['status']or actual!=expected or actual_RAM!=expected_RAM or actual_GPU[:4096]!=expected_GPU[:4096]or result['PC_samples']!=row['steps']or not shape or not stores or not controls:
                save(out/'mismatch.json',dict(case=row['case'],header=header,actual=actual,expected=expected,result=result,bus_shape_match=shape,stores_match=stores,controls_match=controls,native_events=native_events,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(actual_RAM,expected_RAM))if a!=b][:40],GPU_RAM_differences=[hex(0xf03000+i)for i,(a,b)in enumerate(zip(actual_GPU[:4096],expected_GPU[:4096]))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            assert not result['device']['GPUExec1_calls']and not result['device']['game_frames_executed']and not result['device']['device_error']
            coverage[header].update(row['steps'])
            for pc in row['steps']:
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:coverage[header].add(pc+2)
            rows.append(dict(case=row['case'],CPU_header=header,state=actual,original_RAM_and_GPU_state_PC_bus_match=True,RAM_sha256=sha(actual_RAM),GPU_RAM_sha256=sha(actual_GPU[:4096]),device=result['device']))
        for header in coverage:
            row=next(row for row in native_rows if row['CPU_header']==header)
            for options in [{'missing':i}for i in range(5)]+[dict(null_bus=True),dict(null_state=True),dict(budget=0)]+[dict(bad_flag=key)for key in ['z','c','n']]:
                _,_,_,result=translated(row,**options);assert result['status']==1 and result['state_unchanged']and not result['events'];guards.append(dict(CPU_header=header,options=options))
            for options,status in [(dict(bad_pc=True),3),(dict(budget=1),4)]+[(dict(fail=pair),2)for pair in [('read',2),('read',4),('write',2),('write',4)]]+([(dict(fail=('read',1)),2)]if header!='0x6460'else[]):
                _,_,_,result=translated(row,**options);assert result['status']==status and result['state_unchanged'],(header,options,result);guards.append(dict(CPU_header=header,options=options))
            _,_,_,result=translated(row,no_trace=True);assert result['status']==0 and not result['PC_samples'];guards.append(dict(CPU_header=header,options=dict(optional_trace=True)))
        programs={h:dict(cases=sum(row['CPU_header']==h for row in rows),source_instruction_coverage=[len(coverage[h]),mappings[h]['source_instruction_count']],uncovered_instruction_addresses=[hex(r['address'])for r in mappings[h]['instructions_decoded']if r['address']not in coverage[h]],host_guards=sum(g['CPU_header']==h for g in guards),source_sha256=mappings[h]['source_sha256'])for h in coverage}
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='material_C_matches_original_in_retained_inputs_instruction_coverage_reported_per_program',directory=str(out),source_directory=str(source),original_probe_directory=str(capture),cases=len(rows),programs=programs,original_GPU_calls_on_C_side=0,local_model_case_bodies=False,coordinator_generated=True,new_components=0,full_renderer_C=False,full_viewport_proved=False,scope='Both64registers/flags/PC,whole2MBRAM,all4KBGPUlocalRAM,unchangedcontrol/accumulator/divider/matrix state,exactdirectPC order and externalbus readshape/actualstores match original. Native watch readvalues are placeholders. Pinned GPU is sole oracle; source handoff F03440 ends comparison. Uncovered instructions remain explicit; no full instruction acceptance yet.')
        save(out/'fixtures.json',rows);save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_bounded_pass'));save(ROOT/'verification/biwn-gpu-material-candidate-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
