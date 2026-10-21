"""Review the fresh repaired-disc Deck result and preserved-disc/source proofs."""
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as common
ROOT=common.ROOT;V=ROOT/'verification';read=common.read;save=common.save;sha=common.sha
def main():
    out=V/'native-Deck-asset-repair-review'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    pointer=V/'native-Deck-asset-repair-gameplay-current.json';run=read(pointer);assert run['status']=='terminal_native_Deck_asset_repair_gameplay_pending_review'
    build_path=Path(run['build_proof']);build=read(build_path);assert sha(build_path)==run['build_proof_sha256']
    assert sha(build['derived_disc'])==build['derived_disc_sha256']and sha(build['derived_stage'])==build['derived_stage_sha256']
    for p,digest in run['source_sha256'].items():assert sha(p)==digest
    report_path=Path(run['report_path']);report=read(report_path);assert sha(report_path)==run['report_sha256'];o=read(run['observations_path'])
    assert not report['captured_state_input']and not report['host_CPU_or_GPU_register_seed']
    assert o['deck_entries']==o['deck_native_entries']==o['deck_native_returns']==140
    assert o['deck_source_steps']==o['deck_invalid_entries']==0
    assert o['mb_entries']==o['mb_native']==o['mb_returns']and min(o['mb_entries'])>0
    errors={k:v for k,v in o.items()if any(x in k for x in ['error','pending','outside'])and isinstance(v,(int,float))}
    assert errors and all(x==0 for x in errors.values()),errors
    assert o['acquire_entries']==o['acquire_returns']and o['acquire_pending']==0
    assert report['frames'][-1]['scene_word']==312 and report['frames'][-1]['player_mode_word']==1 and report['frames'][-1]['movie_flag_words']==[0,0]
    assert len(report['frames'])==25024 and run['trial_start']==24624
    old_pointer=V/'native-Deck-ordinary-input-current.json';old=read(old_pointer);old_report_path=Path(old['directory'])/'candidate/report.json';old_report=read(old_report_path)
    ignored={'full_RAM_sha256','stage_sha256'}
    for a,b in zip(report['frames'][:24624],old_report['frames'][:24624]):
        assert {k:v for k,v in a.items()if k not in ignored}=={k:v for k,v in b.items()if k not in ignored},a['frame']
    parent=read(build['parent_build']);component=Path(parent['component']).read_bytes();ram_path=Path(run['directory'])/'candidate/RAM-final.bin';ram=ram_path.read_bytes();base=parent['resident_address']
    for lo,hi in [(base,parent['arena_address']),(parent['arena_end'],parent['deck_arena_address'])]:assert ram[lo:hi]==component[lo-base:hi-base]
    used=[]
    for i in range(101):
        a=parent['deck_arena_address']+i*1024
        assert ram[a:a+16]==component[a-base:a-base+16]and ram[a+1008:a+1024]==component[a-base+1008:a-base+1024]
        if ram[a:a+1024]!=component[a-base:a-base+1024]:used.append(i)
    assert used
    matrix_path=V/'frame-acquire-selector13-qualified-current.json';matrix=read(matrix_path);assert matrix['status']=='terminal_original_CPU_source_selector13_all_disc_groups_match'and matrix['cases']==18
    source_path=V/'native-Deck-selector13-source-current.json';source=read(source_path);assert source['status']=='terminal_source_assembled_38byte_Deck_repair_matches_installed_stage'
    transfer_path=V/'native-Deck-transfer-probe-current.json';transfer=read(transfer_path);assert transfer['status']=='terminal_retained_transfer_continuation_observed';assert transfer['final']['arm_count']-transfer['initial']['arm_count']==4
    bound=[Path(__file__),pointer,build_path,report_path,Path(run['observations_path']),ram_path,Path(run['directory'])/'candidate/state-final.bin',Path(run['directory'])/'candidate/original-emulator-final-frame.png',old_pointer,old_report_path,matrix_path,source_path,transfer_path]
    for item in [build,matrix,source,transfer]:
        for path,digest in item.get('source_sha256',{}).items():assert sha(path)==digest;bound.append(Path(path))
    bound.extend(Path(p)for p in run['source_sha256']);bound.append(Path(matrix['reviewed_report']))
    state=dict(status='terminal_fresh_repaired_native_Deck_ordinary_enter_render_exit_reviewed',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),build=str(build_path),build_sha256=sha(build_path),disc=build['derived_disc'],disc_sha256=build['derived_disc_sha256'],frames=25024,ordinary_trial_frames=400,ordinary_native_coordinate_entries=140,ordinary_native_coordinate_returns=140,original_coordinate_body_steps=0,invalid_native_identities=0,native_GPU_roots_reached=8,native_GPU_root_returns=o['mb_returns'],all_observed_errors_pending_and_stack_outside_zero=True,resource_acquisitions_returned=o['acquire_returns'],Deck_arena_used_slots=used,all101_Deck_guards_pass=True,immutable_native_code_unchanged=True,pre_input_CPU_GPU_video_navigation_frames_equal=24624,pre_input_full_RAM_and_stage_hashes_excluded_for_static_repairs=True,source13_disc_matrix_cases=18,source13_cold_loads=9,source13_cached_reuses=9,source_assembled_repair_bytes=38,actual_disc_changed_bytes=37,native_code_bytes=44430,restoration_changes_original_behavior=True,unmodified_original_Deck_activation_verified=False,default_preview_promoted=False,whole_game_complete=False,physical_console_verified=False,new_training=False,source_sha256={str(p):sha(p)for p in set(bound)},scope='Fresh ordinary HLE/emulator boot of separate repaired native CDI; existing adaptive outdoors route then keypad1/B+C/0, no state restore or CPU/task/RAM/GPU injection. Explicit two-site selector13 restoration changes original16-frame behavior. Actual140nativecoordinatecalls and974GPU4720calls; returns/ownership/ABI/taskstack/arenaguards monitored. Entire pre-input CPU/GPU/DSP/video/navigation/other recorded fields equal unrepaired candidate except declared staticRAM/stagehashes. No original-game-unchanged, arbitraryIRQ/reentrancy/timing, audio/audibility,physicalconsole orfullgame source-rebuild claim.')
    save(out/'report.json',state);save(V/'native-Deck-asset-repair-reviewed-current.json',state);print(state['status'],used,flush=True)
if __name__=='__main__':main()
