"""Publish the reproduced mailbox race and separately tested experimental repair."""
import json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def read(path):return json.loads(Path(path).read_text())
def main():
    names=['native-fast-core-first-corruption','native-fast-core-GPU-corruption','native-fast-core-blitter-handoff','native-fast-core-GPU-wait','native-fast-core-corrupt-blit-replay','native-fast-core-wait-format-disc-build','native-fast-core-wait-format-disc-entry','native-fast-core-wait-entry-selector-deck-pair','native-fast-core-wait-format-long-route','native-formatter-diagnostic-Analyst-reviewed']
    pointers={name:ROOT/'verification'/(name+'-current.json')for name in names};proofs={k:read(p)for k,p in pointers.items()}
    oldp=ROOT/'verification/native-formatter-experiment-publication-current.json';old=read(oldp);deps=dict(old['status_dependencies_sha256'])
    deps[str(oldp)]=sha(oldp)
    for name,p in pointers.items():
        d=proofs[name];assert d['status'].startswith('terminal_'),name;deps[str(p)]=sha(p)
        for field in ['source_sha256','output_sha256']:
            for path,h in d.get(field,{}).items():
                if path in deps:assert deps[path]==h,path
                deps[path]=h
    b=proofs['native-fast-core-wait-format-disc-build'];entry=proofs['native-fast-core-wait-format-disc-entry'];pair=proofs['native-fast-core-wait-entry-selector-deck-pair'];long=proofs['native-fast-core-wait-format-long-route'];replay=proofs['native-fast-core-corrupt-blit-replay']
    assert b['linked_component_bytes']==14690 and b['new_mailbox_cases']==256 and b['appended_wait_bytes']==26 and b['parent_resident_prefix_byte_identical']
    assert entry['entry_cases']==96 and entry['component_cases']==5151
    assert pair['exit_codes']==dict(candidate=0,control=0)and pair['frames']==2600
    wait_address=b['symbols']['biwn_GPU_wait_complete'];health={}
    for lane in ['candidate','control']:
        p=Path(pair['directory'])/lane/'report.json';report=read(p);rows=report['frames'];assert len(rows)==2600
        assert not any(int(row['CPU'],16)&1 for row in rows)
        assert all(row['raw_player_X']<=65535 and row['raw_player_Z']<=65535 for row in rows)
        obs=pair['observations'][lane];assert obs['formatter_stack_outside']==[0,0]and obs['formatter_returns'][1]==obs['formatter_entries'][1]>0
        samples=sum(wait_address<=int(row['CPU'],16)<wait_address+26 for row in rows);assert samples>0
        health[lane]=dict(frames=2600,no_odd_PC_in_recorded_frames=True,source_variadic_entries=obs['formatter_entries'][1],outer_variadic_returns=obs['formatter_returns'][1],compiled_core_and_variadic_calls=obs['compiled_formatter_calls'],formatter_stack_violations=obs['formatter_stack_outside'],observed_user_headroom_bytes=obs['formatter_min_headroom'][1],wait_body_frame_samples=samples,frame_samples_are_not_call_counts=True,final_player=dict(X=rows[-1]['raw_player_X'],Z=rows[-1]['raw_player_Z']))
        deps[str(p)]=sha(p);deps[str(Path(pair['directory'])/lane/'RAM-final.bin')]=sha(Path(pair['directory'])/lane/'RAM-final.bin')
    route=long['results']['fast'];assert route['merchant_reached']and route['completed_outdoor_hold']and route['executed_frames']==24975
    p=Path(long['directory'])/'fast/report.json';route_report=read(p);assert not any(int(row['CPU'],16)&1 for row in route_report['frames']);deps[str(p)]=sha(p)
    assert replay['captured_fast_whole_RAM_reproduced']and replay['fast_and_reference_RAM_equal']==[True,True]
    wait=proofs['native-fast-core-GPU-wait'];events=[json.loads(line)for line in(Path(wait['directory'])/'wait-events.jsonl').read_text().splitlines()]
    early=[row for row in events if row['frame']==1429 and row['phase']==1 and row['PC']==0xe0a4 and row['CPU_PC']==0x17e6a and row['busy']==0 and row['command']==0x6720];assert len(early)==1
    overlay=[row for row in events if row['frame']==1429 and row['phase']==1 and row['PC']==0x183e0];assert len(overlay)==1 and overlay[0]['busy']==0xffffffff and overlay[0]['previous_command']==0x6720
    # Verify all four added read-only replays preserve the recorded original
    # failed run's selected frame fields. This is not a whole-state equivalence.
    original_pair=read(ROOT/'verification/native-fast-core-entry-selector-deck-pair-current.json');baseline=read(Path(original_pair['directory'])/'control/report.json');fields=['CPU','GPU','DSP','raw_player_X','raw_player_Z','stage_sha256','video_sha256'];prefix={}
    for name in ['native-fast-core-first-corruption','native-fast-core-GPU-corruption','native-fast-core-blitter-handoff','native-fast-core-GPU-wait']:
        p=Path(proofs[name]['directory'])/'control/report.json';r=read(p);assert len(r['frames'])==1440
        assert all(all(a[k]==c[k]for k in fields)for a,c in zip(r['frames'],baseline['frames']));prefix[name]=dict(frames=1440,selected_fields=fields,different_selected_values=0);deps[str(p)]=sha(p)
    for path in [Path(__file__),Path(b['derived_disc']),Path(b['linked_component']),Path(b['component']),ROOT/'scripts/check_biwn_scheduler.py',ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'verification/biwn-movement-matrix-checks.json',ROOT/'verification/native-formatter-corruption-Analyst-current.json',ROOT/'verification/native-formatter-readable-Analyst-current.json']:
        deps[str(path)]=sha(path)
    for path,h in deps.items():assert Path(path).resolve().is_relative_to(ROOT)and sha(path)==h,path
    now=datetime.now(timezone.utc);out=ROOT/'verification/native-formatter-GPU-wait-publication'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=ROOT/'reports/native-formatter-GPU-wait-repair.txt'
    summary=('The latest separate BIWN experimental build has a14690byte resident payload with a26byte GPU wait repair. '
      'The prior14664resident bytes,16384byte reservation,heap162DC0 and startup layout remain identical. '
      'A captured failed control returned from the old completion wait while command6720 was still pending; '
      'the HUD then overwrote blitterA2base before the GPU renderer delay-slot store launched a blit. '
      'That single launch exactly reproduces the captured full2MB RAM result in both retained blitter engines. '
      'The repair waits for command acceptance as well as busy0.256native scripted mailbox/CCR/mode cases, '
      '96startup and5151installed keypadABI cases pass. Both fresh shared-selector-repaired Deck lanes now '
      'complete2600frames without recorded oddPC or formatter stack violations:672compiled variadic returns '
      'versus800source-wrapper control returns. Position/video differences remain,so this is not frame equivalence. '
      'A fresh repaired raw-disc adaptive route reaches the merchant and completes the outdoor return in24975frames; '
      '1609486nonzero captured audio samples do not prove listening quality. Historical unrepaired control1430 '
      'and slowvariant8546failures remain in their original receipts; the slow15408variant was not rebuilt in this repair. '
      'No whole-game speedup,whole-source recompilation,authenticated physical-console boot or general IRQ fidelity '
      'is proven. Defaults and modelweights remain unpromoted. Both local diagnostic Analyst answers were rejected '
      'as complete advice; the repair was coordinator-authored from traces,not localmodelC.')
    status='terminal_formatter_GPU_wait_repair_published_with_finite_gameplay'
    current=dict(project='Black Ice White Noise,AtariJaguarCD',status=status,recorded_at=now.isoformat(),checked_answer=summary,checked_current_summary=summary,current_verified_route_summary=summary,report=str(report),experimental_build=dict(resident_bytes=14690,reserved_bytes=16384,heap_start='0x162dc0',compiled_binary=b['linked_component'],binary_sha256=sha(b['linked_component']),derived_disc=b['derived_disc'],derived_disc_sha256=b['derived_disc_sha256'],authorship='Coordinator26byte assembled restoration repair; unchanged existing compiledCprefix. Mixed originalengine/devices remain.'),experimental_wait_repair=dict(bytes=26,entry='0xe098',resident_entry=hex(wait_address),native_scripted_cases=256,source_behavior_changed=True,earlier_return_while_command_pending=early[0],HUD_write_while_GPU_busy=overlay[0],isolated_blit_full_2MB_RAM_reproduced=True,both_retained_blitter_engines_equal=True,hardware_equivalence=False),helper_gates=old['current_status'].get('helper_gates',{}),existing_C_prefix_evidence_scope='Unchanged14664bytes retain prior scoped323original formatter instruction-address coverage and19component gates; those19gates were not newly rerun on the14690byte image. New entry/heap/keypad and explicit waitfixtures plus freshgameplay cover this extension.',startup_cases=96,installed_keypad_ABI_cases=5151,fresh_repaired_Deck_pair=dict(frames_per_lane=2600,health=health,pair_finite_checks_passed=True,comparisons=pair['comparisons'],frame_equivalent=False,shared_selector_repair_bytes=38),long_adaptive_route=route,historical_unrepaired_failures=dict(control_first_odd_PC_frame=1430,slow_variant_first_odd_PC_frame=8546,slow_variant_rebuilt_with_wait_repair=False,original_receipts_preserved=True),unrepaired_artifact_failures_remain_recorded=True,new_repaired_control_failure_observed=False,whole_game_speedup_demonstrated=False,physical_console_verified=False,whole_game_complete=False,standalone_runtime_verified=False,default_promoted=False,new_training=False,goal_complete=False,native_Chat_verified=False,local_Analyst=dict(complete_answers_accepted=0,answers=2,inference_seconds=61.93299424997531,same_weights=True,independent_review=False),this_lookup_executes_game_tests=False,this_lookup_invokes_model_or_training=False,remaining=['Broader source restoration and integration of remaining game/platform behavior.','Test repaired synchronization across other scenes,IRQinterleavings and gameplay; earlier slowvariantnotretrofitted.','Verify nativeChat usability,representative localmodelquality and useful training gains.','Authenticated realconsoleboot,audiolistening and future256GBhardware remain unverified.'])
    text='BIWN: REPRODUCED GPU COMPLETION RACE AND EXPERIMENTAL REPAIR\n'+now.isoformat()+'\n\n'+summary+'\n\nACTUAL GAME TESTS\n'+json.dumps(dict(Deck=health,route=route,read_only_replay_prefix_checks=prefix),indent=2)+'\n\nLOCAL MODEL OUTPUT TEST\n'+json.dumps(proofs['native-formatter-diagnostic-Analyst-reviewed'],indent=2)+'\n\nEVIDENCE POINTERS\n'+'\n'.join(str(p)for p in pointers.values())+'\n'
    report.write_text(text);(out/'report.txt').write_text(text);deps[str(report)]=sha(report)
    publication=dict(status=status,recorded_at=now.isoformat(),directory=str(out),report=str(report),current_status=current,status_dependencies_sha256=deps,integrity_mismatches=0,read_only_replay_prefix_checks=prefix,source_behavior_repair=True,known_reproduced_control_failure_addressed_in_finite_retest=True,historical_failure_receipts_preserved=True,all_game_or_hardware_behavior_verified=False,new_training=False,default_promoted=False,goal_complete=False)
    save(out/'publication.json',publication);save(ROOT/'verification/native-formatter-GPU-wait-publication-current.json',publication)
    ledgerp=ROOT/'verification/goal-continuation-current.json';ledger=read(ledgerp);ledger.update(status='active_formatter_GPU_wait_race_reproduced_and_finite_repair_verified_goal_incomplete',recorded_at=now.isoformat(),previous_goal_turn_classification='no progress on active goal: answered verified preview sprint controls; no source,modelorworkflow mutation.',this_turn_classification='progress',current_goal_turn_classification='progress',current_goal_turn_progress='Read-onlyCPU/GPU traces isolate actual blitter overwrite and pending-mailboxcompletionrace; full2MB isolatedlaunch reproducesbothengines.26byte repair/256native fixtures/96startup/5151ABI; both2600frameDeck lanes healthy,24975frame merchant/outdoor route complete. Two localAnalyst completeanswers rejected; no training/defaultpromotion.',current_goal_turn_evidence=str(ROOT/'verification/native-formatter-GPU-wait-publication-current.json'),latest_formatter_GPU_wait_publication=str(ROOT/'verification/native-formatter-GPU-wait-publication-current.json'),latest_finite_jobs_running=False,latest_finite_job_status='All added diagnostic,build,entry,Deck,route and localAnalyst jobs terminal.',new_training=False,goal_complete=False,next_actions=current['remaining']);save(ledgerp,ledger)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(dict(recorded_at=now.isoformat(),coordinator='Four read-onlyreplays,isolatedtwoengineblitfixture,sourcewaitrepair,finitechecks andpublication',local_Diagnostic_Analyst='2actualSDKgenerations/same27Bweights/61.93seconds; completeanswersrejected,exactpromptresponsesandreviewpreserved',compiler_and_runners='Deterministic tools,notAIagents',new_training=False,native_Chat_verified=False,publication=str(ROOT/'verification/native-formatter-GPU-wait-publication-current.json')))+'\n')
    print(json.dumps(dict(status=status,evidence_files=len(deps),report=str(report),integrity_mismatches=0)),flush=True)

if __name__=='__main__':main()
