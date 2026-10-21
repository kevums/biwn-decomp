"""Global source-derived room graph; no guest writes or execution claims."""
import hashlib
import argparse
import json
from collections import deque
from pathlib import Path
from biwn_disc_backend import Disc, ROOT


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--target',type=int,default=17)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--entrance-node',type=int,nargs=3)
    args=parser.parse_args()
    assert 0<=args.target<=65535
    disc=Disc()
    inventory=json.loads((ROOT/'verification/biwn-disc-gate-target-inventory.json').read_text())
    assert inventory['normalized_track_sha256']==disc.manifest['normalized_track_sha256']
    rooms={};segments={};unresolved=[]
    u=lambda b,a,n=2:int.from_bytes(b[a:a+n],'big')
    for payload in inventory['payloads']:
        marker=payload['marker'];block=disc.data[marker+64:marker+64+4704]
        assert hashlib.sha256(block).hexdigest()==payload['sha256']
        tag=int(payload['tag'],16)-0x2000
        for segment in range(9):
            raw=block[payload['offsets'][segment]:payload['offsets'][segment+1]]
            cell=(tag%13*5+segment,46-tag//13)
            if len(raw)<16:continue
            count,base=u(raw,0),u(raw,8)
            gates,gate_base=u(raw,2),u(raw,10)
            if base+count*20>len(raw) or gate_base+gates*28>len(raw):
                unresolved.append(dict(cell=cell,reason='record_bounds'));continue
            if cell in segments:
                # Overlapping groups may share cells; require same geometry
                # before taking the first validated cell as a graph input.
                old=segments[cell]
                if old!=raw:unresolved.append(dict(cell=cell,reason='overlap_bytes_differ'))
                continue
            segments[cell]=raw
            for index in range(count):
                record=raw[base+index*20:base+(index+1)*20]
                x,z,w,h=[u(record,o) for o in [10,14,16,18]]
                if not(0<=x<16 and 0<=z<16 and 0<w<=16 and 0<h<=16):
                    unresolved.append(dict(cell=cell,room=index,reason='noncanonical_bounds'));continue
                rooms[cell+(index,)]=dict(record=record,
                    bounds=[cell[0]*1024+x*64,cell[1]*1024+z*64,
                            cell[0]*1024+(x+w)*64,cell[1]*1024+(z+h)*64],
                    edges=[u(record,o) for o in [2,4,6,8]],
                    gates=[raw[gate_base+i*28:gate_base+(i+1)*28]for i in range(gates)])
    warm_path=ROOT/'runs/fresh-whole-merchant-C-candidate2/warm-RAM.bin'
    ram=warm_path.read_bytes();r=lambda a,n=2:u(ram,a&0xffffff,n)
    start=(r(0x49c50,4)//1024,r(0x49c56,4)//1024,r(0x49c4c+66))
    assert start in rooms
    checked=0
    for tile in range(25):
        cell=(start[0]+tile%5-2,start[1]+tile//5-2)
        container=r(0x49bb4+tile*4,4)&0xffffff
        count=r(container);base=r(container+8,4)&0xffffff
        for index in range(count):
            # Source loader can relocate texture IDs; graph excludes word0.
            assert rooms[cell+(index,)]['record'][2:]==ram[base+index*20+2:base+(index+1)*20]
            checked+=1
    def crossing(a,b,d):
        if d<2:
            low,high=max(a[0],b[0]),min(a[2],b[2])
            if low>=high or (a[3]!=b[1] if d==0 else a[1]!=b[3]):return None
            return [(low+high)//2,(a[3]+16 if d==0 else a[1]-16)]
        low,high=max(a[1],b[1]),min(a[3],b[3])
        if low>=high or (a[2]!=b[0] if d==2 else a[0]!=b[2]):return None
        return [(a[2]+16 if d==2 else a[0]-16),(low+high)//2]
    by_cell={}
    for node in rooms:by_cell.setdefault(node[:2],[]).append(node)
    graph={};entrances=[]
    for node,room in rooms.items():
        links=[]
        for d,edge in enumerate(room['edges']):
            candidates=[]
            if edge<0x1000 and node[:2]+(edge,) in rooms:candidates=[node[:2]+(edge,)]
            elif edge==0xffff:
                dx,dz=[(0,1),(0,-1),(1,0),(-1,0)][d]
                candidates=by_cell.get((node[0]+dx,node[1]+dz),[])
            elif edge&0xf000==0x1000 and (edge&0xfff)<len(room['gates']):
                record=room['gates'][edge&0xfff];key=u(record,[11,13,15,17][d],1);target=u(record,26)
                if key<16 and target!=0xffff:
                    a=room['bounds'];point=([a[0]+key*64+32,a[3]+32]if d==0 else
                        [a[2]-key*64-32,a[1]-32]if d==1 else
                        [a[2]+32,a[3]-key*64-32]if d==2 else[a[0]-32,a[1]+key*64+32])
                    entrances.append(dict(node=node,gate_index=edge&0xfff,direction=d,
                                          target=target,key=key,point=point,record_hex=record.hex()))
            for following in candidates:
                point=crossing(room['bounds'],rooms[following]['bounds'],d)
                if point is not None:links.append((following,point))
        graph[node]=links
    parents={start:None};queue=deque([start])
    while queue:
        node=queue.popleft()
        for following,point in graph[node]:
            if following not in parents:parents[following]=(node,point);queue.append(following)
    def route(gate):
        node=tuple(gate['node']);steps=[]
        while parents[node] is not None:
            before,point=parents[node];steps.append((node,point));node=before
        return list(reversed(steps))
    candidates=[g for g in entrances if g['target']==args.target and tuple(g['node'])in parents and (args.entrance_node is None or list(g['node'])==args.entrance_node)]
    report=dict(status='static_disc_graph_no_target_route',target=args.target,parsed_rooms=len(rooms),
                parsed_cells=len(segments),reachable_rooms=len(parents),warm_room_records_matched=checked,
                normalized_track_sha256=inventory['normalized_track_sha256'],source_RAM=str(warm_path),
                source_RAM_sha256=hashlib.sha256(ram).hexdigest(),unresolved=unresolved,
                reachable_entrances=[g for g in entrances if tuple(g['node'])in parents],
                target_route_lengths=[dict(target=g['target'],room_steps=len(route(g)),node=g['node'])
                                      for g in entrances if tuple(g['node'])in parents],
                guest_memory_writes=False,coordinator_navigation=True,local_LLM_navigation=False,
                limits=['Static graph excludes noncanonical/invalid/overlapping inputs; no full map correctness claim.',
                        'Source geometry matched warm window; other source movement/transition rules may be omitted.',
                        'Waypoints need ordinary-pad runtime observation and later original/C comparisons.'])
    if candidates:
        gate=min(candidates,key=lambda g:len(route(g)));steps=route(gate);points=[]
        for node,point in steps:
            points.append(point);a=rooms[node]['bounds'];points.append([(a[0]+a[2])//2,(a[1]+a[3])//2])
        a=rooms[tuple(gate['node'])]['bounds'];gx,gz=gate['point'];d=gate['direction']
        # Align parallel to the boundary before moving through the key slot.
        # A diagonal approach can hit the blocked edge before its key matches,
        # causing the source movement routine to undo both coordinate changes.
        alignment=([gx,a[3]-32]if d==0 else[gx,a[1]+32]if d==1 else
                   [a[2]-32,gz]if d==2 else[a[0]+32,gz])
        points.extend([alignment,gate['point']])
        report.update(status='static_disc_route_hypothesis_pending_ordinary_pad_execution',
                      points=points,source_room_route=[start]+[n for n,p in steps],gate=gate,
                      gate_alignment=alignment,
                      gate_alignment_reason='Observed first route stalled atX8056,Z44032 during diagonal entry; align inside room before crossing.')
    path=args.output or ROOT/f'verification/normal-route-{args.target}-disc-plan.json'
    path.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(plan=str(path),status=report['status'],rooms=len(rooms),reachable=len(parents),
                         warm_rooms_matched=checked,unresolved=len(unresolved),gate=report.get('gate'),
                         steps=len(report.get('source_room_route',[])))))


if __name__=='__main__':main()
