"""Quarantined local dispatcher C versus72saved original GPU cases."""
import ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_inventory_frame as frame
from probe_biwn_gpu_projection import gpu_state
ROOT=frame.ROOT;read=lambda p:json.loads(p.read_text());save=frame.save;sha=lambda data:hashlib.sha256(data).hexdigest()
R32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.POINTER(c.c_uint32));W32=c.CFUNCTYPE(c.c_int,c.c_void_p,c.c_uint32,c.c_uint32);TRACE=c.CFUNCTYPE(None,c.c_void_p,c.c_uint32,c.c_uint32,c.c_uint32,c.c_uint32)
class Bus(c.Structure):_fields_=[('read32',R32),('write32',W32),('observe_PC',TRACE),('context',c.c_void_p)]
class State(c.Structure):_fields_=[('registers',(c.c_uint32*32)*2)]+[(key,c.c_uint32)for key in ['pc','z','c','n','instructions']]
def state_dict(s):return dict(registers=[list(s.registers[i])for i in range(2)],**{key:getattr(s,key)for key in ['pc','z','c','n']})
def main():
    author=Path(read(ROOT/'verification/GPU-dispatcher-local-author-current.json')['directory']);candidate=author/'candidate';package=read(candidate/'package.json');proof=read(ROOT/'verification/biwn-gpu-dispatcher-original-probes.json');capture=Path(proof['directory']);native_rows=read(capture/'cases.json');out=ROOT/'verification/biwn-gpu-dispatcher'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);library=out/'libgpu-dispatcher.dylib';command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(candidate/'biwn_gpu_dispatcher.c'),'-o',str(library)];compiler=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiler.stdout+compiler.stderr);assert compiler.returncode==0,compiler.stderr
    for name,digest in package['source_sha256'].items():assert sha((candidate/name).read_bytes())==digest
    device=frame.Device(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'render-assets',1,ROOT/'tools/libbiwn-dispatcher-probe.dylib');core=c.CDLL(str(ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib'));core.GPUStateSave.argtypes=[c.c_void_p];core.GPUStateSave.restype=c.c_size_t;core.GPUStateLoad.argtypes=[c.c_void_p];core.GPUStateLoad.restype=c.c_size_t;core.GPUWriteLong.argtypes=[c.c_uint32,c.c_uint32,c.c_uint32];lib=c.CDLL(str(library));run=lib.biwn_gpu_dispatcher_run;run.argtypes=[c.POINTER(Bus),c.POINTER(State),c.c_uint32,c.c_uint32];run.restype=c.c_int
    def translated(row,**options):
        stem=f'case-{row["case"]:02d}';device.seed((capture/f'{stem}-before-RAM.bin').read_bytes(),1);raw=(capture/f'{stem}-before-GPU-state.bin').read_bytes();buf=c.create_string_buffer(raw);assert core.GPUStateLoad(buf)==len(raw);state=State();gpu=row['before_GPU']
        for b in range(2):state.registers[b][:]=gpu['registers'][b]
        for key in ['pc','z','c','n']:setattr(state,key,gpu[key])
        events=[];pcs=[];flag_trace=[];errors=[];polls=[0];fixture=row['fixture']
        def reader(_,address,value):
            if options.get('fail')=='read':return 1
            try:
                if address==0xf03204 and fixture['inject_header']!=0xffffffff:
                    if polls[0]==fixture['wait_reads']:core.GPUWriteLong(0xf03204,fixture['inject_header'],0)
                    polls[0]+=1
                value[0]=device.read(address&0xffffff,4);events.append(['r',address&0xffffff,4,value[0]]);return 0
            except Exception as error:errors.append(repr(error));return 1
        def writer(_,address,value):
            if options.get('fail')=='write':return 1
            try:
                address&=0xffffff
                if address<0x200000:device.direct(address,4,value)
                elif 0xf03000<=address<=0xf03ffc:core.GPUWriteLong(address,value,0)
                else:raise AssertionError(('unsupported_write',hex(address)))
                events.append(['w',address,4,value]);return 0
            except Exception as error:errors.append(repr(error));return 1
        def trace(_,pc,z,carry,n):pcs.append(pc);flag_trace.append(z|(carry<<1)|(n<<2))
        callbacks=[R32(reader),W32(writer),TRACE(trace)]
        if 'missing'in options:callbacks[options['missing']]=type(callbacks[options['missing']])()
        if options.get('no_trace'):callbacks[2]=TRACE()
        if options.get('bad_pc'):state.pc=0
        if 'bad_flag'in options:setattr(state,options['bad_flag'],2)
        if options.get('idle_loop'):core.GPUWriteLong(0xf03204,0xffffffff,0)
        bus=Bus(*callbacks,None);before=bytes(state);status=run(None if options.get('null_bus')else c.byref(bus),None if options.get('null_state')else c.byref(state),options.get('budget',100000),options.get('yield_idle',fixture['yield_idle']));after_raw,hardware=gpu_state(core)
        return device.ram(),after_raw,state,dict(status=status,state_unchanged=before==bytes(state),events=events,PC_samples=pcs,flags_before_each_direct_PC=flag_trace,errors=errors,host_poll_count=polls[0],hardware=hardware,device=device.stats())
    rows=[];coverage=set();guards=[]
    try:
        session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);decoded={r['address']:r for r in read(session/'gpu-dispatcher-loop/source-decode.json')['rows']}
        for row in native_rows:
            stem=f'case-{row["case"]:02d}';save(out/'status.json',dict(status='running',case=row['case']));expected_RAM=(capture/f'{stem}-after-RAM.bin').read_bytes();expected_GPU=(capture/f'{stem}-after-GPU-state.bin').read_bytes();assert sha(expected_RAM)==row['after_RAM_sha256']and sha(expected_GPU)==row['after_GPU_state_sha256']
            actual_RAM,actual_GPU,state,result=translated(row);actual=state_dict(state);expected={key:row['after_GPU'][key]for key in actual};native=[['r'if ev[0]==11 else'w',ev[3],4,ev[4]]for ev in row['events']];visible=[ev for ev in result['events']if ev[1]<0x200000];shape=[ev[:3]for ev in native]==[ev[:3]for ev in visible];stores=[ev for ev in native if ev[0]=='w']==[ev for ev in visible if ev[0]=='w'];control_keys=['accumulator','remainder','hidata','matrix_control','matrix_pointer','division_control','data_organization','control','active_bank'];controls=all(result['hardware'][key]==row['after_GPU'][key]for key in control_keys)
            if result['status']or actual_RAM!=expected_RAM or actual_GPU[:4096]!=expected_GPU[:4096]or actual!=expected or result['PC_samples']!=row['steps'] or result['flags_before_each_direct_PC']!=row['flags_before_each_direct_PC']or not shape or not stores or not controls or result['host_poll_count']!=row['host_poll_count']:
                save(out/'mismatch.json',dict(case=row['case'],actual=actual,expected=expected,result=result,native_events=native,bus_shape_match=shape,stores_match=stores,controls_match=controls,GPU_RAM_differences=[hex(0xf03000+i)for i,(a,b)in enumerate(zip(actual_GPU[:4096],expected_GPU[:4096]))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            assert not result['device']['GPUExec1_calls']and not result['device']['game_frames_executed']and not result['device']['device_error'];coverage.update(row['steps'])
            for pc in row['steps']:
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:coverage.add(pc+2)
            rows.append(dict(case=row['case'],fixture=row['fixture'],state=actual,direct_PC_samples=len(row['steps']),original_GPU_calls_during_C=0,full_architecture_RAM_GPU_RAM_PC_bus_match=True,flags_before_every_direct_PC_match=True,GPU_RAM_sha256=sha(actual_GPU[:4096])))
        row=native_rows[0]
        for options in [{'missing':i}for i in [0,1]]+[dict(null_bus=True),dict(null_state=True),dict(budget=0),dict(yield_idle=2)]+[dict(bad_flag=key)for key in ['z','c','n']]:
            _,_,_,result=translated(row,**options);assert result['status']==1 and result['state_unchanged']and not result['events'];guards.append(options)
        for options,status in [(dict(bad_pc=True),3),(dict(budget=1),4),(dict(fail='read'),2),(dict(fail='write'),2),(dict(idle_loop=True,yield_idle=0,budget=100),4)]:
            _,_,_,result=translated(row,**options);assert result['status']==status and result['state_unchanged'],(options,result);guards.append(options)
        _,_,_,result=translated(row,no_trace=True);assert result['status']==0 and not result['PC_samples'];guards.append(dict(optional_trace=True));assert coverage==set(decoded)
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='local_dispatcher_C_all31_matches_original72_cases',directory=str(out),candidate_directory=str(candidate),package=package,GPU_cases=len(rows),source_instruction_coverage=[31,31],flags_before_every_direct_PC_match=True,host_guards=len(guards),source_sha256=package['source_sha256'],original_probe_directory=str(capture),original_GPU_calls_during_C=0,local_model_case_bodies=True,coordinator_edited_case_bodies=False,new_components=0,full_main_GPU_program_reconstructed=False,full_renderer_C=False,scope='Full64registers/flags/PC,all4KBGPUlocalRAM,whole2MBmainRAM,unchanged GPU controls/matrix/divider/accumulator and exactdirectPC/externalreadshape/stores match original. Source loop only; eight real headers with declared copy/cache/seed variants, host idle-yield boundary and scripted command injection. InternalGPUbus extra idle checks are host policy, not claimed as native watched reads. Native watch readvalues placeholders. No async/hardware/full636byteGPUboot/fullgame claim.',compiler=command)
        save(out/'fixtures.json',rows);save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/biwn-gpu-dispatcher-candidate-checks.json',report);print(json.dumps({k:v for k,v in report.items()if k not in ['package','compiler','scope']}))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:device.close()
if __name__=='__main__':main()
