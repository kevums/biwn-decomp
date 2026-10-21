"""Compare complete fresh probes; require positive IRQ ownership when requested."""
import argparse
import hashlib
import json
from datetime import datetime,timezone
from pathlib import Path
def digest(path):
    with path.open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--frames',type=int,required=True);p.add_argument('--require-source-IRQ',action='store_true');p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    left=json.loads((a.reference/'report.json').read_text());right=json.loads((a.candidate/'report.json').read_text())
    checks={key:left[key]==right[key]for key in ['disc_sha256','requested_options','boot_strategy','frames','audio','final_RAM_sha256','final_serialized_state_sha256']}
    checks['complete_frames']=len(left['frames'])==len(right['frames'])==a.frames
    checks['no_state_seed']=not left['captured_state_input']and not right['captured_state_input']and not left['host_CPU_or_GPU_register_seed']and not right['host_CPU_or_GPU_register_seed']
    checks['same_video_layout']=all(left['video'][k]==right['video'][k]for k in ['width','height','pitch'])
    hashes={}
    for name in ['RAM-final.bin','GPU-final.bin','state-final.bin','video-final.xrgb8888','frontend-PCM.s16le']:
        hashes[name]=[digest(a.reference/name),digest(a.candidate/name)];checks[name]=hashes[name][0]==hashes[name][1]
    irq=right.get('source_CPU_IRQ_entry')
    if a.require_source_IRQ:
        checks['reference_IRQ_owner_disabled']=not left.get('source_CPU_IRQ_entry')
        checks.update(IRQ_owned_positive=bool(irq)and irq['core']['Owned']>0,no_original_IRQ_entry=bool(irq)and irq['core']['Original']==0,no_rejected_IRQ_entry=bool(irq)and irq['core']['Rejected']==0,no_source_IRQ_errors=bool(irq)and irq['source']['errors']==0,IRQ_counts_consistent=bool(irq)and irq['source']['calls']==irq['source']['owned']==irq['core']['Owned'])
    else:checks['both_owners_disabled']=not left.get('source_CPU_IRQ_entry')and not irq
    report=dict(status=('fresh_source_CPU_IRQ_'if a.require_source_IRQ else'default_NULL_IRQ_hook_inertness_')+('pass'if all(checks.values())else'fail'),recorded_at=datetime.now(timezone.utc).isoformat(),reference=str(a.reference.resolve()),candidate=str(a.candidate.resolve()),frames=a.frames,checks=checks,sha256=hashes,source_IRQ=irq,core_hashes=[left['core_sha256'],right['core_sha256']],whole_game_complete=False,scope='Fresh originalCPU/GPU/DSP execution with optional source IRQ entry after original device ACK. All recorded frame fields, audio stats and complete finalRAM/GPU/video/machine/PCM match. No per-instruction CPUstream, standalone runtime, physical hardware or audio-quality proof.')
    report['remaining_providers']=['OriginalCPU','OriginalGPU','OriginalDSP','OriginalIRQSelection','OriginalIRQAck','hostIRQCommitAndPrefetch','hostIRQCycleCharge','firmwareHLE','devices']if irq else['OriginalCPU','OriginalGPU','OriginalDSP','OriginalIRQ','firmwareHLE','devices']
    a.output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k in ['status','frames','checks','source_IRQ']}));assert all(checks.values()),checks
if __name__=='__main__':main()
