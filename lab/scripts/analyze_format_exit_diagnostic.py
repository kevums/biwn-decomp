"""Classify actual actor/media trace and retain the local Analyst's errors."""
import hashlib,json,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
import binary_tools


def read(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')


def intervals(rows,predicate):
    result=[];start=None
    for row in rows:
        if predicate(row):
            if start is None:start=row['frame']
        elif start is not None:
            result.append([start,row['frame']-1]);start=None
    if start is not None:result.append([start,rows[-1]['frame']])
    return result


def main():
    parent_path=ROOT/'verification/native-format-exit-diagnostic-current.json'
    parent=read(parent_path);assert parent['status']=='terminal_fresh_exit_diagnostic_pair_repeats_prior_routes'
    out=ROOT/'verification/native-format-exit-analysis'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True);dependencies={}
    def bind(path):
        path=Path(path).resolve();dependencies[str(path)]=sha(path)
    bind(parent_path);bind(__file__)
    for path,digest in parent['source_sha256'].items():assert sha(path)==digest,path;bind(path)
    old=read(parent['parent'])
    for lane in ['base','optimized']:
        disc=old['builds'][lane];assert sha(disc['disc'])==disc['disc_sha256'];bind(disc['disc'])
    baseline_path=ROOT/'render-assets/biwn-inventory-baseline.bin';baseline=baseline_path.read_bytes();bind(baseline_path)
    ranges=[(0x10252,0x1028e),(0x12f88,0x12fd8),(0x130fc,0x13116),(0x13122,0x131e8),(0x1c9e8,0x1ca68)]
    facts=[dict(start=hex(a),stop=hex(b),instructions=[{k:v for k,v in row.items()if k in ['address','size','bytes','assembly']}
        for row in binary_tools.m68k_instructions(baseline[a:b],a)[0]])for a,b in ranges]
    save(out/'original-instruction-facts.json',facts)
    lanes={};all_records={}
    for lane in ['base','optimized']:
        folder=Path(parent['directory'])/lane;report_path=folder/'report.json';report=read(report_path);rows=report['frames']
        records_path=folder/'gameplay-events.bin.diagnostic.jsonl';records=[json.loads(x)for x in records_path.read_text().splitlines()];all_records[lane]=records
        assert sha(report_path)==parent['results'][lane]['report_sha256']
        assert sha(records_path)==parent['results'][lane]['diagnostic_sha256']
        bind(report_path);bind(records_path);bind(folder/'gameplay-observation.json')
        for path,digest in parent['results'][lane]['snapshots_sha256'].items():assert sha(path)==digest;bind(path)
        distances=[r for r in records if r['pc']==0x12f90]
        for r in distances:
            dx=r['player'][0]-r['actor3'][1];dz=r['player'][1]-r['actor3'][2]
            assert r['registers'][0]==(dx*dx+dz*dz)&0xffffffff
        branches=[r for r in records if r['pc']==0x13122]
        calls=[r for r in records if r['pc']==0x1c9e8]
        returns=[r for r in records if r['pc']==0x131c8]
        for r in calls+returns:
            ram=Path(r['RAM']).read_bytes()
            assert len(ram)==0x200000
            for a,b in ranges:assert ram[a:b]==baseline[a:b],(hex(a),hex(b))
        stalled=intervals(rows,lambda r:r['frame']>=24100 and r['raw_player_X']==12844 and r['raw_player_Z']==42398 and r['player_mode_word']==2 and r['navigation']['buttons']==['U'])
        media=intervals(rows,lambda r:r['frame']>=24090 and r['movie_flag_words'][1]==1)
        lanes[lane]=dict(executed_frames=report['executed_frames'],prior_selected_frame_differences=parent['results'][lane]['prior_selected_frame_differences'],
                        exact_navigation_repeat=parent['results'][lane]['navigation_and_buttons_repeat_exactly'],
                        native_sampled_distance_minimum=min(r['registers'][0]for r in distances),native_distance_return_samples=len(distances),
                        native_distance_matches_actual_coordinates=True,actor_state1_distance_samples=len(branches),
                        actor_state1_distance_minimum=min(r['registers'][3]for r in branches),media_calls=calls,media_returns=returns,
                        position_hold_intervals=stalled,media_active_intervals=media,nonzero_audio_samples=report['audio']['nonzero_samples'])
    assert lanes['base']['media_calls']==[] and lanes['base']['media_returns']==[]
    assert lanes['base']['native_sampled_distance_minimum']==269>255
    optimized=lanes['optimized'];assert optimized['native_sampled_distance_minimum']==244
    assert len(optimized['media_calls'])==len(optimized['media_returns'])==1
    entry=optimized['media_calls'][0];returned=optimized['media_returns'][0]
    assert entry['frame']==24158 and entry['pc']==0x1c9e8 and entry['return_pc']==0x131c8
    assert entry['stack_word4']==10 and entry['registers'][11]==0x49fd6 and entry['registers'][3]==244
    assert entry['registers'][5]&0xffff==0 and entry['actor3'][3]==1
    assert returned['frame']==28971 and returned['registers'][0]==5
    assert optimized['position_hold_intervals']==[[24154,28970]]
    assert optimized['media_active_intervals']==[[24190,27242],[27275,28125],[28158,28970]]
    elapsed=returned['frame']-entry['frame'];assert elapsed==4813
    state_write=[r for r in all_records['optimized']if r['pc']==0x131e2]
    assert len(state_write)==1 and state_write[0]['frame']==28971
    prediction_path=ROOT/'verification/native-format-exit-local-prediction-current.json';prediction=read(prediction_path)
    assert prediction['status']=='terminal_local_prediction_pending_native_review' and not prediction['fresh_diagnostic_result_supplied']
    review=dict(status='partial_media_hypothesis_not_accepted_as_precise_source_analysis',
        broad_hypothesis='Media/NPC encounter is consistent with the fresh native call and recorded playback.',
        errors=[
            'Claimed4812frame freeze from24158; actual forward-held position run is24154..28970 inclusive4817frames; media call spans24158..28971 elapsed4813frames.',
            'Described13122as adaptive-route logic; it is original type5 actor state1 code, initially MOVE.B D2,0x6E(A3).',
            'Described131BEas return; it pushes argument10 before JSR1C9E8 at131C2.',
            'Described131C8as media-state check; it is MOVE.W D0,D1 after the call.',
            'Described131E2as a pause branch; it writes actor state5 after return.',
            'Omitted the actual signed distance comparison to255 at13126/1312C, despite the supplied assembly.',
            'Its disconfirming_observations repeat supporting observations instead of proposing disconfirmation.',
            'Described media-active state as continuous; the original recording includes inactive gaps between three sequences.'
        ],
        input_tokens=prediction['input_tokens'],seconds=prediction['seconds'],same_daily_weights=True,
        instruction_roles_were_supplied_as_assembly=True,held_out_or_independent_validation=False,
        new_training=False,weights_promoted=False)
    save(out/'local-Analyst-review.json',review)
    for path in Path(prediction['directory']).iterdir():
        if path.is_file():bind(path)
    bind(prediction_path)
    failed=ROOT/'runs/format-exit-local-analyst-20261018T164422.875027Z'
    for path in failed.iterdir():
        if path.is_file():bind(path)
    # Store this as development feedback, not a successful training/holdout.
    evaluation=ROOT/'evaluation/native-format-exit';evaluation.mkdir(parents=True,exist_ok=True)
    save(evaluation/'local-Analyst-development-failure.json',dict(prompt_file=prediction['directory']+'/prompts-and-responses.txt',review=review,
         use='Development error corpus. If later used for training, exclude this exact task from held-out evaluation.',
         new_training=False))
    report=ROOT/'reports/native-format-exit-diagnosis.txt'
    report.write_text(
        'BIWN OPTIMIZED EXIT DELAY — NATIVE TRACE DIAGNOSIS\n\n'
        'The extra route frames include an original type5 NPC interaction. They are not a clean measure of whole-game execution speed. '
        'No game-code, NPC-state, waypoint, arrival tolerance or controller-policy change was made in this diagnostic.\n\n'
        'Both fresh HLE starts repeated their prior routes exactly in every recorded playerX/Z,mode,floor,scene,video hash and cumulative audio-count frame, '
        'and all recorded navigation/button decisions. Base24975frames; optimized29791frames. The added observer only reads CPU/RAM and writes host logs/snapshots.\n\n'
        'ORIGINAL ACTOR CONTROL FLOW\n'
        'Type5 slot3 is at0x49FD6, position12832/42408. State1 dispatches through the original table to0x13122. '
        '0x10252 returns squared player-to-actor distance. At0x13126 the actor comparesD3with255; '
        '0x1312C skips this encounter when signedD3is greater. Observed distances are positive. '
        'The base actor-task samples never drop below269 in the observed approach; the optimized task reaches244. '
        'Every captured0x10252 return equals the squared distance from its actual recorded coordinates.\n\n'
        'Atframe24158, the optimized actor hasD3=244,D5.W=0(fullD5=0x40000),state1. 0x131BE pushes10; '
        '0x131C2 calls0x1C9E8, with original returnPC0x131C8 on the real task stack. '
        'That single call returns atframe28971 withD0=5, elapsed4813frames. '
        '0x131C8 copiesD0intoD1;0x131E2 writes actor state5 after return. '
        'The base trace makes no0x1C9E8 call during this observed exit. '
        'The caller/actor/media instruction ranges in the captured RAM match the original baseline bytes.\n\n'
        'The player holds position12844/42398 with forward input overframes24154..28970 inclusive4817frames. '
        'The call includes three media-active intervals:24190..27242,27275..28125,28158..28970, with short inactive gaps. '
        'That explains the additional captured audio and most of the4816frame route difference. '
        'It does not isolate the earlier timing/position divergence that caused the optimized approach to cross the encounter threshold, '
        'nor prove all movement, media timing or game behavior correct. No audibility/quality or physical-console claim.\n\n'
        'LOCAL ANALYST TEST\n'
        'One actual Qwen3_5 27B6bit Analyst generation,22424inputtokens,57.08seconds. '
        'The new diagnostic result was not supplied. It predicted a broad media/NPC interaction but omitted the distance gate, '
        'misidentified several supplied instructions and gave supporting facts as disconfirmation. '
        'Rejected as precise source analysis; no independent Reviewer or new training. '
        'An earlier preparation exceeded32K context before inference; preserved. Columnar encoding then retained all120declared approach rows per lane.\n'
        'Exact prompts/output: '+prediction['directory']+'/prompts-and-responses.txt\n\n'
        'Full decompilation/platform replacement, physical console, broad local model reliability, advertising training and future hardware remain open.\n')
    bind(report);bind(out/'original-instruction-facts.json');bind(out/'local-Analyst-review.json');bind(evaluation/'local-Analyst-development-failure.json')
    result=dict(status='terminal_original_type5_encounter_explains_long_route_delay_with_limits',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),report=str(report),
                lanes=lanes,threshold=255,comparison='signed greater skips encounter; observed positive distances',
                optimized_call_elapsed_frames=elapsed,optimized_position_hold_frames=4817,
                route_frame_difference=4816,raw_instruction_facts=str(out/'original-instruction-facts.json'),local_Analyst_review=review,
                earlier_approach_divergence_cause_isolated=False,whole_game_speedup_demonstrated=False,frame_equivalent=False,
                new_training=False,default_promoted=False,native_Chat_verified=False,whole_game_complete=False,goal_complete=False,
                dependencies_sha256=dependencies)
    save(out/'report.json',result);save(ROOT/'verification/native-format-exit-analysis-current.json',result)
    print(json.dumps({k:result[k]for k in ['status','report','threshold','optimized_call_elapsed_frames','optimized_position_hold_frames','route_frame_difference']}))


if __name__=='__main__':main()
