"""Accept extended CPU candidate only with untouched original1200frame comparison."""
import json
from pathlib import Path
from datetime import datetime,timezone
from record_biwn_native_GPU_bridge import identical
ROOT=Path(__file__).resolve().parents[1]
def main():
    pointer=ROOT/'verification/extended-CPU-1200-run-current.json';entry=json.loads(pointer.read_text());run=Path(entry['directory']);a,b=run/'reference',run/'C';original=json.loads((a/'report.json').read_text());C=json.loads((b/'report.json').read_text())
    assert original['status']==C['status']=='completed_component_uncompared'and not original['errors']and not C['errors'];assert len(original['frames'])==len(C['frames'])==1200;assert original['frames']==C['frames'],'frame checkpoint mismatch'
    artifacts={name:identical(a/name,b/name)for name in ['warm-RAM.bin','CPU-before-instructions.bin','retired-instruction-costs.bin','final-RAM.bin','final-video.bin','final-serialized-state.bin']}
    for p in (a/'OP-GPU-slices').glob('*.bin'):artifacts[str(p.relative_to(a))]=identical(p,b/p.relative_to(a))
    GPU=json.loads((b/'regular-GPU-bundles/report.json').read_text());assert GPU['counts']['Original']==GPU['counts']['Rejected']==0 and GPU['stats']['uncovered']==GPU['stats']['errors']==0;assert C['original_CPU_instructions']==C['rejected_CPU_instructions']==0
    OP=json.loads((b/'OP-GPU-slices/report.json').read_text());assert len(OP['records'])==1200 and all(x['original_opcode_delta']==0 for x in OP['records'])and not OP['errors']
    candidate=json.loads((ROOT/'verification/extended-frame-CPU-candidate.json').read_text());assert candidate['library']==C['CPU_library']
    warm=(b/'warm-RAM.bin').read_bytes();final=(b/'final-RAM.bin').read_bytes();player=lambda ram:{name:int.from_bytes(ram[p:p+4],'big',signed=True)for name,p in [('X',0x49c50),('Z',0x49c56)]}
    out=ROOT/'verification/extended-1200-frame-runtime'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=dict(status='C_CPU_GPU_1200_normal_frames_matches_untouched_original',directory=str(out),run_root=str(run),frames=1200,direction='U',original_startup_frames=600,CPU_owned_instructions=C['owned_CPU_instructions'],regular_GPU_owned_bundles=GPU['counts']['Owned'],OP_C_source_instructions=sum(x['C_source_instructions']for x in OP['records']),original_CPU_GPU_in_owned_window=0,new_CPU_cases=len(candidate['new_cases']),CPU_library=candidate['library'],CPU_candidate=str(ROOT/'verification/extended-frame-CPU-candidate.json'),player_before=player(warm),player_after=player(final),all_audio_samples_silent=C['audio']['nonzero_samples']==0,GPU_instruction_states_recorded=False,artifacts=artifacts,new_training=False,coordinator_authored=True,whole_game_complete=False,limits=['1200normalframes after original600frame startup; one input path and emulator profile.','CPUinstruction state/costs, rawOPboundaries, everyframeRAM/pixels and finalmachine exact. GPUinstruction hashes omitted in long mode; separate60fulltrace retained.','OriginalDSP/IRQ/HLE/authentication/devices retained; PCM silent; other gameplay/scenes, standalone and physicalaccuracy unfinished.'])
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'verification/extended-1200-frame-runtime-current.json').write_text(json.dumps(report,indent=2)+'\n');entry.update(status='terminal_exact_comparison_pass',proof=str(out/'report.json'));pointer.write_text(json.dumps(entry,indent=2)+'\n');print(json.dumps({k:report[k]for k in ['status','frames','CPU_owned_instructions','regular_GPU_owned_bundles','new_CPU_cases','player_before','player_after']}))
if __name__=='__main__':main()
