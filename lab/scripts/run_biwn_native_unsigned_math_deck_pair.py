"""Fresh ordinary-pad unsigned arithmetic candidate and identical-layout original-helper control."""
import argparse,hashlib,json,os,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from extract_biwn_stage import swap16
from run_biwn_native_fast_gameplay_route import make_probe,ROOT,sha,save

def classify_saved(out,state,build):
    assert all(code==0 for code in state['exit_codes'].values())
    observations={lane:json.loads((out/lane/'gameplay-observation.json').read_text())for lane in ['candidate','control']}
    reports={lane:json.loads((out/lane/'report.json').read_text())for lane in observations};payload=Path(build['component']).read_bytes();heap={}
    for lane,obs in observations.items():
        assert not obs['errors']and not obs['copy_errors']and obs['entry_copies']==1
        memory=(out/lane/'RAM-final.bin').read_bytes();assert sha(out/lane/'RAM-final.bin')==reports[lane]['final_RAM_sha256']
        heap[lane]=int.from_bytes(memory[0x112d60:0x112d64],'big');assert heap[lane]==build['heap_start']
        assert memory[build['resident_address']:build['resident_address']+len(payload)]==payload
    a,b=observations['candidate'],observations['control'];assert a['old_unsigned_body_steps']==[0,0]and b['compiled_unsigned_calls']==[0,0]
    assert a['unsigned_entries']==a['compiled_unsigned_calls']
    left,right=reports['candidate']['frames'],reports['control']['frames'];assert len(left)==len(right)==state['frames']
    fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','video_sha256']
    comparisons={k:dict(different_frames=sum(x[k]!=y[k]for x,y in zip(left,right)),first_different_frame=next((x['frame']for x,y in zip(left,right)if x[k]!=y[k]),None))for k in fields}
    state.update(status='terminal_fresh_format_selector_deck_pair_classified',observations=observations,comparisons=comparisons,
        final_RAM_heap_starts=heap,final_resident_payload_preserved=True,legacy_heap_hook_missed_relocated_init=True,
        actual_compiled_helper_exercised=any(a['compiled_unsigned_calls']),both_helpers_exercised=all(a['compiled_unsigned_calls']),
        PCM_equal=sha(out/'candidate/frontend-PCM.s16le')==sha(out/'control/frontend-PCM.s16le'),
        report_sha256={lane:sha(out/lane/'report.json')for lane in reports},timing_vs_algorithm_cause_resolved=False,
        scope='2600fresh HLEboot frames per lane with same ordinary pad schedule. Both discs contain the same two declared38byte selector/count repairs; not untouched-original behavior. Read-only observer returns0; retained CPU executes instructions. Same-layout control differs only two unsigned arithmetic redirects. Final RAM verifies heap and preserved resident payload. Legacy original-address heap observer does not see relocated native init. Differences compare unsigned arithmetic implementation plus runtime cost; algorithm/timing/IRQ causes unresolved. Exact linked component matrices have separate integration receipts. Long gameplay, cycle equivalence and physicalconsole remain unverified by this finite run.')
    state.pop('error',None)
    save(out/'protocol.json',state);save(ROOT/'verification/native-unsigned-math-selector-deck-pair-active.json',state);save(ROOT/'verification/native-unsigned-math-selector-deck-pair-current.json',state)
    print(state['status'],a['compiled_unsigned_calls'],json.dumps(comparisons),flush=True)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--analyze-existing',type=Path);args=parser.parse_args()
    if args.analyze_existing:
        out=args.analyze_existing.resolve();state=json.loads((out/'protocol.json').read_text());assert sha(state['build_proof'])==state['build_proof_sha256'];build=json.loads(Path(state['build_proof']).read_text())
        old=str(Path(__file__).resolve());snapshot=out/'driver-as-run.py'
        if old in state['source_sha256']:
            assert sha(snapshot)==state['source_sha256'][old];state['source_sha256'][str(snapshot)]=state['source_sha256'].pop(old)
        state['analysis_driver_sha256']=sha(__file__);state['analysis_correction']='Reused completed child outputs; replaced stale heap-hook assertion with report-bound final RAM heap/payload checks. Original failed classification and driver retained.'
        classify_saved(out,state,build);return
    bp=ROOT/'verification/native-unsigned-format-disc-build-current.json';build=json.loads(bp.read_text());assert sha(build['derived_disc'])==build['derived_disc_sha256']
    ep=ROOT/'verification/native-unsigned-format-disc-entry-current.json';entry=json.loads(ep.read_text());assert entry['status']=='terminal_native_entry_heap_and_component_pass'and entry['build_proof_sha256']==sha(bp)
    out=ROOT/'verification/native-unsigned-math-selector-deck-pair'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    control=out/'BIWN-23-format-same-layout-original-helper-control.cdi';shutil.copyfile(build['derived_disc'],control)
    session=Path(json.loads((ROOT/'projects/black-ice-white-noise/analysis/current-session.json').read_text())['directory']);mapping=json.loads((session/'nextstage-mapping.json').read_text());offset=mapping['payload_raw_cdi_offset'];patches=json.loads(Path(build['patch_manifest']).read_text())['patches'];intervals=[]
    with control.open('r+b')as stream:
        for address in [0xe61c,0xe67c]:
            row=next(p for p in patches if int(p['address'],16)==address);old=bytes.fromhex(row['original']);new=bytes.fromhex(row['replacement']);at=offset+address-0x4000;stream.seek(at);assert stream.read(len(new))==swap16(new);stream.seek(at);stream.write(swap16(old));intervals.append((at,at+len(old)))
        stream.flush();os.fsync(stream.fileno())
    differences=0;position=0
    with Path(build['derived_disc']).open('rb')as a,control.open('rb')as b:
        while True:
            left=a.read(1048576);right=b.read(1048576);assert len(left)==len(right)
            if not left:break
            for i,(x,y)in enumerate(zip(left,right)):
                if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);differences+=1
            position+=len(left)
    # Same declared selector repairs in both lanes; never patch guest RAM.
    recipe_path=ROOT/'verification/interactive-preview-recipe.json'
    recipe=json.loads(recipe_path.read_text());command=recipe['candidate']
    overlay_path=Path(command[command.index('--experimental-code-overlay')+1])
    overlay=json.loads(overlay_path.read_text());repairs=[row for row in overlay['patches']if int(row['address'],16)in [0x464a6,0x10ac2]]
    assert len(repairs)==2 and sum(len(bytes.fromhex(row['original']))for row in repairs)==38
    candidate_disc=out/'BIWN-23-format-selector-repaired-experimental.cdi'
    shutil.copyfile(build['derived_disc'],candidate_disc)
    repair_intervals=[]
    for row in repairs:
        old=bytes.fromhex(row['original']);new=bytes.fromhex(row['replacement']);assert len(old)==len(new)and len(old)%2==0
        at=offset+int(row['address'],16)-0x4000;repair_intervals.append((at,at+len(old)))
        for path in [candidate_disc,control]:
            with path.open('r+b')as stream:
                stream.seek(at);assert stream.read(len(old))==swap16(old)
                stream.seek(at);stream.write(swap16(new));stream.flush();os.fsync(stream.fileno())
    # Independently compare the entire patched candidate against its parent.
    repair_changed=0;position=0
    with Path(build['derived_disc']).open('rb')as a,candidate_disc.open('rb')as b:
        while True:
            left=a.read(1048576);right=b.read(1048576);assert len(left)==len(right)
            if not left:break
            for i,(x,y)in enumerate(zip(left,right)):
                if x!=y:assert any(lo<=position+i<hi for lo,hi in repair_intervals);repair_changed+=1
            position+=len(left)
    # Control must still differ only in the two unsigned arithmetic redirects.
    pair_changed=0;position=0
    with candidate_disc.open('rb')as a,control.open('rb')as b:
        while True:
            left=a.read(1048576);right=b.read(1048576);assert len(left)==len(right)
            if not left:break
            for i,(x,y)in enumerate(zip(left,right)):
                if x!=y:assert any(lo<=position+i<hi for lo,hi in intervals);pair_changed+=1
            position+=len(left)
    assert pair_changed==differences==11
    repair_proof=dict(status='separate_shared_selector_repair_discs_built',parent_disc=build['derived_disc'],parent_disc_sha256=sha(build['derived_disc']),
        candidate=str(candidate_disc),candidate_sha256=sha(candidate_disc),control=str(control),control_sha256=sha(control),
        parent_build_proof=str(bp),parent_build_proof_sha256=sha(bp),selector_repairs=repairs,
        declared_shared_repair_bytes=38,actual_candidate_changed_CDI_bytes=repair_changed,pair_changed_CDI_bytes=pair_changed,
        source_overlay=str(overlay_path),source_overlay_sha256=sha(overlay_path),host_guest_RAM_writes=0,
        default_promoted=False,whole_game_complete=False,
        scope='Two existing experimental selector/count repairs at464A6/10AC2 applied to both derived discs. Native compiled word-scan loader is inherited. Parent entry proof covers shared startup only; repaired gameplay requires this new run. Not untouched-original behavior.')
    save(out/'shared-selector-repair-build.json',repair_proof)
    source=ROOT/'scripts/native_gameplay_observer.c';text=source.read_text();marker='static uint32_t heap_base;';assert text.count(marker)==1
    text=text.replace(marker,marker+'\nstatic uint64_t unsigned_entries[2],compiled_unsigned_calls[2],old_unsigned_body_steps[2];')
    text=text.replace('static uint32_t heap_base;','static uint32_t heap_base;'+'\nstruct format_pending {unsigned live,kind;uint32_t sp,ret,task;};\nstatic struct format_pending fp[64];\nstatic uint64_t unsigned_returns[2],unsigned_user_observations[2],unsigned_stack_outside[2],unsigned_tracking_errors;\nstatic uint32_t unsigned_min_headroom[2]={0xffffffffu,0xffffffffu};\n')
    text=text.replace('int32_t observe(uint32_t pc) {',"\nstatic void watch_format(uint32_t pc){\n unsigned isentry=(pc==0xe61cu||pc==0xe67cu),any=0;\n for(unsigned j=0;j<64;j++)any|=fp[j].live;\n if(!any&&!isentry)return;\n struct cpu value;read_cpu(&value);uint32_t sp=value.r[15],task=rd32(0xc0920u);\n for(unsigned j=0;j<64;j++)if(fp[j].live&&pc==fp[j].ret&&sp==fp[j].sp+4u){unsigned_returns[fp[j].kind]++;fp[j].live=0;}\n if(isentry){\n  unsigned j;for(j=0;j<64;j++)if(!fp[j].live)break;\n  if(j==64){unsigned_tracking_errors++;return;}\n  fp[j]=(struct format_pending){1u,pc==0xe67cu,sp,rd32(sp),task};\n }\n for(unsigned j=0;j<64;j++)if(fp[j].live&&!(value.sr&0x2000u)&&task==fp[j].task){\n  unsigned kind=fp[j].kind;\n  /* Watch only the same user task while it executes this helper's original\n     body or resident code. Supervisor IRQ code/other tasks are excluded. */\n  if((pc>=0x15edc0u&&pc<0x15edc0u+payload_size)||\n     (kind==0u?pc>=0xe61cu&&pc<0xe67cu:pc>=0xe67cu&&pc<0xe68cu)){\n   unsigned_user_observations[kind]++;\n   if(!task||task>0x1ffbc0u||sp<task+38u||sp>task+0x404u)unsigned_stack_outside[kind]++;\n   else if(sp-task-38u<unsigned_min_headroom[kind])unsigned_min_headroom[kind]=sp-task-38u;\n  }\n }\n}\n"+'\nint32_t observe(uint32_t pc) {')
    text=text.replace('    steps++;','    steps++;\n    watch_format(pc);')
    text=text.replace('    array(file,\"rng_entries\",rng_entries,8);','\n    array(file,"unsigned_returns",unsigned_returns,2);array(file,"unsigned_user_observations",unsigned_user_observations,2);array(file,"unsigned_stack_outside",unsigned_stack_outside,2);\n    fprintf(file,",\\"unsigned_min_headroom\\":[%u,%u],\\"unsigned_tracking_errors\\":%llu",unsigned_min_headroom[0],unsigned_min_headroom[1],(unsigned long long)unsigned_tracking_errors);\n    unsigned pending=0;for(unsigned j=0;j<64;j++)pending+=fp[j].live;\n    fprintf(file,",\\"unsigned_pending_at_finish\\":%u",pending);\n'+'    array(file,\"rng_entries\",rng_entries,8);')
    marker='    steps++;';assert text.count(marker)==1
    extra='\n    const uint32_t fe[2]={0xe61c,0xe67c},fz[2]={0xe67c,0xe68c},fc[2]={'+','.join(hex(build['symbols'][k])for k in ['biwn_native_unsigned_divide','biwn_native_unsigned_remainder'])+'};\n    for(unsigned i=0;i<2;i++){if(pc==fe[i])unsigned_entries[i]++;if(pc==fc[i])compiled_unsigned_calls[i]++;if(pc>fe[i]&&pc<fz[i])old_unsigned_body_steps[i]++;}\n'
    text=text.replace(marker,marker+extra)
    marker='    array(file,"rng_entries",rng_entries,8);';assert text.count(marker)==1
    text=text.replace(marker,'    array(file,"unsigned_entries",unsigned_entries,2);array(file,"compiled_unsigned_calls",compiled_unsigned_calls,2);array(file,"old_unsigned_body_steps",old_unsigned_body_steps,2);\n'+marker)
    observer=out/'format-observer.c';observer.write_text(text);library=out/'libformat-observer.dylib';result=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(observer),'-o',str(library)],capture_output=True,text=True);(out/'observer-build.log').write_text(result.stdout+result.stderr);assert result.returncode==0,result.stderr
    original=ROOT/'projects/black-ice-white-noise/originals/BIWN#23.cdi';probe=out/'fresh-format-probe.py';probe.write_text(make_probe(ROOT/'scripts/probe_biwn_fresh_CD_boot.py',library,original,Path(build['component'])));compile(probe.read_text(),str(probe),'exec')
    probe_text=probe.read_text();probe_marker="floor_word=int.from_bytes(ram[0x49c62:0x49c64],'big'),";assert probe_text.count(probe_marker)==1;probe_text=probe_text.replace(probe_marker,probe_marker+"\n                       debug_overlay_word=int.from_bytes(ram[0x403cc:0x403ce],'big'),\n                       editor_state_word=int.from_bytes(ram[0x403d6:0x403d8],'big'),\n                       held_input_long=int.from_bytes(ram[0x49ba4:0x49ba8],'big'),");probe.write_text(probe_text);compile(probe_text,str(probe),'exec')

    frames=2600;prefix=ROOT/'verification/whole-merchant-global-fixed-input.json';windows=[dict(w,stop_frame=min(w['stop_frame'],1601))for w in json.loads(prefix.read_text())['windows']if w['start_frame']<=1600];windows += [dict(start_frame=1630,stop_frame=1640,buttons=['1']),dict(start_frame=1660,stop_frame=1670,buttons=['B','C']),dict(start_frame=1800,stop_frame=2000,buttons=['OPTION']),dict(start_frame=2100,stop_frame=2104,buttons=['0'])];inputs=out/'input.json';save(inputs,dict(windows=windows))
    core=ROOT/'verification/CPU-IRQ-selection-core-build/20261017T094441.859213Z/source/virtualjaguar_libretro.dylib'
    state=dict(status='prepared',pid=os.getpid(),directory=str(out),build_proof=str(bp),build_proof_sha256=sha(bp),entry_proof=str(ep),entry_proof_sha256=sha(ep),frames=frames,control_disc=str(control),control_disc_sha256=sha(control),control_changed_CDI_bytes=differences,control_change_scope='Only two6byte unsigned arithmetic redirects restored; identical payload/heap/startup/other rebuilt helpers.',shared_selector_repairs=repair_proof,entry_proof_shared_startup_only=True,commands=[],host_guest_RAM_writes=0,checkpoint_restores=0,whole_game_complete=False,source_sha256={str(p):sha(p)for p in [Path(__file__),observer,source,library,probe,inputs,prefix,core,recipe_path,overlay_path,out/'shared-selector-repair-build.json']})
    def mark():save(out/'protocol.json',state);save(ROOT/'verification/native-unsigned-math-selector-deck-pair-active.json',state)
    mark();children=[]
    try:
        for lane,disc in [('candidate',candidate_disc),('control',control)]:
            command=[str(ROOT/'.venv/bin/python'),'-u',str(probe),'--boot','hle','--frames',str(frames),'--core',str(core),'--disc',str(disc),'--frame-controller-script',str(inputs),'--capture-audio','--no-publish','--output',str(out/lane)]
            log=(out/(lane+'.log')).open('w');child=subprocess.Popen(command,stdout=log,stderr=subprocess.STDOUT);children.append((lane,child,log));state['commands'].append(dict(lane=lane,child_pid=child.pid,command=command))
        state['status']='running_fresh_format_selector_deck_pair';mark();print('PIDs',[p.pid for _,p,_ in children],flush=True)
        exit_codes={}
        for lane,child,log in children:exit_codes[lane]=child.wait();log.close()
        state['exit_codes']=exit_codes;assert not any(exit_codes.values()),exit_codes
        classify_saved(out,state,build)
    except BaseException as error:state.update(status='terminal_failed',error=repr(error));mark();raise
if __name__=='__main__':main()
