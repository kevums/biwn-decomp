"""Build isolated current-IRQ probe/comparator with explicit source checkpoints.

Existing pinned preview recipes and historical probes are not changed.
Original checkpoint checks remain intact; source restore has its own option,
verified provenance, report key and comparator checks.
"""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import py_compile
import shutil

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    out = ROOT / 'verification/source-checkpoint-probe-build' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    frozen_module = out / 'biwn_verified_source_checkpoint.py'
    shutil.copy2(ROOT / 'scripts/biwn_verified_source_checkpoint.py', frozen_module)
    prelude = 'import sys\nsys.path.insert(0,' + repr(str(ROOT / 'scripts')) + ')\nsys.path.insert(0,' + repr(str(out)) + ')\n'
    parent = ROOT / 'scripts/probe_biwn_frame_CPU_IRQ_selection.py'
    text = parent.read_text()

    def replace(old, new):
        nonlocal text
        assert text.count(old) == 1, old
        text = text.replace(old, new)

    replace('from biwn_m68k_cycle_cost import Cost', 'from biwn_m68k_cycle_cost import Cost\nfrom biwn_verified_source_checkpoint import verify_source_checkpoint')
    replace("    parser.add_argument('--experimental-code-overlay'", "    parser.add_argument('--restore-source-report',type=Path,help='Explicit checkpoint from a verified source-owned run')\n    parser.add_argument('--source-checkpoint-proof',type=Path,help='Full cold-source comparison verdict for source restore')\n    parser.add_argument('--experimental-code-overlay'")
    replace('    args = parser.parse_args()', "    args = parser.parse_args()\n    assert not(args.restore_original_report and args.restore_source_report)\n    assert bool(args.restore_source_report)==bool(args.source_checkpoint_proof)\n    checkpoint_path=args.restore_original_report or args.restore_source_report")
    replace('max_frames = 30000 if args.frame_controller_script else', 'max_frames = 30000 if (args.frame_controller_script or args.navigation_plan) else')
    replace("assert not args.experimental_code_overlay or args.restore_original_report,", "assert not args.experimental_code_overlay or checkpoint_path,")
    replace('(args.warm_frames==0 and not args.restore_original_report)', '(args.warm_frames==0 and not checkpoint_path)')
    replace('        if args.restore_original_report:', '        if checkpoint_path:')
    replace("            previous=json.loads(args.restore_original_report.read_text())\n            assert previous['mode']=='reference' and (previous.get('original_CPU_instructions',0)>0 or\n                previous.get('original_fresh_probe_checkpoint')and previous.get('original_processors_only'))", "            previous=json.loads(checkpoint_path.read_text())\n            source_provenance=verify_source_checkpoint(checkpoint_path,args.source_checkpoint_proof,core_path)if args.restore_source_report else None\n            if args.restore_original_report:\n                assert previous['mode']=='reference' and (previous.get('original_CPU_instructions',0)>0 or\n                    previous.get('original_fresh_probe_checkpoint')and previous.get('original_processors_only'))")
    replace('source_directory=args.restore_original_report.resolve().parent', 'source_directory=checkpoint_path.resolve().parent')
    replace("restored_checkpoint=dict(report=str(args.restore_original_report),state_sha256=sha(blob),\n                exact_machine_and_RAM_before_execution=True,scope='Captured original continuation; fresh firmware boot/full route not re-proved by this probe')", "restored_checkpoint=dict(report=str(checkpoint_path.resolve()),state_sha256=sha(blob),\n                exact_machine_and_RAM_before_execution=True,scope='Captured original continuation; fresh firmware boot/full route not re-proved by this probe')\n            if source_provenance:restored_checkpoint.update(source_provenance)")
    replace('restored_original_checkpoint=restored_checkpoint,', 'restored_original_checkpoint=restored_checkpoint if args.restore_original_report else None,\n                    restored_source_checkpoint=restored_checkpoint if args.restore_source_report else None,')
    replace('Original warm startup or explicit original checkpoint; requested processor ownership window only.', 'Declared original warmup or explicit original/source checkpoint; see origin/provenance; requested processor ownership window only.')
    replace("ROOT = Path(__file__).resolve().parents[1]", 'ROOT = Path(' + repr(str(ROOT)) + ')')
    text = prelude + text
    probe = out / 'source_checkpoint_probe.py'
    probe.write_text(text)
    py_compile.compile(str(probe), doraise=True)

    parent_compare = ROOT / 'scripts/compare_biwn_frame_CPU_only.py'
    text = parent_compare.read_text()
    text = text.replace('restored_original_checkpoint', 'restored_source_checkpoint')
    text = text.replace('original_checkpoint_report', 'source_checkpoint_report')
    text = text.replace('--original-checkpoint-report', '--source-checkpoint-report')
    text = text.replace('OriginalCheckpoint', 'VerifiedSourceCheckpoint')
    text = text.replace('original_checkpoint_identity', 'source_checkpoint_identity')
    text = text.replace('checkpoint_is_original', 'checkpoint_is_verified_source')
    replace("    parser.add_argument('--experimental-code-overlay'", "    parser.add_argument('--source-checkpoint-proof',type=Path,required=True)\n    parser.add_argument('--experimental-code-overlay'")
    replace('    args=parser.parse_args()', '    args=parser.parse_args()\n    assert args.source_checkpoint_report\n    provenance=verify_source_checkpoint(args.source_checkpoint_report,args.source_checkpoint_proof,Path(json.loads((args.C_run/"report.json").read_text())["core"]))')
    replace("            checkpoint_is_verified_source=expected.get('mode')=='reference'and original_processors,", "            checkpoint_is_verified_source=expected.get('mode')=='C'and checkpoint is not None and checkpoint.get('origin')=='verified_source_execution'and checkpoint.get('source_proof_sha256')==provenance['source_proof_sha256'],")
    replace('import hashlib', 'import hashlib\nfrom biwn_verified_source_checkpoint import verify_source_checkpoint')
    old = """        # Both original capture receipts and full original frame-run reports
        # can identify a checkpoint. A source-owned run cannot qualify here.
        original_processors=(expected.get('original_processors_only')is True or
            (expected.get('original_CPU_instructions',0)>0 and
             expected.get('owned_CPU_instructions',0)==0 and
             expected.get('regular_GPU_report')is None and expected.get('DSP_report')is None))
"""
    replace(old, '        # Source origin is established by the pinned full-route proof above.\n')
    replace("                      no_source_IRQ_errors=irq['source']['errors']==0)", "                      no_source_IRQ_errors=irq['source']['errors']==0,\n                      source_IRQ_selection_positive=irq['selection']['Owned']>0,\n                      no_original_IRQ_selection=irq['selection']['Original']==0,\n                      no_rejected_IRQ_selection=irq['selection']['Rejected']==0)")
    replace("providers+=['OriginalIRQSelection','OriginalIRQAck','hostIRQCommitAndPrefetch','hostIRQCycleCharge']", "providers+=['OriginalIRQQueueAndDeviceLine','OriginalIRQAck','hostIRQCommitAndPrefetch','hostIRQCycleCharge']")
    text = prelude + text
    comparator = out / 'compare_source_checkpoint.py'
    comparator.write_text(text)
    py_compile.compile(str(comparator), doraise=True)
    report = dict(status='isolated_source_checkpoint_probe_compiles_unverified', directory=str(out),
                  recorded_at=datetime.now(timezone.utc).isoformat(), probe=str(probe), comparator=str(comparator),
                  source_checkpoint_module=str(frozen_module),
                  parent_probe=str(parent), parent_probe_sha256=sha(parent),
                  parent_comparator=str(parent_compare), parent_comparator_sha256=sha(parent_compare),
                  artifacts_sha256={str(p): sha(p) for p in [probe, comparator, frozen_module]},
                  scope='Original and source checkpoint paths stay distinct. Source acceptance requires complete existing cold-route verdict, exact same core, source-mode ownership, original-matched state/RAM/video/PCM hashes and inherited18byte repair disclosure. Compilation alone is not a runtime or comparison pass.')
    (out / 'build.json').write_text(json.dumps(report, indent=2) + '\n')
    (ROOT / 'verification/source-checkpoint-probe-candidate.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, flush=True)


if __name__ == '__main__':
    main()
