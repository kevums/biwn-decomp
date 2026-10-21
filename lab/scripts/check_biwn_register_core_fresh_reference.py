"""Compare complete old/new original-emulation startup-to-outdoor references."""
import hashlib,json,os
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def digest(path):
    with path.open('rb')as stream:return hashlib.file_digest(stream,'sha256').hexdigest()

def main():
    old=json.loads((ROOT/'verification/fresh-outdoor-route-active.json').read_text())
    new=json.loads((ROOT/'verification/fast-fresh-outdoor-route-active.json').read_text())
    assert old['children']['reference']['status']==new['children']['reference']['status']=='terminal_completed'
    left=Path(old['directory'])/'reference';right=Path(new['directory'])/'reference'
    before=json.loads((left/'report.json').read_text());after=json.loads((right/'report.json').read_text())
    checks=dict(original_processors=before['mode']==after['mode']=='reference'and before['owned_CPU_instructions']==after['owned_CPU_instructions']==0,
                no_warmup=before['warm_original_frames']==after['warm_original_frames']==0,
                no_checkpoint=before['restored_original_checkpoint']is None and after['restored_original_checkpoint']is None,
                complete=len(before['frames'])==len(after['frames'])==24738,
                same_input=before['frame_controller_script_sha256']==after['frame_controller_script_sha256'],
                same_code_repair=before['experimental_code_overlay']==after['experimental_code_overlay'],
                all_frame_CPU_RAM_video_PCM=before['frames']==after['frames'],
                no_errors=not before['errors']and not after['errors'],
                CPU_counts=before['original_CPU_instructions']==after['original_CPU_instructions']>0)
    assert all(checks.values()),checks
    out=ROOT/'verification/GPU-register-fresh-reference-check'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    report=dict(status='running_full_file_digests',pid=os.getpid(),directory=str(out),old_reference=str(left),new_reference=str(right),checks=checks,sha256={})
    def save():(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for name in ['warm-RAM.bin','CPU-before-instructions.bin','retired-instruction-costs.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','frontend-PCM.s16le']:
        assert (left/name).stat().st_size==(right/name).stat().st_size,name
        one,two=digest(left/name),digest(right/name);report['sha256'][name]=[one,two];report['checks'][name]=one==two;save();print(name,'match'if one==two else'MISMATCH',flush=True);assert one==two,name
    report.update(status='full24738frame_original_core_inertness_verified',recorded_at=datetime.now(timezone.utc).isoformat(),frames=24738,CPU_instructions=before['original_CPU_instructions'],old_core_sha256=before['core_sha256'],new_core_sha256=after['core_sha256'],reconstructed_execution_verified_by_this_check=False,default_promoted=False,whole_game_complete=False,scope='Both cores independently run all original processors from startup with no warmup/checkpoint, same ordinary inputs and18byte wordscan repair. All CPU instruction states/costs, every frame CPU/RAM/video/PCM, full final machine and complete PCM match byte-for-byte. This proves API-only-core inertness on the recorded original route; separate sourceCfull comparisons remain pending. Original IRQ/HLE/device and physical/standalone/fullgame limits remain.')
    save();(ROOT/'verification/GPU-register-fresh-reference-current.json').write_text(json.dumps(report,indent=2)+'\n');print(report['status'],flush=True)

if __name__=='__main__':main()
