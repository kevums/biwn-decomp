"""Review the fresh deeper-helper/original-geometry pair and exact layout gates."""
import json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
import check_native_deck_retained_plane_v3b as five
V=ROOT/'verification'
def read(p):return json.loads(Path(p).read_text())


def main():
    out=V/'native-Deck-plane-gameplay-review-v3'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    bp=V/'native-Deck-plane-disc-build-v3-current.json';build=read(bp);bound={Path(__file__),bp,Path(five.__file__)}
    for key in ['derived_disc','derived_stage','component']:assert sha(build[key])==build[key+'_sha256'];bound.add(Path(build[key]))
    def bind(path):
        proof=read(path)
        for p,h in proof['source_sha256'].items():assert sha(p)==h,p;bound.add(Path(p))
        bound.add(Path(path));return proof
    final=bind(V/'native-Deck-plane-final-v3-current.json');assert final['status']=='terminal_deeper_candidate_final_component_startup_heap_gates_pass'and final['build_sha256']==sha(bp)
    for name,count in [('native-Deck-outer-plane-final-v3-current.json',1280),('native-deck-retained-plane-final-v3-current.json',4992),('native-Deck-plane-final-geometry-v3-current.json',256),('native-Deck-outer-fallback-plane-final-v3-current.json',384),('native-Deck-outer-waits-plane-final-v3-current.json',192),('native-Deck-outer-connected-plane-v3-current.json',128),('shared-Deck-fallback-plane-final-v3-current.json',1280),('native-deck-alias-nesting-plane-final-v3-current.json',128),('native-plane-geometry-alias-v3-current.json',128)]:
        proof=bind(V/name);assert proof['completed']==count;bound.add(Path(proof['directory'])/'cases.json')
    startup=bind(V/'native-Deck-plane-startup-heap-v3-current.json');capacity=bind(V/'native-Deck-plane-capacity-v3-current.json')
    assert startup['startup_cases']==6 and startup['heap_initialize_cases']==192 and capacity['cases']==36
    regions=bind(V/'shared-Deck-region-check-plane-v3-current.json');outer_qualifier=bind(V/'outer-plane-observer-qualified-v3-current.json');geometry_qualifier=bind(V/'plane-observer-qualified-v3-current.json')
    assert len(regions['negative_controls'])==88 and outer_qualifier['rejected_fault_controls']==18 and geometry_qualifier['rejected_fault_controls']==34
    component=Path(build['component']).read_bytes();base=build['resident_address'];jobs={};reports={};observations={};used={};final_heap={}
    for lane in ['candidate','control']:
        path=V/f'native-Deck-plane-geometry-v3-{lane}-current.json';job=bind(path);assert job['status']=='terminal_fresh_plane_geometry_route_pending_review'
        assert job['build_sha256']==sha(bp) and not job['snapshot_restores']and not job['host_guest_RAM_writes']and not job['host_CPU_or_task_seeds']
        jobs[lane]=job;report=read(job['report']);assert sha(job['report'])==job['report_sha256'];reports[lane]=report
        assert not report['captured_state_input']and not report['host_CPU_or_GPU_register_seed']
        trial=report['ordinary_Deck_input_trial'];assert 400<=len(trial['inputs'])<=912 and trial['start_frame']>20000
        assert len(report['frames'])==trial['start_frame']+len(trial['inputs'])
        folder=Path(job['report']).parent
        observations[lane]={k:read(folder/f'{k}-observation.json')for k in ['gameplay','shared','face','geometry','outer']}
        obs=observations[lane]['gameplay'];shared=observations[lane]['shared'];face=observations[lane]['face'];geometry=observations[lane]['geometry'];outer=observations[lane]['outer']
        errors={k:x for k,x in obs.items()if isinstance(x,(int,float))and any(w in k for w in ['error','pending','outside','corruption','collision'])};assert errors and not any(errors.values()),errors
        assert not any(shared[k]for k in ['errors','pending','C_stack_outside'])
        assert shared['public_entries'][:4]==shared['native_entries'][:4]==shared['native_returns'][:4]and min(shared['native_returns'][:4])>0
        assert shared['helper_entries']==shared['helper_returns']and shared['original_body_steps'][:4]==[0]*4 and shared['fallback_entries']==[0]*5
        assert obs['mb_entries']==obs['mb_native']==obs['mb_returns']and min(obs['mb_returns'])>0
        assert obs['acquire_entries']==obs['acquire_returns']and obs['acquire_pending']==0
        assert face['entries']==face['returns']==face['positive_speed_entries']>0 and face['errors']==face['pending']==face['original_parent_returns']==0
        assert face['native_parent_returns']==face['suspended_native_parent_checks']==face['returns']
        assert geometry['entries']==geometry['returns']==geometry['matched_outer_parent_returns']>0
        assert geometry['helper_entries']==geometry['helper_returns']==[geometry['entries']]*5 and geometry['errors']==geometry['pending']==0
        if lane=='candidate':
            assert geometry['original_body_steps']==0 and shared['native_returns'][4]==geometry['entries']
            assert geometry['compiled_helper_services']==geometry['compiled_helper_markers']==[geometry['entries']]*3+[0]*2
            assert geometry['transform_entries']==geometry['transform_returns']==geometry['entries']
            assert geometry['original_transform_entries']==geometry['original_transform_returns']==geometry['original_transform_steps']==0
        else:
            assert geometry['original_body_steps']>0 and shared['native_entries'][4]==shared['native_returns'][4]==0 and shared['original_body_steps'][4]>0
            assert geometry['compiled_helper_services']==geometry['compiled_helper_markers']==[0]*5 and geometry['transform_entries']==geometry['transform_returns']==0
            assert geometry['original_transform_entries']==geometry['original_transform_returns']==geometry['entries']and geometry['original_transform_steps']>0
        assert outer['errors']==outer['pending']==outer['helper_pending']==outer['C_stack_outside']==outer['fallbacks']==0
        assert outer['helper_entries']==outer['helper_returns']and all(outer['helper_entries'][k]>0 for k in [0,1,5,11,12])
        assert outer['helper_entries'][1]==shared['native_returns'][3]and outer['helper_entries'][5]==geometry['returns']
        assert outer['public_entries']==outer['native_entries']==outer['native_returns']>0 and outer['original_returns']==outer['original_body_steps']==0
        assert outer['C_stack_observations']>0 and outer['C_stack_low_offset']>=144 and outer['protected_frame_checks']>0
        last=report['frames'][-1];assert last['scene_word']==312 and last['player_mode_word']==1 and last['movie_flag_words']==[0,0]
        ram_path=folder/'RAM-final.bin';ram=ram_path.read_bytes();assert sha(ram_path)==report['final_RAM_sha256']
        for lo,hi in [(base,build['arena_address']),(build['arena_end'],build['deck_arena_address'])]:assert ram[lo:hi]==component[lo-base:hi-base]
        used[lane]=dict(Deck=[],outer=[])
        for slot in range(101):
            at=build['deck_arena_address']+slot*1024
            for lo,hi in five.FENCES:assert ram[at+lo:at+hi]==component[at-base+lo:at-base+hi]
            for _,off,_,_ in five.LAYOUT.values():assert ram[at+off+114:at+off+118]==bytes(4)
            assert ram[at+392:at+396]==component[at-base+392:at-base+396]
            if ram[at:at+1024]!=component[at-base:at-base+1024]:used[lane]['Deck'].append(slot)
            at=build['outer_arena_address']+slot*576
            for lo,hi in build['outer_fences']:assert ram[at+lo:at+hi]==component[at-base+lo:at-base+hi]
            assert ram[at+130:at+134]==bytes(4)
            if ram[at:at+576]!=component[at-base:at-base+576]:used[lane]['outer'].append(slot)
        assert used[lane]['outer']
        for slot in range(102):
            at=build['arena_address']+slot*256
            for lo in [0,240]:assert ram[at+lo:at+lo+16]==component[at-base+lo:at-base+lo+16]
        final_heap[lane]=int.from_bytes(ram[0x112d64:0x112d68],'big')
        for file in ['report.json','gameplay-observation.json','shared-observation.json','face-observation.json','geometry-observation.json','outer-observation.json','RAM-final.bin','state-final.bin','original-emulator-final-frame.png']:bound.add(folder/file)
    a,b=reports['candidate'],reports['control'];start=a['ordinary_Deck_input_trial']['start_frame'];assert start==b['ordinary_Deck_input_trial']['start_frame']
    ignored={'full_RAM_sha256','stage_sha256'}
    for left,right in zip(a['frames'][:start],b['frames'][:start]):assert {k:x for k,x in left.items()if k not in ignored}=={k:x for k,x in right.items()if k not in ignored},left['frame']
    compared=min(len(a['frames']),len(b['frames']));matching=sum(x['video_sha256']==y['video_sha256']for x,y in zip(a['frames'],b['frames']));final_equal=a['frames'][-1]['video_sha256']==b['frames'][-1]['video_sha256']
    differences=[]
    for left,right in zip(a['frames'],b['frames']):
        keys=[k for k in left if k not in ignored and left[k]!=right[k]]
        if keys:differences.append(dict(frame=left['frame'],differing_fields=keys))
    save(out/'recorded-frame-differences.json',differences)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=session/'nextstage-mapping.json';offset=read(mapping)['payload_raw_cdi_offset']+0x11ad4-0x4000
    command=jobs['control']['command'];control_disc=Path(command[command.index('--disc')+1]);changed=position=0
    with Path(build['derived_disc']).open('rb')as left_file,control_disc.open('rb')as right_file:
        while True:
            left,right=left_file.read(1048576),right_file.read(1048576);assert len(left)==len(right)
            if not left:break
            if left!=right:
                for i,(x,y)in enumerate(zip(left,right)):
                    if x!=y:assert offset<=position+i<offset+8;changed+=1
            position+=len(left)
    assert 0<changed<=8
    for p,h in build['source_sha256'].items():assert sha(p)==h,p;bound.add(Path(p))
    bound.update([mapping,control_disc,V/'native-Deck-six-reviewed-v1-current.json',out/'recorded-frame-differences.json'])
    proof=dict(status='terminal_fresh_four_helper_geometry_candidate_observed_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),
        build=str(bp),build_sha256=sha(bp),disc=build['derived_disc'],disc_sha256=build['derived_disc_sha256'],native_code_bytes=build['linked_component_bytes'],total_reservation_bytes=build['component_bytes'],initial_heap_bytes=build['initial_heap_bytes'],
        installed_recovered_Deck_entries=build['installed_Deck_entries'],remaining_hosted_only_recovered_Deck_entries=[],candidate_frames=len(a['frames']),control_frames=len(b['frames']),candidate_trial_frames=len(a['ordinary_Deck_input_trial']['inputs']),control_trial_frames=len(b['ordinary_Deck_input_trial']['inputs']),
        native_five_returns={lane:dict(zip(five.LAYOUT,observations[lane]['shared']['native_returns']))for lane in observations},outer_observations={lane:x['outer']for lane,x in observations.items()},geometry_observations={lane:x['geometry']for lane,x in observations.items()},face_observations={lane:x['face']for lane,x in observations.items()},
        native_GPU_returns={lane:x['gameplay']['mb_returns']for lane,x in observations.items()},all_runtime_errors_pending_outside_zero=True,all_three_native_arena_fences_pass=True,all_active_flags_clear=True,immutable_code_unchanged=True,used_slots=used,final_heap_free=final_heap,
        pretrial_recorded_fields_equal_frames=start,pretrial_static_RAM_stage_hashes_excluded=True,control_declared_redirect_bytes=8,control_changed_disc_bytes=changed,compared_video_frames=compared,matching_video_frames=matching,differing_video_frames=compared-matching,final_video_equal=final_equal,recorded_state_differing_frames=len(differences),cycle_identity_verified=False,
        observer_region_fault_controls=88,outer_watcher_fault_controls=18,geometry_watcher_fault_controls=34,prior_five_caller_disc_preserved=True,default_preview_promoted=False,current_GUI_native_Deck_callers=6,new_training=False,new_model_authored_game_code=False,whole_game_complete=False,physical_console_verified=False,
        new_internal_helper_entries=['10968','10ba4','11384','110d4'],direct_matrix110D4_original_body_in_candidate=False,global110D4_entry_unpatched=True,installed_preview_changed=False,
        scope='Fresh candidate and same-layout eight-byte original-geometry control. The other five public callers stay compiled in both lanes. All five geometry dependencies execute originally in the control. Candidate runs four compiled C helpers;outer services and nested110D4C service complete at their actual C returns before logical RTS pop. The control executes all original helpers,including real nested110D4entry/RTS. Global110D4 remains unpatched for other callers. Ordinary controller inputs, no checkpoint or guest-state seeds. Coordinator integration;no model source or optimizer update. Recorded pretrial fields exclude static RAM/stage hashes; active-trial timing/state/video differences are reported. Reached scheduler boundaries do not prove arbitrary suspension/reentry/IRQ. Retained HLE/emulator/original-helper dependencies, changed13-frame restoration,audio/physical fidelity and full-game source rebuilding remain incomplete.',
        source_sha256={str(p):sha(p)for p in bound})
    save(out/'review.json',proof);save(V/'native-Deck-plane-gameplay-reviewed-v3-current.json',proof)
    print(proof['status'],proof['outer_observations'],'video differences',proof['differing_video_frames'],'final video equal',final_equal,flush=True)


if __name__=='__main__':main()
