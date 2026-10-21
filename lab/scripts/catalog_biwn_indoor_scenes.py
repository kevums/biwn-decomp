"""Inventory actual repeated-tag indoor records, without executing the game."""
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
from biwn_disc_backend import Disc,ROOT

sha=lambda value:hashlib.sha256(value).hexdigest()
save=lambda path,data:path.write_text(json.dumps(data,indent=2)+'\n')


def records(data,ram):
    rows=[]
    for match in re.finditer(rb'(\x00\x00[\x60-\x7f][\x00-\xff])\1{15}',data):
        tag=int.from_bytes(match[1],'big');index=tag-0x6000
        body=data[match.end():match.end()+4640];assert len(body)==4640
        get=lambda offset,width=2:int.from_bytes(body[offset:offset+width],'big')
        region_count=get(0);groups=get(2);region_offset=get(4,4);group_offset=get(8,4)
        assert 14<=region_offset<=4640 and region_offset+region_count*24<=4640
        assert region_offset+region_count*24==group_offset
        textures_at=group_offset+groups*6;assert textures_at+2<=4640
        texture_count=get(textures_at);texture_ids=[get(textures_at+2+i*2)for i in range(texture_count)]
        actors_at=textures_at+2+texture_count*2;assert actors_at+2<=4640
        actor_count=get(actors_at);actors_at+=2;assert actors_at+actor_count*8<=4640
        actors=[]
        for i in range(actor_count):
            record=[get(actors_at+i*8+j*2)for j in range(4)];actor_id=record[0];flags=ram[0x4208c+actor_id]
            kind='dynamic_task'if flags&1 else'static_sprite'if flags&2 else'static_decode'
            actors.append(dict(raw_words=record,actor_id=actor_id,resident_flags=flags,source_factory_path=kind))
        assert match.start()==0x591c90+index*4704+674
        rows.append(dict(index=index,tag=hex(tag),normalized_marker_offset=match.start(),marker_bytes=64,
            physical_record_bytes=4704,physical_body_bytes=4640,original_requested_payload_bytes=4704,
            requested_payload_sha256=sha(data[match.end():match.end()+4704]),body_sha256=sha(body),
            region_count=region_count,group_records_of_six_bytes=groups,region_relative_offset=region_offset,
            group_relative_offset=group_offset,permissions_word=hex(get(12)),texture_ids=texture_ids,
            actor_count=actor_count,actors=actors,last_actor_record_end=actors_at+actor_count*8))
    assert [row['index']for row in rows]==list(range(800))
    return rows


def main():
    out=ROOT/'verification/indoor-scene-catalog'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    disc=Disc();snapshot=ROOT/'runs/zero-warm-whole-merchant-reference/final-RAM.bin';ram=snapshot.read_bytes();rows=records(disc.data,ram)
    save(out/'records.json',rows)
    classes=Counter(actor['source_factory_path']for row in rows for actor in row['actors'])
    report=dict(status='800_unique_indoor_record_tags_and_bounded_body_layouts_catalogued',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(out),records=len(rows),index_range=[0,799],distinct_4640byte_bodies=len({row['body_sha256']for row in rows}),records_with_actors=sum(bool(row['actor_count'])for row in rows),actor_placements=sum(row['actor_count']for row in rows),actor_factory_classification=dict(classes),distinct_actor_ids=sorted({actor['actor_id']for row in rows for actor in row['actors']}),maximum_actor_end=max(row['last_actor_record_end']for row in rows),normalized_disc_sha256=disc.manifest['normalized_track_sha256'],source_CDI_sha256=disc.manifest['source_CDI_sha256'],resident_classification_RAM=str(snapshot),resident_classification_RAM_sha256=sha(ram),script_sha256=sha(Path(__file__).read_bytes()),game_execution=False,new_training=False,scope='Static scan of normalized track for sixteen repeated longword tags6000..631F; all800unique indices have in-bounds region/group/texture/actor layouts and exact original file-offset relation. Tags/records are not800distinct completed levels; body hashes report duplicates. Actor classes come from the preserved resident flag table and existing factory branch semantics, not inferred names or runtime coverage. Every physical4704byte record includes64markerbytes, leaving4640bodybytes; original loader requests4704bytes AFTER marker and consequently includes64bytes beyond the physical body. Catalogue preserves this behavior without repairing disc/game. No gameplay, scheduling, rendering or port completion claim.')
    save(out/'report.json',report);save(ROOT/'verification/indoor-scene-catalog-current.json',report)
    print(json.dumps({k:report[k]for k in ['status','records','distinct_4640byte_bodies','records_with_actors','actor_placements','actor_factory_classification','directory']}),flush=True)


if __name__=='__main__':main()
