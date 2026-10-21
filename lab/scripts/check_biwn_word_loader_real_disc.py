"""Readable word-scan loader vs patched native CPU using actual scene bytes."""
import ctypes as c
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import check_biwn_resources_native as native

ROOT=native.ROOT
save=native.save
sha=lambda value:hashlib.sha256(value).hexdigest()


def main():
    out=ROOT/'verification/word-loader-real-disc'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    restore=ROOT/'projects/black-ice-white-noise/restoration'
    names=['biwn_resources.c','biwn_memory.c','biwn_transition_cleanup.c','biwn_cd_math.c']
    library=out/'libword-loader.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror']+[str(restore/name)for name in names]+['-o',str(library)]
    compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    runtime=native.Runtime(library);original=runtime.resources[0x1b044]
    word=runtime.lib.biwn_resource_load_word_scan;word.argtypes=original.argtypes;word.restype=original.restype
    snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes()
    patch=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0]
    address=int(patch['address'],16);before=bytes.fromhex(patch['original']);replacement=bytes.fromhex(patch['replacement']);assert snapshot[address:address+len(before)]==before
    diagnosis_path=ROOT/'verification/elevator-up-marker-diagnosis-current.json'
    diagnosis=json.loads(diagnosis_path.read_text())
    capture_path=Path(diagnosis['run'])/'C/final-RAM.bin'
    captured=capture_path.read_bytes()[0x1c0000:0x1c8000]
    assert sha(captured)==diagnosis['buffer_sha256']
    marker=(0x613b).to_bytes(4,'big')*16
    assert runtime.disc.data.find(marker)==runtime.disc.data.rfind(marker)==diagnosis['normalized_disc_marker_offset']
    assert diagnosis['normalized_disc_stream_offset']+captured.find(marker)==diagnosis['normalized_disc_marker_offset']
    historical_phase=runtime.disc.stream_phase
    witness=runtime.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],captured)
    elevator_phase=runtime.disc.stream_phase
    witness.update(capture=str(capture_path),capture_RAM_sha256=sha(capture_path.read_bytes()),diagnosis=str(diagnosis_path))
    rng=random.Random(0x1b0ee);rows=[];coverage=set()
    vectors=[(phase,variant,index,copy)for phase,variants in [(historical_phase,['original','word_scan']),(elevator_phase,['word_scan'])]for variant in variants for index in [314,315]for copy in [False,True]]
    try:
        for phase,variant,index,copy in vectors:
            runtime.disc.stream_phase=phase
            case=dict(entry=0x1b044,id=index,incoming=[rng.getrandbits(32)for _ in native.world.REGS],params=[index*0x1260+0x591c90,index+0x6000,0x190000 if copy else 0,0x1260,0x190004 if copy else 0])
            ram=bytearray(snapshot);ram[0x47b80:0x47b84]=bytes(4);ram[0x190000:0x190004]=(0x180000).to_bytes(4,'big');ram[0x190004:0x190006]=bytes(2)
            if variant=='word_scan':ram[address:address+len(before)]=replacement
            runtime.resources[0x1b044]=word if variant=='word_scan'else original
            left,expected,reference=runtime.native(bytes(ram),case,coverage)
            right,value,rebuilt=runtime.translated(bytes(ram),case)
            matches=native.masked(left)==native.masked(right)and value==expected and all(reference[key]==rebuilt[key]for key in ['calls','disc_requests','disc_completions','disc_stops','hardware'])
            if not matches:
                save(out/'mismatch.json',dict(stream_phase=phase,variant=variant,index=index,copy=copy,expected_D0=expected,C_D0=value,original=reference,C=rebuilt,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(native.masked(left),native.masked(right)))if a!=b][:30]));raise AssertionError(str(out/'mismatch.json'))
            request=rebuilt['disc_requests'][-1];stream=runtime.disc.data[request['normalized_track_offset']:request['normalized_track_offset']+request['bytes']]
            marker=(index+0x6000).to_bytes(4,'big')*16;found=stream.find(marker);assert found>=0
            source=0x1c0000+found+64;payload=stream[found+64:found+64+0x1260]
            assert len(payload)==0x1260 and right[0x1c0000:0x1c0000+request['bytes']]==stream
            if copy:
                assert value==0 and right[0x180000:0x181260]==payload and native.get(right,0x190004,2)==1 and native.get(right,0x47b80,2)==0
            else:assert value==source and native.get(right,0x47b80,2)==1
            rows.append(dict(stream_phase=phase,variant=variant,index=index,copy=copy,full_D0=value,marker_stream_offset=hex(found),marker_alignment_mod4=found%4,payload_bytes=len(payload),payload_sha256=sha(payload),original=reference,rebuilt=rebuilt))
            save(out/'cases.json',rows)
        # Preserve the original entry's bounded non-completion on the observed
        # two-byte phase. This is a host guard, not an original returned value.
        runtime.disc.stream_phase=elevator_phase
        runtime.resources[0x1b044]=original;ram=bytearray(snapshot);ram[0x47b80:0x47b84]=bytes(4)
        case=dict(entry=0x1b044,id=315,incoming=[0]*len(native.world.REGS),params=[315*0x1260+0x591c90,0x613b,0,0x1260,0],work_budget=20000,allow_host_error=True)
        _,value,bounded=runtime.translated(bytes(ram),case)
        save(out/'bounded-original.json',dict(stream_phase=elevator_phase,full_D0=value,rebuilt=bounded))
        assert bounded['status']==4 and value==0xa55aa55a and len(bounded['disc_requests'])>=2
        unresolved=dict(status='original_loader_bounded_retry_no_completion_claim',stream_phase=elevator_phase,host_status=bounded['status'],output_untouched=True,disc_requests=len(bounded['disc_requests']),source='Actual scene315tag613B at2mod4; original full-game360frame retry is recorded separately.',whole_game_diagnosis=str(diagnosis_path))
    except Exception as error:
        save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.close()
    report=dict(status='readable_word_loader_actual_scene_payloads_match_patched_native',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),original_behavior_regression_cases=sum(row['variant']=='original'for row in rows),word_variant_cases=sum(row['variant']=='word_scan'for row in rows),scene_indices=[314,315],payload_bytes_per_load=4704,stream_phases=[historical_phase,elevator_phase],elevator_stream_witness=witness,observed_marker_alignments=sorted({row['marker_alignment_mod4']for row in rows}),original_unaligned_behavior=unresolved,source_sha256={name:sha((restore/name).read_bytes())for name in names+['biwn_resources.h']},test_script_sha256=sha(Path(__file__).read_bytes()),runtime_helper_sha256=sha((ROOT/'scripts/check_biwn_resources_native.py').read_bytes()),backend_sha256=sha((ROOT/'scripts/biwn_disc_backend.py').read_bytes()),native_core_sha256=sha((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes()),source_disc_sha256=runtime.disc.manifest['normalized_track_sha256'],experimental_word_scan_selected_explicitly=True,default_promoted=False,new_training=False,scope='FullD0,public2MBRAM,game call arguments/order,actual normalized-disc transfer/completion events and checked blitter registers match native CPU. Patched native wordscan uses same18byteoverlay as verified floor transition. Original native/C pass at historical674phase; wordvariant passes both674and672phase, including exact full-game32768byte stream witness. Two actual scene payloads tested both direct pointer and copied destination/completion. Frozen original RAM/TOC; phases are explicit replay conditions, not a general BIOS mapping. BIOS303C/3042 and DF60 completion ticks are adapters. No context switching,physicalCD timing,fullCPUABI or newscene20F78integration. Original315retry at672remains bounded non-completion, not a successful return.')
    save(out/'report.json',report);save(ROOT/'verification/word-loader-real-disc-current.json',report)
    save(out/'status.json',dict(status='terminal_pass',cases=len(rows)))
    print(json.dumps({key:report[key]for key in ['status','cases','original_behavior_regression_cases','word_variant_cases','observed_marker_alignments','directory']}),flush=True)


if __name__=='__main__':main()
