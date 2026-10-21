"""Catalogue nine-segment outdoor blocks and bounded25-cell loading windows."""
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
import re
from biwn_disc_backend import Disc,ROOT
from catalog_biwn_indoor_scenes import sha,save


def main():
    disc=Disc();ram_path=ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin';ram=ram_path.read_bytes();rows=[]
    for match in re.finditer(rb'(\x00\x00[\x20-\x3f][\x00-\xff])\1{15}',disc.data):
        tag=int.from_bytes(match[1],'big');index=tag-0x2000;body=disc.data[match.end():match.end()+4640];assert len(body)==4640
        get=lambda a,w=2:int.from_bytes(body[a:a+w],'big');offsets=[get(i*2)for i in range(10)]
        assert match.start()==0x930+index*4704+674
        segments=[]
        for j in range(9):
            start,end=offsets[j:j+2];assert 20<=start<=end<=4640
            length=end-start
            if length==0:segments.append(dict(position=j,start=start,end=end,bytes=0,layout_status='zero_length_boundary_segment'));continue
            assert 18<=length<=532
            raw_header=[get(start+i*2)for i in range(4)];relative=[int.from_bytes(body[start+8+i*2:start+10+i*2],'big',signed=True)for i in range(4)]
            assert all(16<=offset<=length for offset in relative)
            texture_words=raw_header[3];assert texture_words%3==0
            texture_start=start+relative[3];actor_start=texture_start+texture_words*2;actor_count=get(actor_start);actor_start+=2
            assert actor_start+actor_count*14<=end
            actors=[]
            for k in range(actor_count):
                a=actor_start+k*14;id=get(a);flags=ram[0x4208c+id]
                kind='dynamic_task'if flags&1 else'static_sprite'if flags&2 else'static_decode'
                actors.append(dict(actor_id=id,raw_X=get(a+2,4),raw_Y=get(a+6),raw_Z=get(a+8,4),heading=get(a+12),resident_flags=flags,source_factory_path=kind))
            segments.append(dict(position=j,start=start,end=end,bytes=length,layout_status='bounded_segment',raw_header_words=raw_header,relative_offsets=relative,texture_ids=[get(texture_start+i*2+4)for i in range(0,texture_words,3)],actor_count=actor_count,actors=actors,body_sha256=sha(body[start:end])))
        rows.append(dict(index=index,tag=hex(tag),normalized_marker_offset=match.start(),offsets=offsets,body_sha256=sha(body),segments=segments))
    assert [row['index']for row in rows]==list(range(611))
    windows=[];excluded=[]
    for row in range(4,47):
        for column in range(13):
            for remainder in range(5):
                indices=[(row-k)*13+column for k in range(5)]
                missing=[[index,j]for index in indices for j in range(remainder,remainder+5)if rows[index]['segments'][j]['layout_status']!='bounded_segment']
                target=dict(top_row=row,column=column,remainder=remainder,record_indices=indices,
                    X=((column*5+remainder+2)<<10)+511,Z=0xbc01-((row-2)<<10)-256)
                if missing:excluded.append(dict(**target,zero_length_segments=missing))
                else:windows.append(target)
    out=ROOT/'verification/outdoor-scene-catalog'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'records.json',rows);save(out/'windows.json',windows);save(out/'excluded-windows.json',excluded)
    actors=[a for row in rows for segment in row['segments']for a in segment.get('actors',[])]
    report=dict(status='outdoor_record_layouts_and_loading_window_bounds_catalogued',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),records=len(rows),segments=sum(len(r['segments'])for r in rows),zero_length_boundary_segments=sum(s['bytes']==0 for r in rows for s in r['segments']),bounded_segments=sum(s['bytes']>0 for r in rows for s in r['segments']),distinct_block_bodies=len({r['body_sha256']for r in rows}),bounded_loading_windows=len(windows),windows_containing_zero_length_segments=len(excluded),actor_placements_in_stored_segments=len(actors),actor_factory_classification=dict(Counter(a['source_factory_path']for a in actors)),resident_flag_RAM=str(ram_path),resident_flag_RAM_sha256=sha(ram),normalized_disc_sha256=disc.manifest['normalized_track_sha256'],script_sha256=sha(Path(__file__).read_bytes()),game_execution=False,new_training=False,scope='Static original disc layout:611unique2000..2262tagged blocks,10offsetwords defining9segments each. Each bounded segment has source16byteheader, relative tables, texture triplets and14byteactor records.20F78loads5rows and5segments perrow using horizontal remainder0..4. Bounds catalogue retains zero-length edge segments and excludes their windows from the bounded set; this is not a claim that excluded windows execute safely or are reachable in gameplay. Coordinates are supplied test positions derived from the original formula, not discovered traversable routes. Stored segment counts include duplicated/overlapping data. No rendering, scheduling or complete-game proof.')
    save(out/'report.json',report);save(ROOT/'verification/outdoor-scene-catalog-current.json',report)
    print(json.dumps({k:report[k]for k in ['status','records','bounded_segments','zero_length_boundary_segments','bounded_loading_windows','actor_placements_in_stored_segments','directory']}),flush=True)


if __name__=='__main__':main()
