"""Fresh complete10430 native doorway route; original-entry control restores only10430."""
import argparse,json,os,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

WATCH=r'''
static int32_t (*next_owner)(uint32_t);
void set_next_owner(void *fn){next_owner=(int32_t(*)(uint32_t))fn;}
struct acquire_call {uint32_t task;unsigned pending;struct cpu incoming;uint32_t min_sp;};
static struct acquire_call acquire_slots[256];
static uint64_t acquire_entries,acquire_native_entries,acquire_returns,acquire_old_steps;
static uint64_t acquire_monitor_errors,acquire_native_steps,acquire_loader_calls;
static uint64_t acquire_user_stack_observations,acquire_user_stack_outside;
static unsigned acquire_pending,acquire_slot_count;
static uint32_t acquire_user_min_headroom=0xffffffffu,acquire_max_private_depth;
static struct acquire_call *acquire_slot(uint32_t task){
    for(unsigned i=0;i<acquire_slot_count;i++)if(acquire_slots[i].task==task)return &acquire_slots[i];
    if(acquire_slot_count<256){struct acquire_call *slot=&acquire_slots[acquire_slot_count++];slot->task=task;return slot;}
    acquire_monitor_errors++;return NULL;
}
static void watch_acquire(uint32_t pc){
    if(!acquire_pending&&pc!=0x1ac68&&!(pc>=ACQUIRE_START&&pc<ACQUIRE_END)&&!(pc>0x1ac68&&pc<0x1ae56))return;
    uint32_t task=rd32(0xc0920);struct acquire_call *slot=NULL;struct cpu current;
    if(pc==0x1ac68){
        slot=acquire_slot(task);if(!slot)return;
        if(slot->pending)acquire_monitor_errors++;
        read_cpu(&slot->incoming);slot->pending=1;slot->min_sp=slot->incoming.r[15];acquire_entries++;acquire_pending++;emit(pc);
    }
    if(pc>0x1ac68&&pc<0x1ae56)acquire_old_steps++;
    if(pc==ACQUIRE_ENTRY)acquire_native_entries++;
    if(pc>=ACQUIRE_START&&pc<ACQUIRE_END)acquire_native_steps++;
    for(unsigned i=0;i<acquire_slot_count;i++)if(acquire_slots[i].pending&&acquire_slots[i].task==task){slot=&acquire_slots[i];break;}
    if(!slot||!slot->pending)return;
    read_cpu(&current);
    if(!(current.sr&0x2000u)){
        uint32_t sp=current.r[15];acquire_user_stack_observations++;
        if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)acquire_user_stack_outside++;
        else if(sp-task-38u<acquire_user_min_headroom)acquire_user_min_headroom=sp-task-38u;
        if(sp<slot->min_sp)slot->min_sp=sp;
    }
    if(pc==0x1b044){
        uint32_t sp=current.r[15],s=slot->incoming.r[15];acquire_loader_calls++;emit(pc);
        if(sp!=s-68u||rd32(sp+12)!=s-8u||rd32(sp+20)!=0u||rd32(sp+16)!=current.r[5]||rd32(sp+8)!=current.r[12]||rd32(sp+4)!=current.r[9]+current.r[10])acquire_monitor_errors++;
    }
    if(pc==ACQUIRE_RETURN||pc==0x1ae54){
        uint32_t s=slot->incoming.r[15];acquire_returns++;emit(pc);
        const unsigned saved[]={2,3,4,5,6,7,10,11,12};
        for(unsigned i=0;i<9;i++)if(current.r[saved[i]]!=slot->incoming.r[saved[i]]||rd32(s-44u+4u*i)!=slot->incoming.r[saved[i]])acquire_monitor_errors++;
        if(current.r[14]!=slot->incoming.r[14]||current.r[15]!=s||rd32(s-4u)!=slot->incoming.r[14])acquire_monitor_errors++;
        uint32_t low=current.r[0]&0xffffu;uint16_t nz=(uint16_t)(low==0?4:(low&0x8000u)?8:0);
        if((current.sr&15u)!=nz||(current.sr&0xffe0u)!=(slot->incoming.sr&0xffe0u))acquire_monitor_errors++;
        if(s-slot->min_sp>acquire_max_private_depth)acquire_max_private_depth=s-slot->min_sp;
        slot->pending=0;acquire_pending--;
    }
}
'''
REPORT=r'''
    fprintf(file,",\"acquire_entries\":%llu,\"acquire_native_entries\":%llu,\"acquire_returns\":%llu,\"acquire_old_steps\":%llu,\"acquire_monitor_errors\":%llu,\"acquire_native_steps\":%llu,\"acquire_pending\":%u,\"acquire_loader_calls\":%llu",
        (unsigned long long)acquire_entries,(unsigned long long)acquire_native_entries,(unsigned long long)acquire_returns,(unsigned long long)acquire_old_steps,(unsigned long long)acquire_monitor_errors,(unsigned long long)acquire_native_steps,acquire_pending,(unsigned long long)acquire_loader_calls);
    fprintf(file,",\"acquire_user_stack_observations\":%llu,\"acquire_user_stack_outside\":%llu,\"acquire_user_min_headroom\":%u,\"acquire_max_private_depth\":%u",
        (unsigned long long)acquire_user_stack_observations,(unsigned long long)acquire_user_stack_outside,acquire_user_min_headroom,acquire_max_private_depth);
'''


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--same-layout-control',action='store_true');args=parser.parse_args()
    bp=ROOT/'verification/native-doorway-disc-build-current.json';build=json.loads(bp.read_text());assert build['status']=='terminal_native_doorway_disc_built_entry_verified_pending_gameplay';assert sha(build['derived_disc'])==build['derived_disc_sha256']
    tagged_path=ROOT/'verification/native-doorway-current.json';tagged=json.loads(tagged_path.read_text())
    assert tagged['status']=='terminal_native_doorway_v2_CPU_RAM_ordered_pass' and tagged['native_cases']==2025 and tagged['changing_coordinate_cases']==768
    assert tagged['source_sha256']==sha(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/doorway-kernel.c')
    for path,digest in tagged['dependencies_sha256'].items():assert sha(path)==digest,path
    monitor_path=ROOT/'verification/native-doorway-monitor-current.json';monitor=json.loads(monitor_path.read_text());assert monitor['status']=='terminal_doorway_live_oracle_stable_fixtures_pass' and monitor['original_cases']==monitor['compiled_cases']==2025
    for path,digest in monitor['source_sha256'].items():assert sha(path)==digest,path
    parent_path=ROOT/'verification/external-DSP-combined-route-current.json';parent=json.loads(parent_path.read_text());assert parent['status']=='terminal_initial_entry_external_DSP_combined_merchant_equal';cursor=build;found=False
    for _ in range(64):
        if cursor.get('derived_disc')==parent['command'][parent['command'].index('--disc')+1]:found=True;break
        if not cursor.get('parent_build'):break
        cursor=json.loads(Path(cursor['parent_build']).read_text())
    assert found
    template=Path(parent['directory'])/'probe.py';assert sha(template)==parent['source_sha256'][str(template)]
    out=ROOT/'verification/native-doorway-route'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True);(out/'runner-as-run.py').write_bytes(Path(__file__).read_bytes())
    disc=Path(build['derived_disc']);control_delta=None
    if args.same_layout_control:
        from extract_biwn_stage import swap16
        session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);offset=json.loads((session/'nextstage-mapping.json').read_text())['payload_raw_cdi_offset'];patches=json.loads(Path(build['patch_manifest']).read_text())['delta_patches'];rows=[p for p in patches if int(p['address'],16) in [0x10430]];assert len(rows)==1
        disc=out/'BIWN-boundary-layout-only-original-doorway-entry.cdi';shutil.copyfile(build['derived_disc'],disc);intervals=[]
        with disc.open('r+b') as stream:
            for row in rows:
                at=offset+int(row['address'],16)-0x4000;before=bytes.fromhex(row['replacement']);after=bytes.fromhex(row['original']);assert len(before)==len(after)==8;stream.seek(at);assert stream.read(8)==swap16(before);stream.seek(at);stream.write(swap16(after));intervals.append((at,at+8))
            stream.flush();os.fsync(stream.fileno())
        position=changes=0
        with Path(build['derived_disc']).open('rb') as left,disc.open('rb') as right:
            while True:
                a=left.read(1048576);b=right.read(1048576);assert len(a)==len(b)
                if not a:break
                if a!=b:
                    for i,(x,y) in enumerate(zip(a,b)):
                        if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);changes+=1
                position+=len(a)
        control_delta=dict(restored_entries=['10430'],declared_bytes=8,actual_changed_bytes=changes,source_sha256=build['derived_disc_sha256'],control=str(disc),control_sha256=sha(disc));save(out/'control-delta.json',control_delta)
    source=ROOT/'scripts/native_gameplay_observer.c';text=source.read_text();watched=WATCH.replace('ACQUIRE_ENTRY',hex(build['frame_acquire_entry'])+'u').replace('ACQUIRE_START',hex(build['frame_acquire_payload_start'])+'u').replace('ACQUIRE_END',hex(build['frame_acquire_end'])+'u').replace('ACQUIRE_RETURN',hex(build['frame_acquire_entry']+62)+'u')
    init_watch=r'''
static struct cpu table_incoming;
static uint32_t table_handles[50];
static unsigned table_pending;
static uint64_t table_entries,table_native_entries,table_returns,table_old_steps,table_errors,table_native_steps;
static void watch_table(uint32_t pc){
    if(pc==0x1aeda){if(table_pending)table_errors++;table_pending=1;table_entries++;read_cpu(&table_incoming);for(unsigned i=0;i<50;i++)table_handles[i]=rd32(0x15b536u+12*i);emit(pc);}
    if(pc>0x1aeda&&pc<0x1af04)table_old_steps++;
    if(pc==TABLE_ENTRY)table_native_entries++;
    if(pc>=TABLE_ENTRY&&pc<TABLE_END)table_native_steps++;
    if(pc==TABLE_RETURN){
        struct cpu current;read_cpu(&current);table_returns++;emit(pc);
        if(!table_pending||current.r[0]!=588||current.r[1]!=((table_incoming.r[1]&0xffff0000u)|50u)||current.r[8]!=0x15b534u||current.sr!=(table_incoming.sr&0xffe0u)||current.usp!=table_incoming.usp||current.ssp!=table_incoming.ssp)table_errors++;
        for(unsigned i=2;i<16;i++)if(i!=8&&current.r[i]!=table_incoming.r[i])table_errors++;
        for(unsigned i=0;i<50;i++)if(rd16(0x15b534u+12*i)!=0xffffu||rd16(0x15b53au+12*i)||rd16(0x15b53cu+12*i)||rd16(0x15b53eu+12*i)||rd32(0x15b536u+12*i)!=table_handles[i])table_errors++;
        table_pending=0;
    }
}
'''
    init_watch=init_watch.replace('TABLE_ENTRY',hex(build['resource_table_initialize_entry'])+'u').replace('TABLE_RETURN',hex(build['resource_table_initialize_return'])+'u').replace('TABLE_END',hex(build['resource_table_initialize_entry']+78)+'u')
    leaf_path=ROOT/'scripts/native_cache_leaf_observer.inc.c';leaf=leaf_path.read_text();parts=build['components']
    def carray(values):return '{'+','.join(str(x)+'u' for x in values)+'}'
    replacements={'__ORIG_ENTRY__':carray([x['original_entry'] for x in parts]),'__ORIG_END__':carray([0x1ac68,0x1ae88,0x1aeda]),'__CODE_START__':carray([x['address'] for x in parts]),'__CODE_ENTRY__':carray([x['entry'] for x in parts]),'__CODE_END__':carray([x['end'] for x in parts]),'__CODE_RETURN__':carray([x['return_address'] for x in parts]),'__ALL_CODE_START__':str(parts[0]['address'])+'u','__ALL_CODE_END__':str(parts[-1]['end'])+'u','__HEAP_RETURN__':str(build['symbols']['biwn_native_heap_initialize_return'])+'u','__HEAP_FLOOR__':str(build['heap_start'])+'u'}
    for key,value in replacements.items():assert key in leaf;leaf=leaf.replace(key,value)
    watched+='\n'+leaf
    watched+='\n'+init_watch
    geometry_path=ROOT/'scripts/native_geometry_outside_observer.inc.c';geometry=geometry_path.read_text()
    for key,value in {'__GEOMETRY_START__':build['geometry_outside_start'],'__GEOMETRY_END__':build['geometry_outside_end'],'__GEOMETRY_ENTRY__':build['geometry_outside_entry'],'__GEOMETRY_RETURN__':build['geometry_outside_return']}.items():
        assert key in geometry;geometry=geometry.replace(key,str(value)+'u')
    watched+='\n'+geometry
    select_path=ROOT/'scripts/native_geometry_select_observer_v3.inc.c';select=select_path.read_text()
    for key,value in {'__SELECT_START__':build['geometry_select_start'],'__SELECT_END__':build['geometry_select_end'],'__SELECT_ENTRY__':build['geometry_select_entry'],'__SELECT_RETURN__':build['geometry_select_return']}.items():
        assert key in select;select=select.replace(key,str(value)+'u')
    watched+='\n'+select
    scan_path=ROOT/'scripts/native_geometry_scan_observer.inc.c';scan=scan_path.read_text()
    for key,value in {'__SCAN_START__':build['geometry_scan_start'],'__SCAN_END__':build['geometry_scan_end'],'__SCAN_ENTRY__':build['geometry_scan_entry'],'__SCAN_RETURN__':build['geometry_scan_return']}.items():
        assert key in scan;scan=scan.replace(key,str(value)+'u')
    watched+='\n'+scan
    door_path=ROOT/'scripts/native_doorway_observer.inc.c';door=door_path.read_text()
    for key,value in {'__DOOR_START__':build['doorway_start'],'__DOOR_END__':build['doorway_end'],'__DOOR_ENTRY__':build['doorway_entry'],'__DOOR_RETURN__':build['doorway_return']}.items():
        assert key in door;door=door.replace(key,str(value)+'u')
    watched+='\n'+door

    marker='int32_t observe(uint32_t pc) {';assert text.count(marker)==1;text=text.replace(marker,watched+'\n'+marker)
    marker='    steps++;';assert text.count(marker)==1;text=text.replace(marker,marker+'\n    watch_acquire(pc);watch_table(pc);watch_leaf(pc);watch_geometry(pc);watch_select(pc);watch_scan(pc);watch_door(pc);')
    marker='    return 0;\n}\nstatic void array';assert text.count(marker)==1;text=text.replace(marker,'    int32_t result=next_owner?next_owner(pc):0;if(result)errors++;return result;\n}\nstatic void array')
    table_report=r'''
    fprintf(file,",\"table_entries\":%llu,\"table_native_entries\":%llu,\"table_returns\":%llu,\"table_old_steps\":%llu,\"table_errors\":%llu,\"table_pending\":%u,\"table_native_steps\":%llu",(unsigned long long)table_entries,(unsigned long long)table_native_entries,(unsigned long long)table_returns,(unsigned long long)table_old_steps,(unsigned long long)table_errors,table_pending,(unsigned long long)table_native_steps);
'''
    leaf_report=r'''
    array(file,"lookup_counts",leaf_counts[0],8);array(file,"single_counts",leaf_counts[1],8);array(file,"multi_counts",leaf_counts[2],8);array(file,"leaf_min_headroom",leaf_min_headroom,3);array(file,"leaf_max_depth",leaf_max_depth,3);
    fprintf(file,",\"leaf_pending\":%u,\"lookup_matches\":%llu,\"lookup_misses\":%llu,\"single_decrements\":%llu,\"multi_nonnegative\":%llu,\"multi_decrements\":%llu,\"heap_floor_errors\":%llu",leaf_pending_any,(unsigned long long)lookup_matches,(unsigned long long)lookup_misses,(unsigned long long)single_decrements,(unsigned long long)multi_nonnegative,(unsigned long long)multi_decrements,(unsigned long long)heap_floor_errors);
'''
    geometry_report=r'''
    fprintf(file,",\"geometry_entries\":%llu,\"geometry_native_entries\":%llu,\"geometry_returns\":%llu,\"geometry_old_steps\":%llu,\"geometry_native_steps\":%llu,\"geometry_errors\":%llu,\"geometry_pending\":%u,\"geometry_early\":%llu,\"geometry_inside\":%llu,\"geometry_last_outside\":%llu,\"geometry_user_observations\":%llu,\"geometry_stack_outside\":%llu,\"geometry_min_headroom\":%u,\"geometry_max_depth\":%u",(unsigned long long)geometry_entries,(unsigned long long)geometry_native_entries,(unsigned long long)geometry_returns,(unsigned long long)geometry_old_steps,(unsigned long long)geometry_native_steps,(unsigned long long)geometry_errors,geometry_pending,(unsigned long long)geometry_early,(unsigned long long)geometry_inside,(unsigned long long)geometry_last_outside,(unsigned long long)geometry_user_observations,(unsigned long long)geometry_stack_outside,geometry_min_headroom,geometry_max_depth);
'''
    select_report=r'''
    fprintf(file,",\"select_entries\":%llu,\"select_native_entries\":%llu,\"select_returns\":%llu,\"select_old_steps\":%llu,\"select_native_steps\":%llu,\"select_errors\":%llu,\"select_pending\":%u,\"select_successes\":%llu,\"select_failures\":%llu,\"select_user_observations\":%llu,\"select_stack_outside\":%llu,\"select_min_headroom\":%u,\"select_max_depth\":%u",(unsigned long long)select_entries,(unsigned long long)select_native_entries,(unsigned long long)select_returns,(unsigned long long)select_old_steps,(unsigned long long)select_native_steps,(unsigned long long)select_errors,select_pending,(unsigned long long)select_successes,(unsigned long long)select_failures,(unsigned long long)select_user_observations,(unsigned long long)select_stack_outside,select_min_headroom,select_max_depth);
'''
    scan_report=r'''
    fprintf(file,",\"scan_entries\":%llu,\"scan_native_entries\":%llu,\"scan_returns\":%llu,\"scan_old_steps\":%llu,\"scan_native_steps\":%llu,\"scan_errors\":%llu,\"scan_pending\":%u,\"scan_successes\":%llu,\"scan_failures\":%llu,\"scan_skips\":%llu,\"scan_iterations\":%llu,\"scan_user_observations\":%llu,\"scan_stack_outside\":%llu,\"scan_min_headroom\":%u,\"scan_max_depth\":%u",(unsigned long long)scan_entries,(unsigned long long)scan_native_entries,(unsigned long long)scan_returns,(unsigned long long)scan_old_steps,(unsigned long long)scan_native_steps,(unsigned long long)scan_errors,scan_pending,(unsigned long long)scan_successes,(unsigned long long)scan_failures,(unsigned long long)scan_skips,(unsigned long long)scan_iterations,(unsigned long long)scan_user_observations,(unsigned long long)scan_stack_outside,scan_min_headroom,scan_max_depth);
'''
    door_report=r'''
    fprintf(file,",\"door_entries\":%llu,\"door_native_entries\":%llu,\"door_returns\":%llu,\"door_old_steps\":%llu,\"door_native_steps\":%llu,\"door_errors\":%llu,\"door_pending\":%u,\"door_count_rejects\":%llu,\"door_sentinels\":%llu,\"door_key_mismatches\":%llu,\"door_successes\":%llu,\"door_user_observations\":%llu,\"door_stack_outside\":%llu,\"door_min_headroom\":%u,\"door_max_depth\":%u",(unsigned long long)door_entries,(unsigned long long)door_native_entries,(unsigned long long)door_returns,(unsigned long long)door_old_steps,(unsigned long long)door_native_steps,(unsigned long long)door_errors,door_pending,(unsigned long long)door_count_rejects,(unsigned long long)door_sentinels,(unsigned long long)door_key_mismatches,(unsigned long long)door_successes,(unsigned long long)door_user_observations,(unsigned long long)door_stack_outside,door_min_headroom,door_max_depth);
'''
    marker='    array(file,"rng_entries",rng_entries,8);';assert text.count(marker)==1;text=text.replace(marker,REPORT+'\n'+table_report+'\n'+leaf_report+'\n'+geometry_report+'\n'+select_report+'\n'+scan_report+'\n'+door_report+'\n    select_debug_dump(file);scan_debug_dump(file);door_debug_dump(file);\n'+marker)
    observer=out/'frame-acquire-observer.c';observer.write_text(text);library=out/'libframe-acquire-observer.dylib';compiled=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'observer-build.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    text=template.read_text();marker="        rom = c.c_void_p.in_dll(core, 'jaguarMainROM').value";assert text.count(marker)==1
    install=f'''        assert args.CPU_mode=='reference'
        observer=c.CDLL({str(library)!r})
        observer_payload=c.create_string_buffer(Path({build['component']!r}).read_bytes())
        observer.begin_observe.argtypes=[c.c_void_p,c.c_void_p,c.c_int,c.c_void_p,c.c_uint32,c.c_char_p];observer.begin_observe.restype=c.c_int
        assert observer.begin_observe(ram_pointer,c.cast(core.BIWNReadCPUState,c.c_void_p),1,observer_payload,len(observer_payload.raw)-1,str(out/'gameplay-events.bin').encode())==0
        observer.set_next_owner.argtypes=[c.c_void_p];observer.set_next_owner(c.cast(owner,c.c_void_p))
        WATCH_OWNER=c.CFUNCTYPE(c.c_int32,c.c_uint32);watch_owner=WATCH_OWNER(('observe',observer));core.BIWNSetCPUExecOwner.argtypes=[WATCH_OWNER,c.c_int];core.BIWNSetCPUExecOwner(watch_owner,0)
        observer.set_frame.argtypes=[c.c_uint32]
'''
    text=text.replace(marker,install+marker);marker='            current_frame = i+1';assert text.count(marker)==1;text=text.replace(marker,marker+'\n            observer.set_frame(current_frame)')
    marker="        report['C_processor_backends']=finish_processors()";at=text.rindex(marker)
    finish="        observer.finish_observe.argtypes=[c.c_char_p];observer.finish_observe.restype=c.c_int\n        assert observer.finish_observe(str(out/'gameplay-observation.json').encode())==0\n        report['native_compiled_game_C_execution']=True\n"
    text=text[:at]+finish+text[at:]
    old="report['C_CPU_backend']['scope']='SourceCPUfromHLEpreparedinitialPC,not gatedat4000; no originalCPUopcodefallback duringthe testedframes. SourceGPU/DSP/IRQ selection+entry; platformHLE,devices,blitter/OP,IRQlines+ACK/commit/prefetch/emulatorcostservices retained.'";assert text.count(old)==1;text=text.replace(old,"report['C_CPU_backend']['scope']='Retained native emulator CPU/GPU/DSP/IRQ execute the derived disc,including compiled native68000routine1AC68. No host source-instruction processor replacements; read-only observer chains the original reference callback.'")
    probe=out/'probe.py';compile(text,str(probe),'exec');probe.write_text(text)
    command=list(parent['command']);command[2]=str(probe);command[command.index('--CPU-mode')+1]='reference';command[command.index('--disc')+1]=str(disc);command[command.index('--output')+1]=str(out/'candidate')
    state=dict(status='running_fresh_native_doorway_merchant_route',pid=os.getpid(),directory=str(out),command=command,build_proof=str(bp),build_proof_sha256=sha(bp),native_reference_reused=True,reference=parent['reference'],checkpoint_restores=0,host_guest_RAM_writes=0,frame_acquire_entry=build['frame_acquire_entry'],new_training=False,default_promoted=False,whole_game_complete=False,variant='complete10430doorway entry plus preceding native geometry routines; kernel attribution recorded separately',kernel_attribution=build['kernel_attribution'],source_sha256={str(p):sha(p)for p in [out/'runner-as-run.py',tagged_path,monitor_path,leaf_path,geometry_path,select_path,scan_path,door_path,observer,library,probe,template,Path(parent['reference'])/'report.json',Path(parent['reference'])/'frontend-PCM.s16le']},doorway_monitor_scope='Complete10430 plus preceding geometry routines: full D0/D1/A0/A1/SR/register-bank returns and six doorway fields, with source-ordered shadow writes for record/actor overlap and task stack monitoring. Any disagreement retained as an error; component fixtures separately cover changing reads.',scope='Live read-only monitor checks callee-saved registers,public LINK/MOVEM bytes,return NZVC and upperSR,loader arg/register consistency and task stacks; it does not independently predict full D0/D1/A0/A1/X/cache algorithm outputs. Fresh derived native68000disc through the full adaptive merchant/media/outdoor route. Original emulator processors/platform retained. Read-only observer chains unchanged reference callback and checks live1AC68caller ABI,partial flags and stacks at compiled returns. Additionally checks actual lookup/single/group releases inread-only caller/cache oracles,andactual1AEDAinitialization full output registers/SR/banks,all50tags/ready/refs anduntouched handle bytes. No source CPU/GPU/DSPowners,guest writes or savestate restore. Exact old per-frame equality is measured,not assumed across compiled-code timing/layout changes.')
    state.update(same_layout_control=args.same_layout_control,control_delta=control_delta,stack_model='Existing source task context header38bytes,allocation0x404;measure usermode accesses only,with current task read atC0920. Original and compiled returns monitored separately.')
    pointer=ROOT/'verification'/('native-doorway-control-current.json'if args.same_layout_control else'native-doorway-candidate-current.json')
    def mark():save(out/'protocol.json',state);save(pointer,state)
    mark()
    try:
        with(out/'candidate.log').open('w')as log:
            child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;mark();code=child.wait()
        state['exit_code']=code;assert code==0,'Native scene route failed; retain exact child outputs'
        report=json.loads((out/'candidate/report.json').read_text());control=json.loads((Path(parent['reference'])/'report.json').read_text());observed=json.loads((out/'candidate/gameplay-observation.json').read_text());assert not observed['errors']and not observed['copy_errors']and not report['C_CPU_backend']['stats']['errors']
        last=report['frames'][-1];returned=last['player_mode_word']==1 and last['floor_word']==0 and last['navigation']['outdoor_hold']>=120
        fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','video_sha256','navigation'];different={key:sum(a[key]!=b[key]for a,b in zip(report['frames'],control['frames']))for key in fields};PCM_equal=sha(out/'candidate/frontend-PCM.s16le')==sha(Path(parent['reference'])/'frontend-PCM.s16le')
        reached=observed['acquire_native_entries']>0
        body_ownership=reached and observed['acquire_entries']==observed['acquire_native_entries'] and observed['acquire_old_steps']==0
        monitor_pass=body_ownership and observed['acquire_entries']==observed['acquire_returns']and observed['acquire_monitor_errors']==observed['acquire_pending']==observed['acquire_user_stack_outside']==0 and observed['acquire_user_stack_observations']>0 and observed['table_entries']==observed['table_native_entries']==observed['table_returns']==1 and observed['table_old_steps']==observed['table_errors']==observed['table_pending']==0
        leaf_pass=True
        for key in ['lookup_counts','single_counts','multi_counts']:
            values=observed[key];entry,native,returned_count,old_steps,_,errors,_,outside=values
            owned=native==entry and old_steps==0
            leaf_pass &= owned and entry==returned_count and errors==outside==0
        monitor_pass=monitor_pass and leaf_pass and observed['leaf_pending']==observed['heap_floor_errors']==0 and observed['heap_inits']>0 and observed['heap_base']==build['heap_start']
        geometry_reached=observed['geometry_entries']>0
        geometry_owned=observed['geometry_native_entries']==observed['geometry_entries'] and observed['geometry_old_steps']==0
        geometry_pass=geometry_reached and geometry_owned and observed['geometry_entries']==observed['geometry_returns'] and observed['geometry_errors']==observed['geometry_pending']==observed['geometry_stack_outside']==0
        monitor_pass=monitor_pass and geometry_pass
        select_reached=observed['select_entries']>0
        select_owned=observed['select_native_entries']==observed['select_entries'] and observed['select_old_steps']==0
        select_pass=select_reached and select_owned and observed['select_entries']==observed['select_returns'] and observed['select_errors']==observed['select_pending']==observed['select_stack_outside']==0
        monitor_pass=monitor_pass and select_pass
        scan_reached=observed['scan_entries']>0
        scan_owned=observed['scan_native_entries']==observed['scan_entries'] and observed['scan_old_steps']==0
        scan_pass=scan_reached and scan_owned and observed['scan_entries']==observed['scan_returns'] and observed['scan_errors']==observed['scan_pending']==observed['scan_stack_outside']==0
        monitor_pass=monitor_pass and scan_pass
        door_reached=observed['door_entries']>0
        door_owned=(observed['door_native_entries']==0 and observed['door_old_steps']>0) if args.same_layout_control else observed['door_native_entries']==observed['door_entries'] and observed['door_old_steps']==0
        door_pass=door_reached and door_owned and observed['door_entries']==observed['door_returns'] and observed['door_errors']==observed['door_pending']==observed['door_stack_outside']==0
        monitor_pass=monitor_pass and door_pass
        state.update(status='terminal_native_doorway_route_pending_review',frames=len(report['frames']),reference_frames=len(control['frames']),compared_prefix_frames=min(len(report['frames']),len(control['frames'])),frame_differences=different,PCM_equal=PCM_equal,nonzero_audio_samples=report['audio']['nonzero_samples'],returned_outdoors=returned,native_acquire_reached=reached,geometry_reached=geometry_reached,geometry_monitor_pass=geometry_pass,select_reached=select_reached,select_monitor_pass=select_pass,scan_reached=scan_reached,scan_monitor_pass=scan_pass,door_reached=door_reached,door_monitor_pass=door_pass,live_monitor_pass=monitor_pass,observations=observed,report_sha256=sha(out/'candidate/report.json'));mark();print(json.dumps({k:state[k]for k in ['status','frames','frame_differences','PCM_equal','returned_outdoors','native_acquire_reached','live_monitor_pass']}),flush=True)
    except BaseException as error:state.update(status='terminal_native_doorway_route_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
