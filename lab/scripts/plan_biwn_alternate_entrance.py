"""Read a verified warm RAM window and propose ordinary-pad waypoints.

This is static route discovery, not navigation execution or C verification.
Room bounds/edges follow 1039C/102C4 and 13C9A/13B5A; portal keys follow10430.
"""
import hashlib
import json
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    source = ROOT / 'runs/fresh-whole-merchant-C-candidate2/warm-RAM.bin'
    ram = source.read_bytes()
    assert len(ram) == 0x200000
    def read(a, n=2):
        a &= 0xffffff
        assert 0 <= a <= len(ram)-n
        return int.from_bytes(ram[a:a+n], 'big')
    player = 0x49c4c
    start = (read(player+64), read(player+66))
    origin = (read(player+4, 4) & ~1023, read(player+10, 4) & ~1023)
    rooms = {}
    for tile in range(25):
        container = read(0x49bb4+tile*4, 4) & 0xffffff
        if not container:
            continue
        count = read(container)
        assert count <= 256
        base = read(container+8, 4) & 0xffffff
        gates = read(container+12, 4) & 0xffffff
        tile_origin = (origin[0]+(tile%5-start[0]%5)*1024,
                       origin[1]+(tile//5-start[0]//5)*1024)
        for index in range(count):
            record = base+index*20
            x,z,w,h = [read(record+offset) for offset in [10,14,16,18]]
            assert 0<=x<16 and 0<=z<16 and 0<w<=16 and 0<h<=16
            rooms[(tile,index)] = dict(record=record,
                bounds=[tile_origin[0]+x*64,tile_origin[1]+z*64,
                        tile_origin[0]+(x+w)*64,tile_origin[1]+(z+h)*64],
                edges=[read(record+o) for o in [2,4,6,8]],
                gate_base=gates, gate_count=read(container+2))
    def crossing(a,b,direction):
        if direction in [0,1]:
            low,high=max(a[0],b[0]),min(a[2],b[2])
            if low>=high or (a[3]!=b[1] if direction==0 else a[1]!=b[3]):return None
            x=(low+high)//2;z=a[3] if direction==0 else a[1]
            return [x,z+(16 if direction==0 else -16)]
        low,high=max(a[1],b[1]),min(a[3],b[3])
        if low>=high or (a[2]!=b[0] if direction==2 else a[0]!=b[2]):return None
        x=a[2] if direction==2 else a[0];z=(low+high)//2
        return [x+(16 if direction==2 else -16),z]
    graph = {}; entrances = []
    for node,room in rooms.items():
        links=[]
        for direction,edge in enumerate(room['edges']):
            candidates=[]
            if edge<0x1000 and (node[0],edge) in rooms:
                candidates=[(node[0],edge)]
            elif edge==0xffff:
                next_tile=node[0]+[5,-5,1,-1][direction]
                if 0<=next_tile<25 and (direction<2 or next_tile//5==node[0]//5):
                    candidates=[n for n in rooms if n[0]==next_tile]
            elif edge&0xf000==0x1000:
                index=edge&0xfff
                if index<room['gate_count']:
                    gate=room['gate_base']+index*28
                    key=read(gate+[11,13,15,17][direction],1)
                    target=read(gate+26)
                    if key<16 and target!=0xffff:
                        a=room['bounds']
                        point=([a[0]+key*64+32,a[3]+32] if direction==0 else
                               [a[2]-key*64-32,a[1]-32] if direction==1 else
                               [a[2]+32,a[3]-key*64-32] if direction==2 else
                               [a[0]-32,a[1]+key*64+32])
                        entrances.append(dict(node=node,index=index,direction=direction,
                                              target=target,key=key,point=point,record=gate))
            for candidate in candidates:
                point=crossing(room['bounds'],rooms[candidate]['bounds'],direction)
                if point is not None:links.append((candidate,point))
        graph[node]=links
    assert start in graph
    parents={start:None};queue=deque([start])
    while queue:
        node=queue.popleft()
        for following,point in graph[node]:
            if following not in parents:
                parents[following]=(node,point);queue.append(following)
    reachable=[g for g in entrances if g['target']==17 and tuple(g['node']) in parents]
    if not reachable:
        diagnostic=dict(status='no_scene17_route_in_static_room_graph',
                        source_RAM=str(source),source_RAM_sha256=hashlib.sha256(ram).hexdigest(),
                        start=start,parsed_rooms=len(rooms),reachable_nodes=list(parents),
                        entrances=entrances,
                        graph={str(n):[list(v) for v,p in links]for n,links in graph.items()},
                        limitation='Room-edge graph may omit other source movement/transition semantics; no runtime conclusion.')
        (ROOT/'verification/normal-route-17-discovery.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
        print(json.dumps(dict(status=diagnostic['status'],reachable=list(parents),entrances=entrances)))
        return
    def route(gate):
        node=tuple(gate['node']);steps=[]
        while parents[node] is not None:
            before,point=parents[node];steps.append((node,point));node=before
        return list(reversed(steps))
    gate=min(reachable,key=lambda g:len(route(g)))
    steps=route(gate);points=[]
    for node,point in steps:
        points.append(point)
        a=rooms[node]['bounds'];points.append([(a[0]+a[2])//2,(a[1]+a[3])//2])
    points.append(gate['point'])
    report=dict(status='static_route_hypothesis_pending_ordinary_pad_execution',
                source_RAM=str(source),source_RAM_sha256=hashlib.sha256(ram).hexdigest(),
                points=points,start=list(start),source_room_route=[list(start)]+[list(n)for n,p in steps],
                gate=gate,parsed_rooms=len(rooms),reachable_rooms=len(parents),
                discovered_entrances=entrances,guest_memory_writes=False,
                coordinator_navigation=True,local_LLM_navigation=False,new_training=False,
                limits=['One warm25-tile window; room graph and doorway hypothesis only.',
                        'Ordinary controller execution may reject clearance, loading or gate assumptions.',
                        'No reconstructed-C, whole-game, physical timing or standalone proof.'])
    target=ROOT/'verification/normal-route-17-plan.json'
    target.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(plan=str(target),rooms=len(rooms),reachable=len(parents),
                         path=report['source_room_route'],gate=gate,waypoints=len(points))))


if __name__=='__main__':main()
