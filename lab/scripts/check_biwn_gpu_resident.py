"""Resident C comparison with identical original preparation on both paths.

Original GPU executes preparation before the component boundary; zero GPUExec
calls are permitted during the C resident itself. Blitter remains pinned/core.
"""
import argparse,ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from check_biwn_gpu_projection import State,state_from,state_dict
from probe_biwn_gpu_projection import gpu_state
from probe_biwn_gpu_draw import blitter_registers
import resident_fixture_inputs
ROOT=frame.ROOT;read=lambda p:json.loads(p.read_text());save=frame.save;sha=lambda data:hashlib.sha256(data).hexdigest()
R16=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint16));R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32));W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32);BLIT=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32,c.POINTER(c.c_uint8));TRACE=c.CFUNCTYPE(None,c.c_void_p,c.c_uint32)
class Bus(c.Structure):_fields_=[('read16',R16),('read32',R32),('write32',W32),('blitter_write32',BLIT),('observe_PC',TRACE),('context',c.c_void_p)]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--limit',type=int);opt=ap.parse_args();session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);source=session/'gpu-resident-C-candidate';mapping=read(source/'C-generation.json');decoded={r['address']:r for r in mapping['instructions_decoded']};proof=read(ROOT/'verification/biwn-gpu-resident-original-probes.json');capture=Path(proof['directory']);base=Path(proof['source_projection_directory']);native_rows=read(capture/'cases.json')[:opt.limit or None]
    out=ROOT/'verification/biwn-gpu-resident'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);library=out/'libgpu-resident.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_gpu_resident.c'),'-o',str(library)];compiler=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiler.stdout+compiler.stderr);assert compiler.returncode==0,compiler.stderr
    for name,digest in mapping['source_sha256'].items():assert sha((source/name).read_bytes())==digest
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-resident-probe.dylib');core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));lib=device.lib
    core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.GPUGetRAM.restype=c.POINTER(c.c_uint8);core.BlitterReadLong.argtypes=[c.c_uint32,c.c_uint32];core.BlitterReadLong.restype=c.c_uint32
    lib.lab_movement_setup.restype=c.c_int;assert lib.lab_movement_setup()==0;lib.lab_resident_prepare.argtypes=[c.c_uint32];lib.lab_resident_prepare.restype=c.c_int
    program=c.CDLL(str(library));run=program.biwn_gpu_resident_run;run.argtypes=[c.POINTER(Bus),c.POINTER(State),c.c_uint32];run.restype=c.c_int
    def translated(row,**options):
        projection_stem=f'case-{row["original_projection_case"]:02d}';device.seed((base/f'{projection_stem}-before-RAM.bin').read_bytes(),1);raw=(base/f'{projection_stem}-before-GPU-state.bin').read_bytes();buf=c.create_string_buffer(raw);assert core.GPUStateLoad(buf)==len(raw);assert lib.lab_resident_prepare(row['occurrence'])==0
        if row.get('declared_variant'):resident_fixture_inputs.apply(device,core,row['declared_inputs'])
        stem=f'case-{row["case"]:02d}';raw,before_gpu=gpu_state(core);before=device.ram();before_blitter=blitter_registers(core)
        assert before==(capture/f'{stem}-before-RAM.bin').read_bytes()and raw[:4396]==(capture/f'{stem}-before-GPU-state.bin').read_bytes()[:4396]and before_blitter==(capture/f'{stem}-before-blitter-registers.bin').read_bytes()
        state=state_from(before_gpu,raw);events=[];pcs=[];errors=[];blits=[0];start_stats=device.stats()
        def reader(width):
            def call(_,address,value):
                if options.get('fail')==('read',width):return 1
                try:value[0]=device.read(address&0xffffff,width);events.append(['r',address&0xffffff,width,value[0]]);return 0
                except Exception as error:errors.append(repr(error));return 1
            return call
        def writer(_,address,value):
            if options.get('fail')==('write',4):return 1
            try:
                address&=0xffffff
                if address<0x200000:device.direct(address,4,value)
                elif 0xf02200<=address<=0xf0229c:device.write(address,value)
                else:raise AssertionError(('unsupported_external_write',hex(address)))
                events.append(['w',address,4,value]);return 0
            except Exception as error:errors.append(repr(error));return 1
        def blitter(_,address,value,local_RAM):
            if options.get('fail')==('blitter',4):return 1
            c.memmove(core.GPUGetRAM(),local_RAM,4096)
            status=writer(None,address,value)
            c.memmove(local_RAM,core.GPUGetRAM(),4096);blits[0]+=1;return status
        def trace(_,pc):pcs.append(pc)
        callbacks=[R16(reader(2)),R32(reader(4)),W32(writer),BLIT(blitter),TRACE(trace)]
        if 'missing'in options:callbacks[options['missing']]=type(callbacks[options['missing']])()
        if options.get('no_trace'):callbacks[4]=TRACE()
        if options.get('bad_pc'):state.pc=0
        if 'bad_flag'in options:setattr(state,options['bad_flag'],2)
        before_state=bytes(state);bus=Bus(*callbacks,None);status=run(None if options.get('null_bus')else c.byref(bus),None if options.get('null_state')else c.byref(state),options.get('budget',1000000));end_stats=device.stats();hardware=gpu_state(core)[1]
        return device.ram(),state,dict(status=status,state_unchanged=before_state==bytes(state),events=events,PC_samples=pcs,errors=errors,blitter_calls=blits[0],blitter_readbacks=blitter_registers(core).hex(),preparation_GPU_calls=start_stats['GPUExec1_calls'],GPU_calls_during_C=end_stats['GPUExec1_calls']-start_stats['GPUExec1_calls'],hardware=hardware,device=end_stats)
    rows=[];coverage=set();guards=[]
    try:
        for row in native_rows:
            stem=f'case-{row["case"]:02d}';save(out/'status.json',dict(status='running',case=row['case']));expected_RAM=(capture/f'{stem}-after-RAM.bin').read_bytes();expected_GPU=(capture/f'{stem}-after-GPU-state.bin').read_bytes();expected_blitter=(capture/f'{stem}-after-blitter-registers.bin').read_bytes();assert sha(expected_RAM)==row['after_RAM_sha256']and sha(expected_GPU)==row['after_GPU_state_sha256']
            actual_RAM,state,result=translated(row);actual=state_dict(state);expected={key:row['after_GPU'][key]for key in actual};native=[]
            for ev in row['events']:
                pc=ev[2]-2;op=int(decoded[pc]['bytes'][:4],16)>>10;width=2 if 0xf02200<=ev[3]<=0xf0229e else {40:2,41:4,47:4,54:2}[op];native.append(['r'if ev[0]==11 else'w',ev[3],width,ev[4]])
            visible=[]
            for kind,address,width,value in result['events']:
                if 0xf02200<=address<=0xf0229c:visible.extend([[kind,address,2,value>>16],[kind,address+2,2,value&65535]])
                else:visible.append([kind,address,width,value])
            shape=[ev[:3]for ev in native]==[ev[:3]for ev in visible];stores=[ev for ev in native if ev[0]=='w']==[ev for ev in visible if ev[0]=='w'];controls=all(result['hardware'][key]==row['after_GPU'][key]for key in ['hidata','data_organization','control','active_bank'])
            if result['status']or actual_RAM!=expected_RAM or bytes(state.local_RAM)!=expected_GPU[:4096]or actual!=expected or result['PC_samples']!=row['steps']or bytes.fromhex(result['blitter_readbacks'])!=expected_blitter or not shape or not stores or not controls:
                save(out/'mismatch.json',dict(case=row['case'],actual=actual,expected=expected,result=result,bus_shape_match=shape,stores_match=stores,controls_match=controls,native_events=native,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(actual_RAM,expected_RAM))if a!=b][:40],GPU_RAM_differences=[hex(0xf03000+i)for i,(a,b)in enumerate(zip(state.local_RAM,expected_GPU[:4096]))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            assert result['preparation_GPU_calls']>0 and result['GPU_calls_during_C']==0 and not result['device']['game_frames_executed']and not result['device']['device_error']
            coverage.update(row['steps'])
            for pc in row['steps']:
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:coverage.add(pc+2)
            rows.append(dict(case=row['case'],entry_PC=hex(row['before_GPU']['pc']),original_projection_case=row['original_projection_case'],occurrence=row['occurrence'],state=actual,instructions=state.instructions,direct_PC_samples=len(row['steps']),blitter_calls=result['blitter_calls'],preparation_GPU_calls=result['preparation_GPU_calls'],GPU_calls_during_C=0,whole_RAM_GPU_state_PC_bus_and_blitter_readbacks_match=True,RAM_sha256=sha(actual_RAM),GPU_RAM_sha256=sha(bytes(state.local_RAM))));save(out/'fixtures.json',rows);print(json.dumps(dict(case=row['case'],blitter_calls=result['blitter_calls'],passed=True)),flush=True)
        row=native_rows[0]
        for options in [{'missing':i}for i in range(4)]+[dict(null_bus=True),dict(null_state=True),dict(budget=0)]+[dict(bad_flag=key)for key in ['z','c','n']]:
            _,_,result=translated(row,**options);assert result['status']==1 and result['state_unchanged']and not result['events'];guards.append(options)
        for options,status in [(dict(bad_pc=True),3),(dict(budget=1),4)]+[(dict(fail=pair),2)for pair in [('read',2),('read',4),('write',4),('blitter',4)]]:
            _,_,result=translated(row,**options);assert result['status']==status and result['state_unchanged'],(options,result);guards.append(options)
        _,_,result=translated(row,no_trace=True);assert result['status']==0 and not result['PC_samples'];guards.append(dict(optional_trace=True))
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='resident_C_matches_retained_original_draw_inputs_instruction_coverage_explicit',directory=str(out),source_directory=str(source),source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],original_probe_directory=str(capture),cases=len(rows),source_instruction_coverage=[len(coverage),len(decoded)],uncovered_instruction_addresses=[hex(pc)for pc in sorted(set(decoded)-coverage)],host_guards=len(guards),original_GPU_calls_during_C_resident=0,original_preparation_GPU_execution=True,blitter_calls=sum(r['blitter_calls']for r in rows),local_model_case_bodies=False,coordinator_generated=True,new_components=0,full_renderer_C=False,scope='Original GPU reruns identical preparation before each C component boundary, preserving natural intra-replay blitter state. No GPU execution during C resident. Full64registers/flags/PC/accumulator/matrix/divider/remainder,4KBGPU RAM,2MBmainRAM,exactPCorder,externalreadshape/stores and blitter readbacks match in retained inputs. Synchronous pinned blitter shared; no hardware/timing/interrupt/scanout/fullgame claim. Instruction coverage is explicit, not completeness from generation.',compiler=command)
        save(out/'report.json',report);save(out/'guards.json',guards);save(out/'status.json',dict(status='terminal_preflight'if opt.limit else'terminal_bounded_pass'))
        if not opt.limit:save(ROOT/'verification/biwn-gpu-resident-candidate-checks.json',report)
        print(json.dumps({k:v for k,v in report.items()if k not in ['uncovered_instruction_addresses','compiler']}))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
