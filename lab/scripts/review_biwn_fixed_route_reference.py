"""Verify an original fixed-input replay against its completed navigation."""
import argparse
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(path):
    with path.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--target',type=int,required=True);a=p.parse_args()
    jp=ROOT/f'verification/scene{a.target}-full-fixed-reference-job.json';job=json.loads(jp.read_text());out=Path(job['directory'])
    reference=json.loads((out/'report.json').read_text());navigation=json.loads((ROOT/f'verification/normal-route-{a.target}-navigation-review.json').read_text());nav=Path(navigation['directory']);prior=json.loads((nav/'report.json').read_text());n=navigation['frames']
    checks=dict(original_reference_mode=reference['mode']=='reference',no_checkpoint=reference['restored_original_checkpoint']is None,no_warmup=reference['warm_original_frames']==0,same_core=reference['core_sha256']==prior['core_sha256'],complete_frames=reference['requested_frames']==len(reference['frames'])==len(prior['frames'])==n,no_errors=not reference['errors'],no_source_CPU=reference['owned_CPU_instructions']==0,
                all_frame_CPU_PC=all(x['CPU']['pc']==int(y['CPU'],16)and x['frame']==y['frame']for x,y in zip(reference['frames'],prior['frames'])),
                all_frame_nonzero_audio=all(x['audio']['nonzero_samples']==y['cumulative_nonzero_audio_samples']for x,y in zip(reference['frames'],prior['frames'])))
    hashes={}
    for source,other in [('final-RAM.bin','RAM-final.bin'),('final-serialized-state.bin','state-final.bin'),('final-video.bin','video-final.xrgb8888'),('frontend-PCM.s16le','frontend-PCM.s16le')]:
        hashes[source]=[digest(out/source),digest(nav/other)];checks[source]=hashes[source][0]==hashes[source][1]
    result=dict(status=f'original_scene{a.target}_fixed_replay_'+('pass'if all(checks.values())else'fail'),recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),navigation=str(nav),frames=n,original_CPU_instructions=reference['original_CPU_instructions'],checks=checks,sha256=hashes,reconstructed_C_execution_verified=False,whole_game_complete=False,scope='Original fixed pad replay agrees with navigation on recorded CPU PC/nonzero audio and finalRAM/machine/video/PCM. Navigation excludes full CPU instruction state streams; this reference supplies those for the subsequent source comparison.')
    path=ROOT/f'verification/scene{a.target}-full-fixed-reference-review.json';path.write_text(json.dumps(result,indent=2)+'\n');assert all(checks.values()),checks
    job.update(status='terminal_verified_original_replay',review=str(path));jp.write_text(json.dumps(job,indent=2)+'\n');print(result['status'],n)
if __name__=='__main__':main()
