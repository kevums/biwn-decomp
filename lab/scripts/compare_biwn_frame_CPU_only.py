"""Compare CPU-owned fresh frames with same-core original execution."""
import argparse
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--C-run',type=Path,required=True)
    parser.add_argument('--reference',type=Path,required=True)
    parser.add_argument('--expected-frames',type=int,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--original-checkpoint-report',type=Path,
                        help='Require this exact original checkpoint instead of a fresh run')
    parser.add_argument('--experimental-code-overlay',type=Path,
                        help='Require this exact byte-checked post-restore overlay on both executions')
    args=parser.parse_args()
    rebuilt,original=args.C_run.resolve(),args.reference.resolve()
    c=json.loads((rebuilt/'report.json').read_text())
    o=json.loads((original/'report.json').read_text())
    checkpoint=c['restored_original_checkpoint']
    checkpoint_checks={}
    if args.original_checkpoint_report:
        expected_path=args.original_checkpoint_report.resolve()
        expected=json.loads(expected_path.read_text())
        checkpoint_directory=Path(expected.get('directory',expected_path.parent))
        if not checkpoint_directory.is_absolute():checkpoint_directory=expected_path.parent
        checkpoint_state_hash=expected.get('state_sha256')or digest(checkpoint_directory/'final-serialized-state.bin')
        expected_RAM=bytearray((checkpoint_directory/'final-RAM.bin').read_bytes())
        if args.experimental_code_overlay:
            for patch in json.loads(args.experimental_code_overlay.read_text())['patches']:
                address=int(patch['address'],16);old=bytes.fromhex(patch['original']);new=bytes.fromhex(patch['replacement'])
                assert len(old)==len(new)>0 and expected_RAM[address:address+len(old)]==old
                expected_RAM[address:address+len(new)]=new
        expected_RAM_hash=hashlib.sha256(expected_RAM).hexdigest()
        # Both original capture receipts and full original frame-run reports
        # can identify a checkpoint. A source-owned run cannot qualify here.
        original_processors=(expected.get('original_processors_only')is True or
            (expected.get('original_CPU_instructions',0)>0 and
             expected.get('owned_CPU_instructions',0)==0 and
             expected.get('regular_GPU_report')is None and expected.get('DSP_report')is None))
        checkpoint_checks=dict(
            original_checkpoint_identity=checkpoint==o['restored_original_checkpoint']and checkpoint is not None,
            checkpoint_is_original=expected.get('mode')=='reference'and original_processors,
            checkpoint_core=expected['core_sha256']==c['core_sha256']==o['core_sha256'],
            checkpoint_file_hash=checkpoint_state_hash==digest(checkpoint_directory/'final-serialized-state.bin'))
        for phase,result in [('C',c),('reference',o)]:
            restored=result['restored_original_checkpoint']or{}
            checkpoint_checks[phase+'_expected_checkpoint']=restored.get('report')==str(expected_path)
            checkpoint_checks[phase+'_exact_restore']=restored.get('exact_machine_and_RAM_before_execution')is True
            checkpoint_checks[phase+'_checkpoint_state']=restored.get('state_sha256')==checkpoint_state_hash
            checkpoint_checks[phase+'_checkpoint_RAM']=digest((rebuilt if phase=='C'else original)/'warm-RAM.bin')==expected_RAM_hash
    else:
        checkpoint_checks['no_checkpoint']=checkpoint is None and o['restored_original_checkpoint']is None
    checks={'modes':c['mode']=='C'and o['mode']=='reference',
            **checkpoint_checks,
            'same_core':c['core_sha256']==o['core_sha256'],
            'same_warm_frames':c['warm_original_frames']==o['warm_original_frames'],
            'same_controller_script':c['frame_controller_script_sha256']==o['frame_controller_script_sha256'],
            'complete_frames':len(c['frames'])==len(o['frames'])==c['requested_frames']==o['requested_frames']==args.expected_frames,
            'all_frame_CPU_RAM_pixels_audio':c['frames']==o['frames'],
            'no_errors':not c['errors']and not o['errors'],
            'no_original_CPU':c['original_CPU_instructions']==0,
            'no_rejected_CPU':c['rejected_CPU_instructions']==0,
            'all_reference_CPU_owned':c['owned_CPU_instructions']==o['original_CPU_instructions']>0}
    overlay=c.get('experimental_code_overlay')
    checks['same_experimental_overlay']=overlay==o.get('experimental_code_overlay')
    checks['expected_experimental_overlay']=(overlay is None if not args.experimental_code_overlay else
        overlay is not None and overlay['sha256']==digest(args.experimental_code_overlay)and
        (overlay['after_exact_restore']is True if args.original_checkpoint_report else
         overlay.get('after_exact_restore')is False and isinstance(overlay.get('applied_before_frame'),int)and overlay['applied_before_frame']>0))
    hashes={}
    gpu=None
    if c.get('regular_GPU_report'):
        gpu=json.loads(Path(c['regular_GPU_report']).read_text())
        checks.update(no_original_GPU=gpu['counts']['Original']==0,
                      no_rejected_GPU=gpu['counts']['Rejected']==0,
                      no_GPU_errors=not gpu['errors'],GPU_owned_positive=gpu['counts']['Owned']>0)
    dsp=None
    if c.get('DSP_report'):
        dsp=json.loads(Path(c['DSP_report']).read_text())
        checks.update(no_original_DSP=dsp['core_counts']['Original']==0,
                      no_rejected_DSP=dsp['core_counts']['Rejected']==0,
                      no_DSP_errors=dsp['errors']==0,DSP_owned_positive=dsp['core_counts']['Owned']>0,
                      no_uncovered_DSP=dsp['uncovered']==0)
    for name in ['CPU-before-instructions.bin','retired-instruction-costs.bin','warm-RAM.bin',
                 'final-RAM.bin','final-video.bin','final-serialized-state.bin','frontend-PCM.s16le']:
        hashes[name]=[digest(rebuilt/name),digest(original/name)]
        checks[name]=hashes[name][0]==hashes[name][1]
    irq=None
    if c.get('CPU_IRQ_report'):
        irq=json.loads(Path(c['CPU_IRQ_report']).read_text())
        checks.update(source_IRQ_entry_positive=irq['core']['Owned']>0,
                      no_original_IRQ_entry=irq['core']['Original']==0,
                      no_rejected_IRQ_entry=irq['core']['Rejected']==0,
                      no_source_IRQ_errors=irq['source']['errors']==0)
    processors='CPU'+('_GPU'if gpu else'')+('_DSP'if dsp else'')+('_only'if not gpu and not dsp else'')
    providers=([]if gpu else['OriginalGPU'])+([]if dsp else['OriginalDSP'])+['OriginalIRQ','firmwareHLE','devices']
    if irq:providers.remove('OriginalIRQ');providers+=['OriginalIRQSelection','OriginalIRQAck','hostIRQCommitAndPrefetch','hostIRQCycleCharge']
    result=dict(status=processors+'_frame_comparison_'+('pass'if all(checks.values())else'fail'),
                recorded_at=datetime.now(timezone.utc).isoformat(),C_run=str(rebuilt),reference=str(original),
                original_warm_frames=c['warm_original_frames'],frames=len(c['frames']),
                owned_CPU_instructions=c['owned_CPU_instructions'],checks=checks,sha256=hashes,
                GPU_counts=gpu['counts']if gpu else None,
                DSP_counts=dsp['core_counts']if dsp else None,
                source_IRQ_entry=irq,
                whole_game_complete=False,remaining_providers=(['OriginalCheckpoint']if args.original_checkpoint_report else[])+providers,
                restored_original_checkpoint=checkpoint,
                experimental_code_overlay=overlay,
                original_checkpoint_frame=expected.get('source_frame')if args.original_checkpoint_report else None,
                scope='Declared warm frames followed by requested reconstructed CPU/GPU/DSP execution. CPU instruction states/costs, recorded frames and complete final machine/PCM are compared; GPU/DSP per-instruction state hashes are not compared. No standalone/full-game or physical hardware proof.')
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key]for key in ['status','frames','owned_CPU_instructions','checks']}))
    raise SystemExit(0 if all(checks.values()) else 1)


if __name__=='__main__':
    main()
