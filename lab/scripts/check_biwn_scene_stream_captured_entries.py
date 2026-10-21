"""Replay readable scene setup from actual20F78entry captures.

The live observer intentionally stops before loader/context services. This
checks exact natural entry states with synchronous disc adapters and source
task creation, not the unobserved natural return or interrupt/context lifecycle.
"""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import struct
import check_biwn_scene_stream as scene

ROOT=scene.ROOT
sha=scene.sha
save=scene.save


def masked(data,stack):
    result=bytearray(data);result[stack-0x1000:stack+32]=bytes(0x1000+32)
    return bytes(result)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt',type=Path,required=True)
    parser.add_argument('--replay',type=Path,required=True)
    args=parser.parse_args()
    receipt=json.loads(args.receipt.read_text());assert receipt['routine']=='scene_setup'
    assert sha((Path(receipt['directory'])/'fast_CPU_bridge.c').read_bytes())==receipt['source_sha256']
    replay=json.loads((args.replay/'comparison.json').read_text());assert all(replay['checks'].values())
    bridge=json.loads((args.replay/'C/native-CPU-bridge-report.json').read_text());assert bridge['library']==receipt['library']
    proof=json.loads((ROOT/'verification/scene-stream-current.json').read_text());restore=ROOT/'projects/black-ice-white-noise/restoration'
    for name,digest in proof['source_sha256'].items():assert sha((restore/name).read_bytes())==digest,name
    runtime=scene.Runtime(Path(proof['directory'])/'libscene-stream.dylib')
    diagnosis=json.loads((ROOT/'verification/elevator-up-marker-diagnosis-current.json').read_text())
    buf=(Path(diagnosis['run'])/'C/final-RAM.bin').read_bytes()[0x1c0000:0x1c8000];assert sha(buf)==diagnosis['buffer_sha256']
    witness=runtime.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],buf)
    overlay=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0]
    address=int(overlay['address'],16);replacement=bytes.fromhex(overlay['replacement'])
    out=ROOT/'verification/scene-stream-captured-entry'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    captures=Path(receipt['captures']);rows=[]
    try:
        for path in sorted(captures.glob('*-result.json')):
            prefix=path.name[:3];capture_result=json.loads(path.read_text())
            cpu_path=captures/(prefix+'-before-CPU.bin');ram_path=captures/(prefix+'-before-RAM.bin')
            cpu=struct.unpack('>19IH',cpu_path.read_bytes());ram=ram_path.read_bytes();assert len(ram)==0x200000 and cpu[16]==0x20f78
            assert ram[address:address+len(replacement)]==replacement
            stack=cpu[15];scene.SP=stack
            get=scene.native.get;mode=get(ram,stack+4,2);assert mode==2
            case=dict(entry=0x20f78,mode=mode,word_scan=1,incoming=list(cpu[:15]),external_D0=0xc001d00d)
            original,d0,left=runtime.native(ram,case);rebuilt,value,right=runtime.translated(ram,case)
            match=masked(original,stack)==masked(rebuilt,stack)and value==d0 and right['status']==0 and not right['errors']and all(left[k]==right[k]for k in ['calls','disc_requests','disc_completions','disc_stops','hardware'])
            if not match:
                save(out/(prefix+'-mismatch.json'),dict(original=left,C=right,original_D0=d0,C_D0=value,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(masked(original,stack),masked(rebuilt,stack)))if a!=b][:40]));raise AssertionError('captured entry replay mismatch')
            assert get(rebuilt,0x49c60,2)==2 and get(rebuilt,0x47b80,2)==0
            rows.append(dict(capture=prefix,original_entry_CPU=str(cpu_path),original_entry_CPU_sha256=sha(cpu_path.read_bytes()),original_entry_RAM=str(ram_path),original_entry_RAM_sha256=sha(ram),live_capture_result=capture_result,natural_return_observed=bool(capture_result['complete']),entry_floor=get(ram,0x49c62,2),scene_index=get(ram,0x49c64,2),entry_SR=hex(cpu[19]),entry_SP=hex(stack),full_D0=value,original=left,rebuilt=right,created_task_records_checked=scene.check_task_records(original,rebuilt,left),full_public_RAM_matches=True,final_public_RAM_sha256=sha(masked(rebuilt,stack))))
            save(out/'cases.json',rows)
    except Exception as error:
        save(out/'status.json',dict(status='terminal_failed',error=repr(error),native_diagnostic=getattr(runtime,'failure',None)));raise
    finally:runtime.close()
    assert len(rows)==2 and {row['scene_index']for row in rows}=={314,315}
    report=dict(status='readable_scene_stream_exact_natural_entries_matches_native_with_explicit_IO_adapters',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),results=rows,capture_receipt=str(args.receipt.resolve()),capture_source_sha256=receipt['source_sha256'],original_frame_replay=str(args.replay.resolve()),original_frame_comparison_passed=True,original_frame_replay_frames=replay['frames'],entry_world_heap_cache_edits=False,entry_registers_edits='Native unit harness seeds supplied data registers and exact entrySP; supervisor mode/CCR are controlled for isolated execution, not original CPU ABI.',original_native_CPU_in_unit=True,readable_C_original_CPU_fallback=False,explicit_synchronous_disc_adapters=True,task_execution_in_this_call=False,natural_scene_return_verified=False,natural_scheduler_and_interrupts_verified=False,elevator_stream_witness=witness,source_sha256=proof['source_sha256'],verifier_sha256=sha(Path(__file__).read_bytes()),new_training=False,default_promoted=False,scope='Exact20F78entry RAM anddata registers/SP captured during ordinary-input480frame floor2to3to2route withisolatedwordscan repair. Observer stops before1B044loader; both wholecall captures are incomplete andretained. No world/heap/cache/pendinglist/input/actor/clock edits in isolated replay. Originalnative andreadableC use same672captured stream phase,actualdiscbytes,BIOS303C/3042/DF60synchronous completion adapters; DF6C task creation is computed from actual linked lists with source C. FullD0/public2MBRAM/externalcalls/disc events/7blitterregisters match in isolated replay. Exact initial code/RAM is captured, but private stack/SR/CCR/cycles/interrupts/context switches and actual naturalreturn are not established. This does not substitute highlevelC into the frame runtime.')
    report['task_creation_results_supplied']=False
    report['created_task_records_checked']=sum(len(row['created_task_records_checked'])for row in rows)
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)));save(ROOT/'verification/scene-stream-captured-entry-current.json',report)
    print(json.dumps({k:report[k]for k in ['status','cases','natural_scene_return_verified','directory']}),flush=True)


if __name__=='__main__':main()
