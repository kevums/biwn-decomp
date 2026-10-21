"""Choose a real disc tile center and verify a fresh source scene setup there."""
import json,random
from datetime import datetime,timezone
from pathlib import Path
import check_biwn_scene_queue_restoration as queue
ROOT=queue.ROOT;get=queue.scene.native.get;sha=queue.sha;save=queue.save

def main():
    out=ROOT/'verification/walkable-scene-setup'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);print(out,flush=True)
    prior=json.loads((ROOT/'verification/nearby-actor-scene-current.json').read_text());raw=(Path(prior['directory'])/'scene-0-loaded-C-RAM.bin').read_bytes();obj=0x49c4c;room=get(raw,obj+64,2);container=get(raw,0x49bb4+room*4);records=get(raw,container+8);count=get(raw,container,2);assert 0<count<128
    choices=[];ox=get(raw,obj+4)&~1023;oz=get(raw,obj+10)&~1023
    for i in range(count):
        record=records+i*20;x,z,w,h=[get(raw,record+offset,2)for offset in [10,14,16,18]]
        assert x+w<=16 and z+h<=16
        if w and h:choices.append(dict(index=i,record=hex(record),flags=get(raw,record,2),local_rect=[x,z,w,h],area=w*h,X=ox+x*64+w*32,Z=oz+z*64+h*32))
    selected=max(choices,key=lambda row:row['area']);save(out/'tile-selection.json',dict(source_scene=str(Path(prior['directory'])/'scene-0-loaded-C-RAM.bin'),source_RAM_sha256=sha(raw),room=room,container=hex(container),choices=choices,selected=selected,scope='Explicit initial player position chosen from actual source geometry. No geometry/collision/actor/camera field is patched. Natural reachability is not established.'))
    proof=json.loads((ROOT/'verification/scene-queue-restoration-current.json').read_text());library=Path(proof['directory'])/'libscene-queue-restoration.dylib';runtime=queue.Runtime(library)
    catalogue=json.loads((ROOT/'verification/outdoor-scene-catalog-current.json').read_text());snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes();assert sha(snapshot)==catalogue['resident_flag_RAM_sha256']
    prefix=runtime.disc.use_previous_track_prefix();scan=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0];a=int(scan['address'],16);old=bytes.fromhex(scan['original']);new=bytes.fromhex(scan['replacement']);initial=bytearray(snapshot);assert initial[a:a+len(old)]==old;initial[a:a+len(old)]=new;initial[0x47b80:0x47b84]=bytes(4)
    diagnosis=json.loads((ROOT/'verification/elevator-up-marker-diagnosis-current.json').read_text());buffer=(Path(diagnosis['run'])/'C/final-RAM.bin').read_bytes()[0x1c0000:0x1c8000];assert sha(buffer)==diagnosis['buffer_sha256'];witness=runtime.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],buffer)
    for a,value in queue.PATCHES.items():assert get(initial,a)==value;initial[a:a+4]=queue.QUEUE.to_bytes(4,'big')
    rng=random.Random(0x102c417e0e);incoming=lambda:[rng.getrandbits(32)for _ in queue.scene.world.REGS]
    try:
        prepared,_,_,_,_=queue.outdoor.compare(runtime,bytes(initial),dict(entry=0x1aa40,mode=1,word_scan=1,incoming=incoming(),external_D0=0xc001d00d),out,'textures')
        position=bytearray(prepared);position[obj+4:obj+8]=selected['X'].to_bytes(4,'big');position[obj+10:obj+14]=selected['Z'].to_bytes(4,'big')
        left,right,d0,original,rebuilt=queue.outdoor.compare(runtime,bytes(position),dict(mode=1,word_scan=1,incoming=incoming(),external_D0=0xc001d00d),out,'scene')
        assert original['fault']is None and not original['texture_queue_overruns']and not original['unmapped_actor_reads']
        actual=runtime.last_C_raw;assert queue.normalized(actual)==right
        bounds=dict(X_min=get(actual,obj+76),X_max=get(actual,obj+72),Z_min=get(actual,obj+84),Z_max=get(actual,obj+80))
        assert bounds['X_min']<=selected['X']<bounds['X_max']and bounds['Z_min']<=selected['Z']<bounds['Z_max'],bounds
        assert get(actual,obj+66,2)==selected['index']
        records_checked=queue.scene.check_task_records(left,right,original)
        (out/'scene-0-loaded-C-RAM.bin').write_bytes(actual);save(out/'original.json',original);save(out/'rebuilt.json',rebuilt)
    except Exception as error:save(out/'status.json',dict(status='terminal_failed',error=repr(error)));raise
    finally:runtime.close()
    report=dict(status='real_tile_center_C_scene_setup_matches_original',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),scene_RAM=str(out/'scene-0-loaded-C-RAM.bin'),scene_RAM_sha256=sha(actual),selected=selected,player_bounds=bounds,task_records_checked=records_checked,queue_proof=str(ROOT/'verification/scene-queue-restoration-current.json'),source_sha256=proof['source_sha256'],script_sha256=sha(Path(__file__).read_bytes()),disc_prefix=prefix,disc_witness=witness,scope='Fresh source1AA40/20F78 setup at the center of the largest positive-area rectangle in actual room12 disc geometry. Full publicRAM/D0/disc/device/actor/task original/C comparisons use explicitqueue/wordscan/672 adapters. Assert resulting source player tile index and bounds contain the supplied position. This establishes coherent starting collision geometry, not natural reachability, a modified collision rule or standalone/full-game proof.')
    save(out/'report.json',report);save(out/'status.json',dict(status='terminal_pass'));save(ROOT/'verification/walkable-scene-setup-current.json',report);print(json.dumps(dict(status=report['status'],directory=str(out),position=[selected['X'],selected['Z']],bounds=bounds)),flush=True)

if __name__=='__main__':main()
