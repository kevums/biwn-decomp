"""Strict material bundle acceptance; retains previous renderer proof separately."""
import argparse,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path);ap.add_argument('--control',action='store_true');ap.add_argument('--setup',action='store_true');args=ap.parse_args()
    stage='setup'if args.setup else'control'if args.control else'material'
    pointer=ROOT/('verification/'+stage+'-bundle-run-current.json');run=args.run_root or Path(json.loads(pointer.read_text())['directory'])
    a,b=run/'trace',run/'C';reports=[json.loads((p/'report.json').read_text())for p in [a,b]]
    for report in reports:
        assert report['status']=='completed_component_uncompared' and not report['errors']
        assert report['original_CPU_instructions']==0 and report['rejected_CPU_instructions']==0
    assert reports[0]['frames']==reports[1]['frames'], 'per-frame mismatch'
    names=['warm-RAM.bin','CPU-before-instructions.bin','retired-instruction-costs.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin','regular-GPU-bundles/before-state-hashes.bin','regular-GPU-bundles/PC-stream.bin']
    names.extend(str(p.relative_to(a))for p in (a/'OP-GPU-slices').rglob('*.bin'));artifacts={}
    for name in names:
        left=(a/name).read_bytes();right=(b/name).read_bytes();assert left==right,('artifact mismatch',name)
        artifacts[name]=dict(bytes=len(left),sha256=hashlib.sha256(left).hexdigest())
    gr=json.loads((b/'regular-GPU-bundles/report.json').read_text());assert gr['material_bundles_enabled']and gr['status']=='completed_uncompared'and gr['counts']['Rejected']==0
    baseline_name='control-bundle-progress.json'if args.setup else'material-bundle-progress.json'if args.control else'renderer-bundle-progress.json'
    baselines=json.loads((ROOT/'verification'/baseline_name).read_text())
    if reports[1]['direction']not in baselines and args.setup:
        baselines=json.loads((ROOT/'verification/material-bundle-progress.json').read_text())
    baseline=baselines[reports[1]['direction']]
    if args.control:assert gr['control_bundles_enabled']
    if args.setup:assert gr['setup_bundles_enabled']
    assert gr['counts']['Owned']>baseline['regular_GPU_owned_bundles'] and gr['counts']['Original']<baseline['regular_GPU_original_bundles_remaining'],'no expanded ownership'
    out=ROOT/('verification/'+stage+'-GPU-runtime')/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    libraries=[dict(name=x['name'],library=x['library'],source_sha256=x['source_sha256'],coordinator_repairs=x.get('coordinator_repairs',[]),library_sha256=hashlib.sha256(Path(x['library']).read_bytes()).hexdigest())for x in gr['material_overlays']]
    report=dict(status=stage+'_C_bundles_exact_normal_frame_comparison',directory=str(out),run_root=str(run),reference_run=str(a.resolve()),direction=reports[1]['direction'],frames=len(reports[1]['frames']),regular_GPU_owned_bundles=gr['counts']['Owned'],regular_GPU_original_bundles_remaining=gr['counts']['Original'],C_source_instructions=gr['C_source_instructions'],uncovered_instruction_variants=len(gr['uncovered_instruction_variants']),artifacts=artifacts,material_libraries=libraries,base_renderer_library=gr['renderer_library'],new_training=False,coordinator_authored_integration=True,whole_game_complete=False,
        original_CPU_in_owned_window=0,all_audio_samples_silent=reports[1]['audio']['nonzero_samples']==0,
        limits=['Original600frame startup, DSP/IRQ/HLE/device providers retained; only checked profile and paths.', 'Exact CPU states/costs, known GPU before-state stream, OP boundaries, RAM/pixels/final machine in tested window. No all-game or physical accuracy claim.', 'Consumer case bodies originated from earlier local-model output; SHLQ carry repaired by coordinator in isolated bundle candidate.'])
    report['control_libraries']=[dict(name=x['name'],library=x['library'],source_sha256=x['source_sha256'])for x in gr.get('control_overlays',[])]
    report['setup_source']=gr.get('setup_source')
    report['all_regular_GPU_owned_in_test_window']=gr['counts']['Original']==0
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/('verification/'+stage+'-GPU-runtime-current.json')).write_text(json.dumps(report,indent=2)+'\n')
    progress_path=ROOT/('verification/'+stage+'-bundle-progress.json');progress=json.loads(progress_path.read_text())if progress_path.exists()else{};progress[report['direction']]=report;progress_path.write_text(json.dumps(progress,indent=2)+'\n')
    pointer.write_text(json.dumps(dict(status='terminal_exact_comparison_pass',directory=str(run),proof=str(out/'report.json')),indent=2)+'\n');print(json.dumps(dict({k:report[k]for k in ['status','frames','regular_GPU_owned_bundles','regular_GPU_original_bundles_remaining','uncovered_instruction_variants']},report=str(out/'report.json'))))
if __name__=='__main__':main()
