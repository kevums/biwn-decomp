"""Compare raw marker spacing with frozen source acquisition tables; no patches."""
import hashlib,json
from datetime import datetime,timezone
from pathlib import Path
from biwn_disc_backend import Disc

ROOT=Path(__file__).resolve().parents[1]


def main():
    disc=Disc();atlas_path=ROOT/'verification/zero-warm-startup-instruction-atlas.bin'
    atlas=atlas_path.read_bytes();rows=[]
    for mode in [1,2,3]:
        count=int.from_bytes(atlas[0x464a0+mode*2:0x464a2+mode*2],'big')
        bias=int.from_bytes(atlas[0x464c8+mode*2:0x464ca+mode*2],'big')
        offset=int.from_bytes(atlas[0x464a8+mode*4:0x464ac+mode*4],'big')
        tag=int.from_bytes(atlas[0x464b8+mode*4:0x464bc+mode*4],'big')
        low=max(0,offset-0x10000);high=min(len(disc.data),offset+0x1000000)
        markers=[];missing=0
        for group in range(256):
            pattern=(tag+group).to_bytes(4,'big')*16
            positions=[];start=low
            while len(positions)<3:
                position=disc.data.find(pattern,start,high)
                if position<0:break
                positions.append(position);start=position+64
            if positions:
                missing=0;markers.append(dict(group=group,tag=hex(tag+group),positions=positions))
            else:
                missing+=1
                if markers and missing>=8:break
        intervals=[]
        for left,right in zip(markers,markers[1:]):
            if right['group']!=left['group']+1:continue
            stride=right['positions'][0]-left['positions'][0]
            payload_extent=stride-64
            intervals.append(dict(group=left['group'],next_group=right['group'],
                                  stride=stride,payload_extent=payload_extent,
                                  whole_8192_blocks=payload_extent/8192,
                                  matches_frozen_count=payload_extent==count*8192))
        rows.append(dict(mode=mode,frozen_bias=bias,frozen_count=count,
                         frozen_offset=hex(offset),frozen_tag=hex(tag),markers=markers,
                         intervals=intervals,expected_stride=count*8192+64))
    snapshots=[]
    for name in ['zero-warm-whole-merchant-CPU-GPU-DSP',
                 'scene17-full-fixed-CPU-GPU-DSP-candidate2','scene532-full-fixed-CPU-GPU-DSP']:
        p=ROOT/'runs'/name/'final-RAM.bin';m=p.read_bytes()
        snapshots.append(dict(route=name,sha256=hashlib.sha256(m).hexdigest(),
                              mode=int.from_bytes(m[0x15b530:0x15b532],'big'),
                              mode3_count=int.from_bytes(m[0x464a6:0x464a8],'big')))
    report=dict(status='disc_markers_and_frozen_tables_inspected',
                recorded_at=datetime.now(timezone.utc).isoformat(),
                atlas_sha256=hashlib.sha256(atlas).hexdigest(),
                normalized_track_sha256=disc.manifest['normalized_track_sha256'],
                modes=rows,verified_route_final_snapshots=snapshots,
                original_tables_changed=False,natural_mode3_use_verified=False,
                scope='Sixteen-longword marker locations and adjacent physical byte extents from the preserved normalized disc. '
                      'Extents are observed spacing, not decoded image counts or confirmed asset schema. '
                      'Frozen source count/offset/tag tables and three verified final route RAM snapshots compared. '
                      'No restoration patch, mode3 natural gameplay, author-intended format or causal explanation established.')
    path=ROOT/'verification/frame-disc-layout-current.json';path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps([dict(mode=r['mode'],count=r['frozen_count'],markers=len(r['markers']),
                           strides=sorted(set(x['stride']for x in r['intervals'])),
                           matching_intervals=sum(x['matches_frozen_count']for x in r['intervals']))for r in rows]))


if __name__=='__main__':main()
