"""Accept normal-frame renderer substitution only after exact reference comparison."""
import argparse,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path);args=ap.parse_args()
    pointer=ROOT/'verification/renderer-bundle-run-current.json'
    run=args.run_root or Path(json.loads(pointer.read_text())['directory'])
    a,b=run/'trace',run/'C'
    reports=[json.loads((p/'report.json').read_text())for p in [a,b]]
    for report in reports:
        assert report['status']=='completed_component_uncompared' and not report['errors']
        assert report['original_CPU_instructions']==0 and report['rejected_CPU_instructions']==0
    assert reports[0]['frames']==reports[1]['frames']
    artifacts={}
    names=['warm-RAM.bin','CPU-before-instructions.bin','retired-instruction-costs.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','regular-GPU-bundles/before-state-hashes.bin']
    names.extend(str(p.relative_to(a))for p in (a/'OP-GPU-slices').rglob('*.bin'))
    for name in names:
        left=(a/name).read_bytes();right=(b/name).read_bytes()
        assert left==right,('artifact mismatch',name)
        artifacts[name]=dict(bytes=len(left),sha256=hashlib.sha256(left).hexdigest())
    gr=json.loads((b/'regular-GPU-bundles/report.json').read_text())
    assert gr['renderer_enabled'] and gr['status']=='completed_uncompared' and gr['counts']['Rejected']==0
    previous=json.loads((ROOT/'verification/regular-GPU-resident-runtime-current.json').read_text())
    assert gr['counts']['Owned']>previous['regular_GPU_owned_bundles'],'no expanded ownership'
    out=ROOT/'verification/regular-GPU-renderer-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=dict(direction=reports[1]['direction'],status='renderer_bundles_exact_normal_frame_comparison',directory=str(out),run_root=str(run),frames=len(reports[1]['frames']),
                regular_GPU_owned_bundles=gr['counts']['Owned'],regular_GPU_original_bundles_remaining=gr['counts']['Original'],
                C_source_instructions=gr['C_source_instructions'],uncovered_instruction_variants=len(gr['uncovered_instruction_variants']),artifacts=artifacts,
                library=gr['renderer_library'],overlay_libraries=[dict(name=x['name'],library=x['library'],source_sha256=x['source_sha256'])for x in gr.get('renderer_overlays',[])],new_training=False,coordinator_authored=True,whole_game_complete=False,
                limits=['Original600frame startup and DSP/IRQ/HLE/device providers retained.',
                        'Exact results in this tested window; not all paths, physical timing, natural audio or standalone game.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (ROOT/'verification/regular-GPU-renderer-runtime-current.json').write_text(json.dumps(report,indent=2)+'\n')
    pointer.write_text(json.dumps(dict(status='terminal_pass',directory=str(run),proof=str(out/'report.json')),indent=2)+'\n')
    progress_path=ROOT/'verification/renderer-bundle-progress.json'
    progress=json.loads(progress_path.read_text())if progress_path.exists()else{}
    progress[report['direction']]=report
    progress_path.write_text(json.dumps(progress,indent=2)+'\n')
    print(json.dumps(dict({k:report[k]for k in ['status','frames','regular_GPU_owned_bundles','regular_GPU_original_bundles_remaining','uncovered_instruction_variants']},report=str(out/'report.json'))))
if __name__=='__main__':main()
