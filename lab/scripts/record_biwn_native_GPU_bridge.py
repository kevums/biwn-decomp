"""Stream strict native-GPU comparisons and untouched original CPU-core frame baselines."""
import argparse,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def identical(a,b):
    digest=hashlib.sha256();size=0
    with a.open('rb')as left,b.open('rb')as right:
        while True:
            x=left.read(1024*1024);y=right.read(1024*1024)
            assert x==y,('byte mismatch',str(a),str(b),size)
            if not x:break
            digest.update(x);size+=len(x)
    return dict(bytes=size,sha256=digest.hexdigest())
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path,required=True);args=ap.parse_args();run=args.run_root
    CPU=json.loads((ROOT/'verification/frame-CPU-owner-runtime-current.json').read_text());rows={}
    for direction in ['none','U']:
        a,b=run/(direction+'-trace'),run/(direction+'-C');left=json.loads((a/'report.json').read_text());right=json.loads((b/'report.json').read_text())
        assert left['status']==right['status']=='completed_component_uncompared'and not left['errors']and not right['errors'];assert left['frames']==right['frames'];frames=len(right['frames'])
        gr=json.loads((b/'regular-GPU-bundles/report.json').read_text());assert gr['native_bridge']and gr['counts']['Original']==gr['counts']['Rejected']==0 and gr['stats']['uncovered']==gr['stats']['errors']==0
        assert right['original_CPU_instructions']==right['rejected_CPU_instructions']==0
        names=['warm-RAM.bin','CPU-before-instructions.bin','retired-instruction-costs.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','regular-GPU-bundles/before-state-hashes.bin','regular-GPU-bundles/PC-stream.bin']
        names += [str(p.relative_to(a))for p in (a/'OP-GPU-slices').glob('*.bin')];artifacts={name:identical(a/name,b/name)for name in names}
        OP=json.loads((b/'OP-GPU-slices/report.json').read_text());assert not OP['errors'] and len(OP['records'])==frames and all(x['original_opcode_delta']==0 for x in OP['records'])
        original=CPU['runs'][direction];assert original['frames']==frames,'Untouched original baseline frame count differs'
        baseline=Path(original['source_paths']['baseline']);observed=Path(original['source_paths']['reference']);whole={}
        for name in ['warm-RAM.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin']:whole[name]=identical(baseline/name,b/name)
        for name in ['CPU-before-instructions.bin','retired-instruction-costs.bin']:whole[name]=identical(observed/name,b/name)
        assert json.loads((baseline/'report.json').read_text())['frames']==right['frames']
        rows[direction]=dict(frames=frames,run_root=str(run),C_run=str(b),untouched_original_run=str(baseline),CPU_owned_instructions=right['owned_CPU_instructions'],regular_GPU_owned_bundles=gr['counts']['Owned'],C_GPU_source_instructions=gr['C_source_instructions'],OP_C_source_instructions=sum(x['C_source_instructions']for x in OP['records']),original_CPU_GPU_in_owned_window=0,all_recorded_states_costs_pixels_and_final_machine_match=True,artifacts=artifacts,untouched_original_comparison=whole,native_elapsed_seconds=gr['elapsed_seconds'],all_audio_samples_silent=right['audio']['nonzero_samples']==0)
    out=ROOT/'verification/native-GPU-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    candidate=json.loads((ROOT/'verification/fast-GPU-bridge-candidate.json').read_text());report=dict(status='native_C_CPU_GPU_matches_untouched_original_extended_frames',directory=str(out),run_root=str(run),runs=rows,bridge=candidate['library'],bridge_sha256=hashlib.sha256(Path(candidate['library']).read_bytes()).hexdigest(),original_startup_frames=600,original_DSP_IRQ_HLE_devices=True,new_training=False,coordinator_authored=True,whole_game_complete=False,native_Chat_latest_verified=False,limits=['Only tested normal-frame paths/profile after original600frame startup.','DSP/IRQ/HLE/devices retained; PCM silent; no whole-game/standalone/physical display or accuracy proof.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/native-GPU-runtime-current.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(report=str(out/'report.json'),runs={k:{x:v[x]for x in ['frames','CPU_owned_instructions','regular_GPU_owned_bundles','native_elapsed_seconds']}for k,v in rows.items()})))
if __name__=='__main__':main()
