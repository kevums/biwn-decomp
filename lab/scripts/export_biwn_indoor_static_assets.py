"""Export C-decoded static assets whose raw bytes match the native sweep."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys
import check_biwn_scene_stream as scene

ROOT=scene.ROOT
sys.path.insert(0,str(ROOT))
import animation_renderer


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--scene',type=int,default=4);args=parser.parse_args()
    proof_path=ROOT/'verification/indoor-scene-sweep-current.json';proof=json.loads(proof_path.read_text());assert proof['cases']==800
    restore=ROOT/'projects/black-ice-white-noise/restoration'
    for name,digest in proof['source_sha256'].items():assert scene.sha((restore/name).read_bytes())==digest,name
    selected=None
    for line in(Path(proof['directory'])/'cases.jsonl').read_text().splitlines():
        row=json.loads(line)
        if row['index']==args.scene:selected=row;break
    assert selected and selected['decoded_sprite_payloads_checked'],'No setup-decoded static assets in this record'
    snapshot=(ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin').read_bytes();ram=bytearray(snapshot)
    patch=json.loads((ROOT/'verification/elevator-word-scan-overlay.json').read_text())['patches'][0];address=int(patch['address'],16)
    assert ram[address:address+len(bytes.fromhex(patch['original']))]==bytes.fromhex(patch['original'])
    ram[address:address+len(bytes.fromhex(patch['replacement']))]=bytes.fromhex(patch['replacement']);ram[0x47b80:0x47b84]=bytes(4);ram[0x49c64:0x49c66]=args.scene.to_bytes(2,'big')
    for i in range(36):ram[0x15b4a0+i*4:0x15b4a4+i*4]=b'\xff\xff\0\0'
    runtime=scene.Runtime(Path(proof['directory'])/'libindoor-sweep.dylib')
    diagnosis=json.loads((ROOT/'verification/elevator-up-marker-diagnosis-current.json').read_text());buffer=(Path(diagnosis['run'])/'C/final-RAM.bin').read_bytes()[0x1c0000:0x1c8000]
    runtime.disc.use_captured_stream(diagnosis['normalized_disc_stream_offset'],buffer)
    try:
        output,d0,result=runtime.translated(bytes(ram),selected['case'])
        assert result['status']==0 and not result['errors']and d0==selected['full_D0']
        assert not result['device']['original_GPUExec1_calls']and not result['device']['original_GPU_sprite_decodes']and not result['device']['game_frames_executed']
        assert result['device']['C_sprite_decodes']==len(selected['decoded_sprite_payloads_checked'])
    finally:runtime.close()
    out=ROOT/'runs/indoor-static-assets'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    rows=[]
    for i,sprite in enumerate(selected['decoded_sprite_payloads_checked'],1):
        a=sprite['destination'];raw=output[a:a+sprite['pixel_bytes']];header=output[a-16:a]
        assert scene.sha(raw)==sprite['pixel_sha256']and scene.sha(header)==sprite['header_sha256']
        stem='scene-'+str(args.scene)+'-object-'+str(i);image=out/(stem+'.png');raw_path=out/(stem+'.raw16be')
        raw_path.write_bytes(raw);image.write_bytes(animation_renderer.image_png(raw,sprite['width'],sprite['height'],scale=6))
        rows.append(dict(position=i,source_frame_index=sprite['index'],source_frame_address=hex(sprite['frame']),width=sprite['width'],height=sprite['height'],raw_path=str(raw_path),raw_sha256=scene.sha(raw),image_path=str(image),png_sha256=scene.sha(image.read_bytes()),header_hex=header.hex(),native_sweep_raw_hash_matches=True))
    report=dict(status='static_assets_exported_by_C_match_native_sweep_raw_pixels',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),scene_index=args.scene,assets=rows,source_sweep=str(proof_path),source_sweep_directory=proof['directory'],C_device_statistics=result['device'],new_training=False,native_Chat_verified=False,scope='Fresh readable Cscene setup from the same suppliedmerchant RAM/coldcache/index/wordscan672conditions as the800case sweep. Each raw assetheader/pixelhash matches its recorded originalCPU/GPU oracle. NumericCRY16palette conversion withpinned emulator tables,6xnearestneighbor; zero words shownblack. Notworldrendering,physicaldisplay calibration,allassets orplayablegame.')
    scene.save(out/'report.json',report);scene.save(ROOT/'verification/indoor-static-assets-current.json',report)
    print(json.dumps(dict(status=report['status'],assets=len(rows),directory=str(out),first_image=rows[0]['image_path'])),flush=True)


if __name__=='__main__':main()
