"""Compare fixed C52E0 to retained native live-prefix GPU observations."""
import argparse,ctypes as c,hashlib,json,os,subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_gpu_geometry as common
ROOT=common.ROOT;Bus=common.Bus;read=common.read;save=common.save
class State(c.Structure):
    _fields_=[('registers',(c.c_uint32*32)*2)]+[(name,c.c_uint32)for name in ['pc','z','c','n','matrix_control','matrix_pointer','division_control','remainder','instructions','accumulator']]+[('local_RAM',c.c_uint8*4096)]
def state_from(gpu,raw):
    state=State()
    for bank in range(2):state.registers[bank][:]=gpu['registers'][bank]
    for name in ['pc','z','c','n','matrix_control','matrix_pointer','division_control','remainder','accumulator']:setattr(state,name,gpu[name])
    state.local_RAM[:]=raw[:4096];return state
def state_dict(state):return dict(registers=[list(state.registers[b])for b in range(2)],**{name:getattr(state,name)for name in ['pc','z','c','n','matrix_control','matrix_pointer','division_control','remainder','accumulator']})
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--variants',action='store_true');parser.add_argument('--integer-divider',action='store_true');options=parser.parse_args()
    out=ROOT/('verification/biwn-gpu-integer-projection'if options.integer_divider else'verification/biwn-gpu-projection')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    source=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libgpu-projection.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source/'biwn_gpu_projection.c'),'-o',str(library)]
    compiler=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.txt').write_text(compiler.stdout+compiler.stderr);assert compiler.returncode==0,compiler.stderr
    proof=read(ROOT/'verification'/('biwn-gpu-projection-integer-original-probes.json'if options.integer_divider else'biwn-gpu-projection-original-probes.json'));capture=Path(proof['directory']);session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'gpu-render-52e0-overlay/C-generation.json');decoded={r['address']:r for r in mapping['instructions_decoded']}
    lib=c.CDLL(str(library));run=lib.biwn_gpu_projection_run;run.argtypes=[c.POINTER(Bus),c.POINTER(State),c.c_uint32];run.restype=c.c_int
    prepare=lib.biwn_gpu_projection_prepare;prepare.argtypes=[c.POINTER(State),c.c_uint32];prepare.restype=c.c_int
    def translated(row,**opts):
        stem=f'case-{row["case"]:02d}';memory=bytearray((capture/f'{stem}-before-RAM.bin').read_bytes());raw=(capture/f'{stem}-before-GPU-state.bin').read_bytes();state=state_from(row['before_GPU'],raw);events=[];pcs=[];errors=[]
        def reader(width):
            def cb(_,a,value):
                physical=a&0xffffff
                if opts.get('fail')==('read',width):return 1
                if not 0<=physical<=len(memory)-width:errors.append(['read',hex(a),width]);return 1
                value[0]=int.from_bytes(memory[physical:physical+width],'big');events.append(['r',physical,width,value[0]]);return 0
            return cb
        def writer(width):
            def cb(_,a,value):
                physical=a&0xffffff
                if opts.get('fail')==('write',width):return 1
                if not 0<=physical<=len(memory)-width:errors.append(['write',hex(a),width]);return 1
                memory[physical:physical+width]=value.to_bytes(width,'big');events.append(['w',physical,width,value]);return 0
            return cb
        callbacks=[common.R16(reader(2)),common.R32(reader(4)),common.W16(writer(2)),common.W32(writer(4)),common.TRACE(lambda _,pc:pcs.append(pc))]
        if 'missing'in opts:callbacks[opts['missing']]=type(callbacks[opts['missing']])()
        if opts.get('bad_pc'):state.pc=0
        if opts.get('bad_flag'):state.z=2
        before=bytes(state);bus=Bus(*callbacks,None);status=run(None if opts.get('null_bus')else c.byref(bus),None if opts.get('null_state')else c.byref(state),opts.get('budget',1000000))
        return bytes(memory),state,dict(status=status,state_unchanged=before==bytes(state),events=events,PC_samples=pcs,errors=errors)
    datasets=[(capture,read(capture/'cases.json'))]
    if options.variants:
        variant=read(ROOT/'verification'/('biwn-gpu-projection-integer-variant-original-probes.json'if options.integer_divider else'biwn-gpu-projection-variant-original-probes.json'));variant_capture=Path(variant['directory']);datasets.append((variant_capture,read(variant_capture/'cases.json')))
    rows=[];coverage=set()
    try:
        for capture,row in [(folder,row)for folder,items in datasets for row in items]:
            save(out/'status.json',dict(status='running',case=row['case']));stem=f'case-{row["case"]:02d}'
            before=(capture/f'{stem}-before-RAM.bin').read_bytes();after=(capture/f'{stem}-after-RAM.bin').read_bytes();raw=(capture/f'{stem}-after-GPU-state.bin').read_bytes()
            assert hashlib.sha256(before).hexdigest()==row['before_RAM_sha256'] and hashlib.sha256(after).hexdigest()==row['after_RAM_sha256'] and hashlib.sha256(raw).hexdigest()==row['after_GPU_state_sha256']
            # Check prepare against the actual original overlay/argument setup.
            prefix_raw=(capture/f'{stem}-prefix-GPU-state.bin').read_bytes();initial=state_from(row['prefix_GPU'],prefix_raw);assert prepare(c.byref(initial),row['record_count'])==0
            initial_dict=state_dict(initial);expected_before={k:row['before_GPU'][k]for k in initial_dict};assert initial_dict==expected_before and bytes(initial.local_RAM)==(capture/f'{stem}-before-GPU-state.bin').read_bytes()[:4096]
            right,actual,rebuilt=translated(row);actual_dict=state_dict(actual);expected={k:row['after_GPU'][k]for k in actual_dict};native_events=[]
            for event in row['events']:
                pc=event[2]-2;op=int(decoded[pc]['bytes'][:4],16)>>10;width={40:2,41:4,46:2,47:4,54:2}[op];native_events.append(['r'if event[0]==11 else'w',event[3],width,event[4]])
            shape=[e[:3]for e in native_events]==[e[:3]for e in rebuilt['events']];writes=[e for e in native_events if e[0]=='w']==[e for e in rebuilt['events']if e[0]=='w']
            if rebuilt['status']or right!=after or bytes(actual.local_RAM)!=raw[:4096]or actual_dict!=expected or rebuilt['PC_samples']!=row['steps']or not shape or not writes:
                save(out/'mismatch.json',dict(case=row['case'],expected=expected,actual=actual_dict,rebuilt=rebuilt,native_events=native_events,bus_shape_match=shape,stores_match=writes,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(after,right))if a!=b][:50],GPU_RAM_differences=[hex(0xf03000+i)for i,(a,b)in enumerate(zip(raw[:4096],actual.local_RAM))if a!=b][:50]));raise AssertionError(str(out/'mismatch.json'))
            coverage.update(row['steps'])
            for pc in row['steps']:
                if int(decoded[pc]['bytes'][:4],16)>>10 in [52,53]:coverage.add(pc+2)
            rows.append(dict(case=row['case'],record_count=row['record_count'],camera_rotation=row.get('camera_rotation'),camera_translation=row.get('camera_translation'),source_native_case=str(capture/f'{stem}-before-RAM.bin'),state=actual_dict,C_instructions_including_delays=actual.instructions,direct_PC_samples=len(row['steps']),external_reads=sum(e[0]=='r'for e in rebuilt['events']),external_writes=sum(e[0]=='w'for e in rebuilt['events']),full_banks_flags_accumulator_divider_matrix_GPU_RAM_main_RAM_PC_bus_match=True))
        capture=datasets[0][0];guards=[];row=datasets[0][1][0]
        for opts in [{'missing':i}for i in range(4)]+[{'null_bus':True},{'null_state':True},{'budget':0},{'bad_flag':True}]:
            _,_,result=translated(row,**opts);assert result['status']==1 and result['state_unchanged']and not result['events'];guards.append(opts)
        for opts,status in [({'bad_pc':True},3),({'budget':1},4)]+[({'fail':('read',w)},2)for w in [2,4]]+[({'fail':('write',w)},2)for w in [2,4]]:
            _,_,result=translated(row,**opts);assert result['status']==status and result['state_unchanged'];guards.append(opts)
        initial=State();assert prepare(None,4)==1 and prepare(c.byref(initial),0)==1;guards.extend([dict(prepare_null=True),dict(prepare_zero_count=True)])
        missing=[hex(pc)for pc in sorted(set(decoded)-coverage)]
        if options.variants:assert not missing,missing
        report=dict(recorded_at=datetime.now(timezone.utc).isoformat(),status='GPU52E0_fixed_C_full_instruction_coverage_matches_original_live_prefix_and_declared_camera_variants'if not missing else'GPU52E0_fixed_C_matches_retained_original_live_prefix_observations_partial_instruction_coverage',directory=str(out),GPU_cases=len(rows),actual_live_prefix_cases=len(datasets[0][1]),declared_camera_variant_cases=sum(len(items)for _,items in datasets[1:]),source_instruction_coverage=[len(coverage),len(decoded)],uncovered_instruction_addresses=missing,host_guards=len(guards),source_sha256=mapping['source_sha256'],generator_sha256=mapping['generator_sha256'],shared_generator_sha256=mapping['shared_generator_sha256'],payload_sha256=mapping['payload_sha256'],native_probe_directory=str(capture),native_probe_directories=[str(folder)for folder,_ in datasets],original_GPU_core_calls_on_C_side=0,live_CPU_E19E_linked=False,full_renderer_verified=False,new_published_components=0,matched=['Both64register banks,Z/C/N,32-bit accumulator,matrix control/pointer,divider remainder/mode,all4KB GPU RAM,whole2MBmain RAM,directPC order,externalread shape and actualstores. Prepared state matches source arguments without resetting priorGPUstate.'],limits=['16captured liveprefix cases plus32declared camera variants when enabled; variantCPU prefix is not rerun. OriginalGPU52E0 observer is the sole GPU oracle. No second GPU emulator/physical hardware or timing proof. Externalwatch read values are placeholders.', 'Full CPU E19E separately reconstructed and checked, but not linked into the live C renderer. C57A0 setup separately accepted; remaining resident dispatcher and58A0/6380/6460/6720/69A0 still original in hybrid draw tests. Existing assisted startup/scripts and synchronous devices remain; full C viewport/game incomplete.'],compiler=command)
        report.update(GPU_division_control=0 if options.integer_divider else'from_retained_fractional_input',source_C_shader_changed=False)
        save(out/'fixtures.json',rows);save(out/'guards.json',guards);save(out/'report.json',report);save(out/'status.json',dict(status='terminal_bounded_pass'));save(ROOT/'verification'/('biwn-gpu-integer-projection-checks.json'if options.integer_divider else'biwn-gpu-projection-checks.json'),report);print(json.dumps(report))
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
if __name__=='__main__':main()
