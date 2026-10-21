"""Single-input fast native GPU comparison; GPU trace scope explicitly reported."""
import argparse,hashlib,json
from pathlib import Path
from datetime import datetime,timezone
from record_biwn_native_GPU_bridge import identical
ROOT=Path(__file__).resolve().parents[1]
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-root',type=Path,required=True);args=ap.parse_args();run=args.run_root;a,b=run/'trace',run/'C'
    left=json.loads((a/'report.json').read_text());right=json.loads((b/'report.json').read_text());assert left['status']==right['status']=='completed_component_uncompared'and not left['errors']and not right['errors'];assert left['frames']==right['frames']
    GPU=json.loads((b/'regular-GPU-bundles/report.json').read_text());assert GPU['native_bridge']and GPU['counts']['Original']==GPU['counts']['Rejected']==0 and GPU['stats']['uncovered']==GPU['stats']['errors']==0;assert right['original_CPU_instructions']==right['rejected_CPU_instructions']==0
    names=['warm-RAM.bin','CPU-before-instructions.bin','retired-instruction-costs.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin'];names += [str(p.relative_to(a))for p in (a/'OP-GPU-slices').glob('*.bin')]
    if GPU['full_instruction_trace']:names += ['regular-GPU-bundles/before-state-hashes.bin','regular-GPU-bundles/PC-stream.bin']
    artifacts={name:identical(a/name,b/name)for name in names};OP=json.loads((b/'OP-GPU-slices/report.json').read_text());assert len(OP['records'])==len(right['frames'])and not OP['errors']and all(x['original_opcode_delta']==0 for x in OP['records'])
    out=ROOT/'verification/fast-GPU-frame-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=dict(status='native_fast_frame_CPU_GPU_comparison_pass',directory=str(out),run_root=str(run),direction=right['direction'],frames=len(right['frames']),regular_GPU_owned_bundles=GPU['counts']['Owned'],regular_GPU_original_bundles_remaining=0,original_CPU_in_owned_window=0,OP_original_GPU_in_owned_window=0,all_regular_GPU_owned_in_test_window=True,GPU_instruction_states_recorded=GPU['full_instruction_trace'],native_elapsed_seconds=GPU['elapsed_seconds'],artifacts=artifacts,bridge=GPU['library'],bridge_sha256=hashlib.sha256(Path(GPU['library']).read_bytes()).hexdigest(),all_audio_samples_silent=right['audio']['nonzero_samples']==0,new_training=False,whole_game_complete=False,coordinator_authored=True,limits=['Original600frame startup, DSP/IRQ/HLE/devices retained.','CPUinstruction states/costs, OPrawboundaries, per-frameRAM/pixels and finalserializedmachine compared; GPUinstruction hashes only when GPU_instruction_states_recorded=true.','Same tested emulator profile/paths; no fullgame, standalone, physicalaccuracy or newtraining claim.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/fast-GPU-frame-runtime-current.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(dict(report=str(out/'report.json'),frames=report['frames'],GPU_instruction_states_recorded=report['GPU_instruction_states_recorded'],native_elapsed_seconds=report['native_elapsed_seconds'])))
if __name__=='__main__':main()
