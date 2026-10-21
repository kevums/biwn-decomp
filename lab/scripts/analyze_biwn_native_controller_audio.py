"""Classify fresh merchant route outcomes and captured PCM, without listening claims."""
from datetime import datetime,timezone
import json
from pathlib import Path
import numpy as np
from run_biwn_native_gameplay_route import ROOT,save,sha


def main():
    p=ROOT/'verification/native-controller-lean-adaptive-merchant-current.json';d=json.loads(p.read_text());out=Path(d['directory']);assert d['status']=='terminal_native_controller_lean_adaptive_merchant_pair_classified'
    reports={lane:json.loads((out/lane/'report.json').read_text())for lane in ['reference','candidate']}
    result=dict(status='terminal_fresh_merchant_audio_observations_classified',recorded_at=datetime.now(timezone.utc).isoformat(),source_proof=str(p),source_proof_sha256=sha(p),directory=str(out),lanes={},whole_game_complete=False,listening_test=False,physical_console=False,
        source_sha256={str(Path(__file__)):sha(__file__)},scope='Two fresh partial-native/original CDI paths under retained emulator and identical feedback pad policy; input timings differ. Captured frontend signed16stereoPCM only; no listening, physical-console, standalone-game or newly rewritten DSP claim. Leading-silence-normalized common prefix is narrower than identical total stream/timing.')
    arrays={};first={}
    for lane,report in reports.items():
        assert not report['captured_state_input'] and not report['host_CPU_or_GPU_register_seed']
        obs=d['results'][lane]['observation'];assert not(obs['errors']or obs['copy_errors'])
        pcm=out/lane/'frontend-PCM.s16le';samples=np.memmap(pcm,mode='r',dtype='<i2');arrays[lane]=samples
        indices=np.flatnonzero(samples);first[lane]=int(indices[0])if len(indices)else None
        rows=report['frames'];first_audio=next((x for x in rows if x['cumulative_nonzero_audio_samples']),None)
        result['lanes'][lane]=dict(report_sha256=sha(out/lane/'report.json'),PCM_sha256=sha(pcm),PCM_bytes=pcm.stat().st_size,PCM_int16_samples=len(samples),nonzero_int16_samples=len(indices),first_nonzero_int16_sample=first[lane],minimum_sample=int(samples.min()),maximum_sample=int(samples.max()),first_audio_frame=first_audio['frame']if first_audio else None,first_audio_scene=first_audio['scene_word']if first_audio else None,first_audio_movie_flags=first_audio['movie_flag_words']if first_audio else None,scene_change_frame=report['scene_change_frame'],executed_frames=report['executed_frames'],final_player_fields={k:rows[-1][k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']})
        assert len(indices)==report['audio']['nonzero_samples']
    result['both_nonzero_audio']=all(v['nonzero_int16_samples']>0 for v in result['lanes'].values())
    result['total_PCM_equal']=result['lanes']['reference']['PCM_sha256']==result['lanes']['candidate']['PCM_sha256']
    result['final_player_fields_equal']=result['lanes']['reference']['final_player_fields']==result['lanes']['candidate']['final_player_fields']
    if all(v is not None for v in first.values()):
        left=arrays['reference'][first['reference']:];right=arrays['candidate'][first['candidate']:];common=min(len(left),len(right));different=np.flatnonzero(left[:common]!=right[:common])
        result['leading_silence_normalized_common_prefix']=dict(compared_int16_samples=common,different_int16_samples=len(different),first_difference=int(different[0])if len(different)else None,equal=len(different)==0,does_not_prove_total_stream_or_timing_equality=True)
    save(out/'audio-analysis.json',result);save(ROOT/'verification/native-controller-audio-current.json',result)
    print(json.dumps({k:v for k,v in result.items()if k not in ['source_sha256']},indent=2))


if __name__=='__main__':main()
