"""Classify fresh original/native route recordings without assuming success."""
import argparse
from datetime import datetime,timezone
import json,hashlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
FIELDS=['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word','tile_word','equipped_word','movie_flag_words','raw_word_49c5c','video_sha256']

def sha(path):
    with Path(path).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def comparison(left,right):
    assert len(left)==len(right)
    result={}
    for field in FIELDS:
        different=[(a,b)for a,b in zip(left,right)if a[field]!=b[field]]
        result[field]=dict(different_frames=len(different),first_difference=(dict(frame=different[0][0]['frame'],reference=different[0][0][field],candidate=different[0][1][field])if different else None))
    samples=[(a,b)for a,b in zip(left,right)if'active_actor_snapshot'in a]
    assert all('active_actor_snapshot'in b for _,b in samples)
    result['actor_samples']=dict(samples=len(samples),different_samples=sum(a['active_actor_snapshot']!=b['active_actor_snapshot']for a,b in samples))
    return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--proof',type=Path,required=True);args=p.parse_args()
    d=json.loads(args.proof.read_text());out=Path(d['directory']);assert d['status'].startswith('terminal_fresh')
    paths={lane:out/lane/'report.json'for lane in ['reference','candidate']}
    reports={lane:json.loads(path.read_text())for lane,path in paths.items()};frames={lane:r['frames']for lane,r in reports.items()}
    assert all(len(rows)==d['frames']for rows in frames.values())
    result=dict(status='terminal_fresh_route_differences_classified',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),source_proof=str(args.proof),source_proof_sha256=sha(args.proof),frames=d['frames'],comparison=comparison(frames['reference'],frames['candidate']),final_fields={lane:{k:rows[-1][k]for k in FIELDS if k!='video_sha256'}for lane,rows in frames.items()},
        scene_transitions={},audio={lane:report['audio']for lane,report in reports.items()},host_guest_RAM_writes=0,checkpoint_restores=0,whole_game_complete=False,source_sha256={str(path):sha(path)for path in [Path(__file__),*paths.values()]},
        scope='Fresh same-core original/partial-native CDI loads and identical pad windows, unmodified marker scan. Frame-field/video equality and sampled actors are separate observations, not whole-state/hardware equivalence.18E92boundary is coordinate editor, not normal movement. Raw49C5C is fractionalY, not yaw. No route completion is inferred from old route labels.')
    for lane,rows in frames.items():
        changes=[];previous=None
        for row in rows:
            current=[row[k]for k in ['player_mode_word','floor_word','scene_word']]
            if current!=previous:changes.append(dict(frame=row['frame'],mode=current[0],floor=current[1],scene=current[2]));previous=current
        result['scene_transitions'][lane]=changes
    prior_path=ROOT/'verification/native-gameplay-route-current.json'
    if args.proof.resolve()!=prior_path.resolve():
        prior=json.loads(prior_path.read_text());ref_path=Path(prior['directory'])/'reference/report.json'
        ref=json.loads(ref_path.read_text())['frames']
        assert d['frames']==prior['frames']
        result['reference_reproducibility']=dict(prior_proof=str(prior_path),prior_proof_sha256=sha(prior_path),prior_reference_sha256=sha(ref_path),comparison=comparison(ref,frames['reference']))
        save(ROOT/'verification/native-controller-fixed-analysis-current.json',result)
    else:save(ROOT/'verification/native-gameplay-analysis-current.json',result)
    save(out/'route-analysis.json',result)
    print(json.dumps({k:result[k]for k in ['status','comparison','final_fields','scene_transitions']},indent=2))

if __name__=='__main__':main()
