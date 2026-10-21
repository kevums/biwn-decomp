"""Classify native RNG cold-boot evidence without hiding actor differences."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parents[1]


def read(path):return json.loads(Path(path).read_text())
def sha(path):
    with Path(path).open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')


def ranges(values):
    result=[]
    for value in values:
        if result and value==result[-1][1]+1:result[-1][1]=value
        else:result.append([value,value])
    return result


def compare(reference,candidate):
    assert len(reference)==len(candidate)==24000
    fields=['raw_player_X','raw_player_Z','scene_word','player_mode_word','tile_word',
            'equipped_word','movie_flag_words','movie_controller_state_word']
    video=[];tracked=[];actors=[];actor_samples=0;different_fields={key:0 for key in fields}
    for a,b in zip(reference,candidate):
        assert a['frame']==b['frame']
        frame=a['frame']
        if a['video_sha256']!=b['video_sha256']:video.append(frame)
        if any(a[key]!=b[key]for key in fields):tracked.append(frame)
        for key in fields:different_fields[key]+=a[key]!=b[key]
        if 'active_actor_snapshot'in a or'active_actor_snapshot'in b:
            assert 'active_actor_snapshot'in a and'active_actor_snapshot'in b
            actor_samples+=1
            if a['active_actor_snapshot']!=b['active_actor_snapshot']:actors.append(frame)
    return dict(video_different_frames=len(video),video_difference_ranges=ranges(video),
                tracked_player_scene_different_frames=len(tracked),tracked_difference_ranges=ranges(tracked),
                tracked_fields=fields,per_tracked_field_differences=different_fields,
                actor_samples_compared=actor_samples,actor_sample_differences=len(actors),actor_difference_sample_frames=actors,
                actor_scope='Active nonzero-type records sampled from the probe’s first40actor slots every60frames (400samples); not a per-frame whole-world state comparison.')


def actor_snapshot(ram):
    result=[]
    for slot in range(40):
        a=0x49d6c+slot*206
        if not any(ram[a:a+2]):continue
        result.append(dict(slot=slot,type=int.from_bytes(ram[a:a+2],'big'),
            X=int.from_bytes(ram[a+4:a+8],'big',signed=True),Z=int.from_bytes(ram[a+10:a+14],'big',signed=True),
            state=int.from_bytes(ram[a+108:a+110],'big'),region=int.from_bytes(ram[a+42:a+44],'big')))
    return result


def main():
    proof=ROOT/'verification/native-rng-disc-cold-boot-current.json';state=read(proof)
    assert state['status']=='terminal_fresh_native_rng_disc_observed'
    out=Path(state['directory']);build=read(state['build_proof'])
    for path,digest in state['runtime_dependencies_sha256'].items():assert sha(path)==digest,path
    reports={lane:read(out/lane/'report.json')for lane in ['reference','candidate']}
    analysis=compare(reports['reference']['frames'],reports['candidate']['frames'])
    assert analysis['video_different_frames']==112 and analysis['tracked_player_scene_different_frames']==0
    rams={lane:(out/lane/'RAM-final.bin').read_bytes()for lane in reports}
    analysis['final_rng_selector_equal']=rams['reference'][0x113080:0x113082]==rams['candidate'][0x113080:0x113082]
    analysis['final_rng_state_table_equal']=rams['reference'][0x113082:0x113482]==rams['candidate'][0x113082:0x113482]
    analysis['final_rng_state_table_sha256']={lane:hashlib.sha256(ram[0x113082:0x113482]).hexdigest()for lane,ram in rams.items()}
    analysis['final_sampled_actors']={lane:actor_snapshot(ram)for lane,ram in rams.items()}
    analysis['final_sampled_actors_equal']=analysis['final_sampled_actors']['reference']==analysis['final_sampled_actors']['candidate']
    analysis['audio_nonzero_samples']={lane:report['frames'][-1]['cumulative_nonzero_audio_samples']for lane,report in reports.items()}
    previous=read(ROOT/'verification/native-optimized-disc-cold-boot-current.json');old=Path(previous['directory'])
    old_reports={lane:read(old/lane/'report.json')for lane in ['reference','candidate']}
    old_analysis=compare(old_reports['reference']['frames'],old_reports['candidate']['frames'])
    comparison_fields=['video_sha256',*analysis['tracked_fields'],'active_actor_snapshot']
    analysis['fresh_original_matches_prior_reference_all_sampled_fields']=all(
        all(a.get(key)==b.get(key)for key in comparison_fields)for a,b in zip(reports['reference']['frames'],old_reports['reference']['frames']))
    analysis['prior_four_entry_profile']=dict(proof=str(ROOT/'verification/native-optimized-disc-cold-boot-current.json'),
        video_different_frames=old_analysis['video_different_frames'],
        tracked_player_scene_different_frames=old_analysis['tracked_player_scene_different_frames'],
        actor_samples_compared=old_analysis['actor_samples_compared'],actor_sample_differences=old_analysis['actor_sample_differences'],
        same_original_reference_verified=analysis['fresh_original_matches_prior_reference_all_sampled_fields'])
    save(out/'comparison-analysis.json',analysis)
    state.update(status='terminal_native_rng_fresh_boot_classified_with_remaining_actor_video_differences',
        classified_at=datetime.now(timezone.utc).isoformat(),comparison_analysis=analysis,
        native_rng_entry_events=state['observations']['candidate']['rng_entries'],
        original_rng_body_instructions_on_candidate=state['observations']['candidate']['rng_old_body_steps'],
        compiled_C_math_entry_events=state['observations']['candidate']['compiled_math_entries'],
        native_rebuilt_entry_contracts=12,rng_entry_contracts_component_checked=8,
        unchanged_whole_game_source_rebuild=False,strict_whole_run_equivalence=False,
        zero_divisor_RNG_behavior_verified=False,
        interpretation='Eight new C RNG contracts pass component CPU/RAM/access tests. In this fresh game run only reached public RNG init and indexed entries are observed; C-internal seed/select/fill calls bypass original entry addresses. All eight tracked player/scene fields match each frame, but sampled actors and video still differ. Improved counts do not prove exact cause or complete game equivalence.',
        classification_artifacts_sha256={str(path):sha(path)for path in [Path(__file__),out/'comparison-analysis.json',*[(out/lane/name)for lane in reports for name in ['report.json','native-observation.json','RAM-final.bin','video-final.xrgb8888','frontend-PCM.s16le']]]})
    save(proof,state);save(out/'protocol.json',state);save(ROOT/'verification/native-rng-disc-cold-boot-active.json',state)
    print(json.dumps({key:analysis[key]for key in ['video_different_frames','tracked_player_scene_different_frames','actor_samples_compared','actor_sample_differences','final_rng_state_table_equal','final_sampled_actors_equal','prior_four_entry_profile']},indent=2))


if __name__=='__main__':main()
