"""Quarantined candidate57A0 versus original GPU, pinned blitter on bothpaths."""
import argparse,ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
from probe_biwn_gpu_draw import blitter_registers
ROOT=frame.ROOT;save=frame.save;read=lambda p:json.loads(p.read_text());sha=lambda x:hashlib.sha256(x).hexdigest()
R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32));W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32);TRACE=c.CFUNCTYPE(None,c.c_void_p,c.c_uint32)
class Bus(c.Structure):_fields_=[('read32',R32),('write32',W32),('observe_PC',TRACE),('context',c.c_void_p)]
class State(c.Structure):_fields_=[('registers',(c.c_uint32*32)*2)]+[(name,c.c_uint32)for name in ['pc','z','c','n','instructions']]
def state_dict(state):return dict(registers=[list(state.registers[i])for i in range(2)],**{name:getattr(state,name)for name in ['pc','z','c','n']})
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--directory',type=Path,required=True);options=parser.parse_args();candidate=options.directory.resolve();package=read(candidate/'package.json')
    out=ROOT/'verification/biwn-gpu-setup57'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);library=out/'libgpu-setup57.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(candidate/'biwn_gpu_setup57.c'),'-o',str(library)]
    compiler=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiler.stdout+compiler.stderr)
    if compiler.returncode:save(out/'status.json',dict(status='terminal_failed',error='strict compilation failed'));raise AssertionError(compiler.stderr)
    for name,digest in package['source_sha256'].items():assert sha((candidate/name).read_bytes())==digest
    original=read(ROOT/'verification/biwn-gpu-setup57-original-probes.json');capture=Path(original['directory']);native_rows=read(capture/'cases.json')
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-setup57-probe.dylib');core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'))
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t
    core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];core.BlitterReadLong.argtypes=[c.c_uint32,c.c_uint32];core.BlitterReadLong.restype=c.c_uint32
    lib=c.CDLL(str(library));run=lib.biwn_gpu_setup57_run;run.argtypes=[c.POINTER(Bus),c.POINTER(State),c.c_uint32];run.restype=c.c_int
    def translated(row,**options):
        stem=f'case-{row["case"]:02d}';memory=(capture/f'{stem}-before-RAM.bin').read_bytes();raw=(capture/f'{stem}-before-GPU-state.bin').read_bytes();device.seed(memory,1);buf=c.create_string_buffer(raw);assert core.GPUStateLoad(buf)==len(raw)
        assert blitter_registers(core)==(capture/f'{stem}-before-blitter-registers.bin').read_bytes()
        state=State()
        for bank in range(2):state.registers[bank][:]=row['before_GPU']['registers'][bank]
        for name in ['pc','z','c','n']:setattr(state,name,row['before_GPU'][name])
        events=[];pcs=[];errors=[];current_PC=[state.pc]
        def reader(_,address,value):
            if options.get('fail')=='read':return 1
            try:
                if options.get('busy_PC')==current_PC[0] and address==0xf02238:value[0]=0
                else:value[0]=device.read(address&0xffffff,4)
                events.append(['r',address&0xffffff,4,value[0]]);return 0
            except Exception as error:errors.append(repr(error));return 1
        def writer(_,address,value):
            if options.get('fail')=='write':return 1
            try:
                address&=0xffffff
                if address<=0x1ffffc:device.direct(address,4,value)
                elif 0xf02200<=address<=0xf0229c:device.write(address,value)
                elif 0xf03000<=address<=0xf03ffc or address==0xf02104:core.GPUWriteLong(address,value,0)
                else:raise AssertionError(('unsupported_write',hex(address)))
                events.append(['w',address,4,value]);return 0
            except Exception as error:errors.append(repr(error));return 1
        def trace(_,pc):pcs.append(pc);current_PC[0]=pc
        callbacks=[R32(reader),W32(writer),TRACE(trace)]
        if 'missing'in options:callbacks[options['missing']]=type(callbacks[options['missing']])()
        if options.get('bad_pc'):state.pc=0
        if 'bad_flag'in options:setattr(state,options['bad_flag'],2)
        before=bytes(state);bus=Bus(*callbacks,None);status=run(None if options.get('null_bus')else c.byref(bus),None if options.get('null_state')else c.byref(state),options.get('budget',100000))
        after_raw,hardware=gpu_state(core)
        return device.ram(),after_raw,state,dict(status=status,state_unchanged=before==bytes(state),events=events,PC_samples=pcs,errors=errors,hardware=hardware,blitter_registers=blitter_registers(core).hex(),device=device.stats())
    rows=[];coverage=set()
    try:
        for row in native_rows:
            save(out/'status.json',dict(status='running',case=row['case']));stem=f'case-{row["case"]:02d}';expected_RAM=(capture/f'{stem}-after-RAM.bin').read_bytes();expected_GPU=(capture/f'{stem}-after-GPU-state.bin').read_bytes();expected_blitter=(capture/f'{stem}-after-blitter-registers.bin').read_bytes()
            assert sha(expected_RAM)==row['after_RAM_sha256']and sha(expected_GPU)==row['after_GPU_state_sha256']and sha(expected_blitter)==row['after_blitter_registers_sha256']
            actual_RAM,actual_GPU,state,result=translated(row);actual=state_dict(state);expected={key:row['after_GPU'][key]for key in actual}
            native_events=[['r'if e[0]==11 else'w',e[3],2 if 0xf02200<=e[3]<=0xf0229e else 4,e[4]]for e in row['events']]
            rebuilt=[]
            for kind,address,width,value in result['events']:
                if 0xf02200<=address<=0xf0229c:rebuilt.extend([[kind,address,2,value>>16],[kind,address+2,2,value&65535]])
                elif address<0x200000:rebuilt.append([kind,address,width,value])
            shape=[e[:3]for e in native_events]==[e[:3]for e in rebuilt];writes=[e for e in native_events if e[0]=='w']==[e for e in rebuilt if e[0]=='w']
            control_names=['accumulator','remainder','hidata','matrix_control','matrix_pointer','division_control','data_organization','control','active_bank'];controls=all(result['hardware'][k]==row['after_GPU'][k]for k in control_names)
            if result['status']or actual!=expected or actual_RAM!=expected_RAM or actual_GPU[:4096]!=expected_GPU[:4096]or bytes.fromhex(result['blitter_registers'])!=expected_blitter or result['PC_samples']!=row['steps']or not shape or not writes or not controls:
                save(out/'mismatch.json',dict(case=row['case'],actual_state=actual,expected_state=expected,result=result,native_events=native_events,C_visible_events=rebuilt,bus_shape_match=shape,stores_match=writes,controls_match=controls,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(actual_RAM,expected_RAM))if a!=b][:40],GPU_RAM_differences=[hex(0xf03000+i)for i,(a,b)in enumerate(zip(actual_GPU[:4096],expected_GPU[:4096]))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            assert not result['device']['GPUExec1_calls']and not result['device']['game_frames_executed']and not result['device']['device_error']
            coverage.update(result['PC_samples']);coverage.add(0xf03320)
            rows.append(dict(case=row['case'],source_native_directory=str(capture),state=actual,instructions_including_delays=state.instructions,native_PC_samples=len(row['steps']),RAM_sha256=sha(actual_RAM),GPU_RAM_sha256=sha(actual_GPU[:4096]),blitter_read_registers_sha256=sha(expected_blitter),external_read_shape_and_actual_stores_match=True,device=result['device']))
        guards=[];row=native_rows[0]
        for options in [{'missing':i}for i in [0,1]]+[dict(null_bus=True),dict(null_state=True),dict(budget=0)]+[dict(bad_flag=name)for name in ['z','c','n']]:
            _,_,_,result=translated(row,**options);assert result['status']==1 and result['state_unchanged']and not result['events'];guards.append(options)
        for options,status in [(dict(bad_pc=True),3),(dict(budget=1),4),(dict(fail='read'),2),(dict(fail='write'),2),(dict(busy_PC=0xf03274,budget=200),4),(dict(busy_PC=0xf03298,budget=200),4)]:
            _,_,_,result=translated(row,**options);assert result['status']==status and result['state_unchanged'],(options,result);guards.append(options)
        assert len(coverage)==73,len(coverage)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='GPU57A0_candidate_C_all73_full_registers_RAM_controls_blitter_readbacks_PC_bus_match_original',directory=str(out),GPU_cases=len(rows),source_instruction_coverage=[73,73],host_guards=len(guards),candidate_directory=str(candidate),package=package,original_probe_directory=str(capture),original_GPU_calls_on_C_side=0,local_model_case_bodies=True,coordinator_engine_primitives_tests=True,live_draw_chain_linked=False,full_viewport_proved=False,matched=['Both64registers,Z/C/N,PC,4KBGPUlocalRAM,whole2MBRAM,unchangedaccumulator/remainder/HIDATA/matrixpointer/division/dataorganization/control/activebank,matrixcontrolwrite,blitterread-registerwindow,exactdirectPCorder and externalbusreadshape/actualstores. Source2776bytecopyand6380queueverified.', 'Blitterportlongsappearastwo16bitnativebusrecords; Ctraceexpandedaccordingly. InternalGPUmatrix/localmailboxeffectscomparedthroughsnapshots,notclaimedaswatchedbusreads. Nativewatchreadvaluesareplaceholders.'],limits=['Standalonefourrealprojectionoutputinputs plus60declaredGPUregister/controlseeds,withfreshpinnedblitteronbothpaths. SameoriginalGPUoracle/sharedblitterbackend; noindependenthardware/timing/interruptproof. Blitterreadbackwindowhasaliasesandisnotfulldecodedstate.', 'SourceCPU E202,residentdispatcher/58A0/6380/6460Cdraw andliveGPUcontextintegrationstillpending. No originalGPUinstructionsorwholegameframesexecuteCside. BusyguardsareCbusfixtures,notnativeasyncwaitvalidation.'],compiler=command)
        save(out/'fixtures.json',rows);save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-gpu-setup57-candidate-checks.json',report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
