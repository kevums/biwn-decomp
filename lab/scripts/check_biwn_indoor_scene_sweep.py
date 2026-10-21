"""All tagged indoor records through readable scene setup with native oracle."""
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import check_biwn_scene_stream as scene

ROOT=scene.ROOT
save=scene.save
sha=scene.sha


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--indices');args=parser.parse_args()
    catalogue=json.loads((ROOT/'verification/indoor-scene-catalog-current.json').read_text());records=json.loads((Path(catalogue['directory'])/'records.json').read_text())
    indices=[int(i)for i in args.indices.split(',')]if args.indices else list(range(800))
    assert indices and len(set(indices))==len(indices)and all(0<=i<800 for i in indices)
    out=ROOT/'verification/indoor-scene-sweep'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    restore=ROOT/'projects/black-ice-white-noise/restoration';library=out/'libindoor-sweep.dylib'
    command=['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',*[str(restore/name)for name in scene.SOURCES],'-o',str(library)]
    compiled=subprocess.run(command,capture_output=True,text=True,env={**os.environ,'DEVELOPER_DIR':'/Library/Developer/CommandLineTools'});(out/'compiler.log').write_text(compiled.stdout+compiled.stderr);assert compiled.returncode==0,compiled.stderr
    runtime=scene.Runtime(library);snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes()
    assert sha(snapshot)==catalogue['resident_classification_RAM_sha256']
    diagnosis=json.loads((ROOT/'verification/elevator-up-marker-diagnosis-current.json').read_text());captured=(Path(diagnosis['run'])/'C/final-RAM.bin').read_bytes()[0x1c0000:0x1c8000]
    assert sha(captured)==diagnosis['buffer_sha256'];witness=runtime.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],captured)
    patch=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0]
    address=int(patch['address'],16);before=bytes.fromhex(patch['original']);after=bytes.fromhex(patch['replacement']);assert snapshot[address:address+len(before)]==before
    rng=random.Random(0x6000631f);rows=[]
    try:
        for index in indices:
            ram=bytearray(snapshot);ram[address:address+len(before)]=after;ram[0x47b80:0x47b84]=bytes(4);ram[0x49c64:0x49c66]=index.to_bytes(2,'big')
            for i in range(36):ram[0x15b4a0+i*4:0x15b4a4+i*4]=b'\xff\xff\0\0'
            case=dict(mode=2,index=index,word_scan=1,incoming=[rng.getrandbits(32)for _ in scene.world.REGS],external_D0=0xc001d00d)
            save(out/'status.json',dict(status='running',pid=os.getpid(),completed_cases=len(rows),requested_cases=len(indices),index=index))
            left,expected,original=runtime.native(bytes(ram),case);original_mail=[runtime.core.GPUReadLong(a,0)for a in[0xf03200,0xf03204,0xf0320c,0xf03210,0xf03214]]
            right,value,rebuilt=runtime.translated(bytes(ram),case);C_mail=[runtime.core.GPUReadLong(a,0)for a in[0xf03200,0xf03204,0xf0320c,0xf03210,0xf03214]]
            same=scene.native.masked(left)==scene.native.masked(right)and value==expected and rebuilt['status']==0 and not rebuilt['errors']and all(original[k]==rebuilt[k]for k in['calls','disc_requests','disc_completions','disc_stops','hardware'])and original_mail==C_mail
            if not same:
                save(out/'mismatch.json',dict(index=index,original_D0=expected,C_D0=value,original=original,C=rebuilt,original_mailboxes=original_mail,C_mailboxes=C_mail,RAM_differences=[hex(i)for i,(a,b)in enumerate(zip(scene.native.masked(left),scene.native.masked(right)))if a!=b][:40]));raise AssertionError(str(out/'mismatch.json'))
            stats=rebuilt['device'];assert not stats['device_error']and not stats['original_GPUExec1_calls']and not stats['original_GPU_sprite_decodes']and not stats['game_frames_executed']
            expected_decodes=sum(actor['source_factory_path']=='static_decode'for actor in records[index]['actors'])
            assert stats['C_sprite_decodes']==original['device']['original_GPU_sprite_decodes']==len(original['decoded_sprites'])==expected_decodes
            sprites=[]
            for sprite in original['decoded_sprites']:
                dest=sprite['destination'];size=sprite['width']*sprite['height']*2;assert size>0 and left[dest-16:dest+size]==right[dest-16:dest+size]
                sprites.append(dict(**sprite,pixel_bytes=size,pixel_sha256=sha(right[dest:dest+size]),header_sha256=sha(right[dest-16:dest])))
            # The original cache only considers slots below36-group. Report
            # unresolved groups rather than treating CPU-equivalent loading as
            # proof that every scene's textures are available for rendering.
            cached={scene.native.get(right,0x15b4a0+i*4,2)for i in range(36)}
            unresolved=[id for id in records[index]['texture_ids']if id not in cached]
            rows.append(dict(index=index,case=case,full_D0=value,body_sha256=records[index]['body_sha256'],actor_count=records[index]['actor_count'],source_actor_paths=dict(Counter(a['source_factory_path']for a in records[index]['actors'])),original=original,rebuilt=rebuilt,created_task_records_checked=scene.check_task_records(left,right,original),decoded_sprite_payloads_checked=sprites,unresolved_texture_group_ids=unresolved,full_public_RAM_and_checked_mailboxes_match=True))
            with(out/'cases.jsonl').open('a')as f:f.write(json.dumps(rows[-1])+'\n')
    except Exception as error:
        save(out/'status.json',dict(status='terminal_failed',completed_cases=len(rows),requested_cases=len(indices),index=index,error=repr(error),native_diagnostic=getattr(runtime,'failure',None)));raise
    finally:runtime.close()
    report=dict(status='indoor_scene_sweep_native_CPU_GPU_vs_readable_C_match'if not args.indices else'indoor_scene_sweep_selected_preflight_pass',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),cases=len(rows),indices=indices,distinct_bodies=len({row['body_sha256']for row in rows}),records_with_actors=sum(bool(row['actor_count'])for row in rows),actor_placements=sum(row['actor_count']for row in rows),C_sprite_decodes=sum(row['rebuilt']['device']['C_sprite_decodes']for row in rows),original_GPU_sprite_decodes=sum(row['original']['device']['original_GPU_sprite_decodes']for row in rows),original_GPU_instructions=sum(row['original']['device']['original_GPUExec1_calls']for row in rows),created_task_records_checked=sum(len(row['created_task_records_checked'])for row in rows),unresolved_texture_groups_by_scene={str(row['index']):row['unresolved_texture_group_ids']for row in rows if row['unresolved_texture_group_ids']},catalogue=str(ROOT/'verification/indoor-scene-catalog-current.json'),source_sha256={n:sha((restore/n).read_bytes())for n in scene.SOURCES+[n.replace('.c','.h')for n in scene.SOURCES]},script_sha256=sha(Path(__file__).read_bytes()),native_helper_sha256=sha((ROOT/'scripts/check_biwn_scene_stream.py').read_bytes()),device_bridge_sha256=sha((ROOT/'tools/libbiwn-inventory-device.dylib').read_bytes()),native_core_sha256=sha((ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib').read_bytes()),normalized_disc_sha256=runtime.disc.manifest['normalized_track_sha256'],captured_stream_witness=witness,new_training=False,default_promoted=False,native_Chat_verified=False,scope='Each selected realtagged indoorrecord is loaded from actual normalizeddisc using source20F78/loader/copy/texture/cache/fixups/playerposition/actorfactory/taskcreation. Static objects issue originalE2B8protocol; originalCPU plus originalGPU4B00decoder oracle compares with readableC plus checkedCdecoder, zerooriginalCPU/GPUfallback onCpath. FullD0/public2MBRAM/externalcalls/disctransfers/7blitterregs/5GPUmailboxes, explicit newtaskrecords/neighbors anddecoded spriteheaders/pixels compare. Sourcewordscan repair andfixed672phase selected explicitly, notoriginalprogram success. Frozen merchant RAM/TOC/heap/flag/assets, cold texturecache andsceneindexarefixtures. SynchronousBIOS/DF60completion andGPUmailboxack areadapters; taskexecution,realcontextswitches,interrupts,fullCPU/GPUABI/cycles,physicaltiming,naturalentryforallscenes,renderedworlds andfullgame remain unproved. Unresolvedtexturegroups reportoriginalcachelimits; equivalence doesnotmakeallscenesrenderable.800tags contain duplicatedbodies, not800distinct completedlevels.')
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass',cases=len(rows)))
    save(ROOT/'verification'/('indoor-scene-sweep-preflight-current.json'if args.indices else'indoor-scene-sweep-current.json'),report)
    print(json.dumps({key:report[key]for key in['status','cases','C_sprite_decodes','created_task_records_checked','directory']}),flush=True)


if __name__=='__main__':main()
