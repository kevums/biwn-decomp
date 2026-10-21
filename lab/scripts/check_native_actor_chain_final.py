"""Original movement/collision versus a source-owned native C call chain.

Both public collision roots and movement are compared. Internal collision uses
the C ABI; its shadow entry CPU is compared to the original physical entry.
Remaining direction/GPU/geometry helper entries retain actual physical ABI.
Only E220 effects are prescribed in movement cases; direct collision has no
prescribed helper. Full returnedCPU/SR/banks/publicRAM/ordered access compare.
"""
import argparse
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import check_biwn_native_actor_collision_v2 as direct
import native_actor_chain_engine as chain

ROOT=chain.ROOT
ND=chain.ND


def prepare(gate):
    baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes()
    build=direct.g.read(ROOT/'verification/native-actor-collision-disc-build-current.json')
    assert direct.g.sha(build['derived_stage'])==build['derived_stage_sha256']
    assert direct.g.sha(build['component'])==build['component_sha256']
    snapshot=bytearray(baseline)
    snapshot[0x4000:0x100000]=Path(build['derived_stage']).read_bytes()
    resident=build['resident_address']
    snapshot[resident:resident+23260]=Path(build['component']).read_bytes()[:23260]
    for entry,width in {0x13c9a:8,**direct.g.PATCH_WIDTHS}.items():
        snapshot[entry:entry+width]=baseline[entry:entry+width]
    payload=Path(gate['binary']).read_bytes()
    base=gate['code_address']
    # Avoid treating obsolete movement/collision payload as a legal fallback.
    chain.BASE=chain.COLLBASE=direct.BASE=base
    chain.PARENT_RANGE=direct.PARENT_RANGE=(resident,resident+23260)
    chain.COLL_PAYLOAD=payload
    chain.COLL_SYMBOLS=gate['symbols']
    return bytes(snapshot),payload,gate['symbols'],build


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--limit',type=int)
    ap.add_argument('--address',type=lambda x:int(x,0),default=0x180000)
    ap.add_argument('--move-source',type=Path,default=ND/'actor-chain-move.c')
    ap.add_argument('--collision-source',type=Path,default=ND/'actor-chain-collision.c')
    args=ap.parse_args()
    out=ROOT/'verification/native-actor-chain-final'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    print(out,flush=True)
    command=['make','-f',str(ND/'Makefile.actor-chain-compact'),'actor-chain','BUILD='+str(out/'build'),'ADDRESS='+hex(args.address),'MOVE_SOURCE='+str(args.move_source.resolve()),'COLLISION_SOURCE='+str(args.collision_source.resolve())]
    p=subprocess.run(command,capture_output=True,text=True)
    (out/'build.log').write_text(p.stdout+p.stderr)
    assert p.returncode==0,p.stderr
    binary=out/'build/actor-chain.bin';elf=out/'build/actor-chain.elf'
    nm=subprocess.check_output([str(ROOT/'tools/m68k-elf/bin/m68k-elf-nm'),'-n',str(elf)],text=True)
    (out/'symbols.txt').write_text(nm)
    symbols={x[2]:int(x[0],16)for line in nm.splitlines()if len(x:=line.split())==3}
    gate=dict(binary=str(binary),ELF=str(elf),code_address=args.address,symbols=symbols)
    snapshot,payload,symbols,build=prepare(gate)
    assert len(payload)<=build['component_bytes']-23260
    collisions=direct.vectors();movements=chain.vectors()
    if args.limit:
        collisions=sum([[c for c in collisions if c['entry']==entry][:args.limit]for entry in direct.g.PATCH_WIDTHS],[])
        movements=[movements[i]for i in[0,16,32,80,96,112,160,176]][:args.limit]
    direct.g.save(out/'collision-fixtures.json',collisions);direct.g.save(out/'movement-fixtures.json',movements)
    direct.g.save(out/'parent-build.json',build)
    paths=[Path(__file__),Path(chain.__file__),Path(chain.g.__file__),Path(direct.__file__),Path(direct.g.__file__),args.move_source.resolve(),args.collision_source.resolve(),*[ND/n for n in ['actor-chain-native.h','actor-chain-compact-shim.S','actor-chain.ld','Makefile.actor-chain-compact']],binary,elf,out/'parent-build.json',Path(build['derived_stage']),Path(build['component']),ROOT/'tools/blitter-runtime/virtualjaguar_libretro.dylib',ROOT/'scripts/check_biwn_scheduler.py']
    hashes={str(p):direct.g.sha(p)for p in paths}
    state=dict(status='checking_source_owned_actor_chain',directory=str(out),pid=os.getpid(),planned=len(collisions)+len(movements),completed=0,binary_bytes=len(payload),binary=str(binary),ELF=str(elf),symbols=symbols,code_address=args.address,source_sha256=hashes,new_predictions=0,disc_integrated=False,scope=__doc__)
    def mark():
        direct.g.save(out/'protocol.json',state)
        direct.g.save(ROOT/'verification/native-actor-chain-final-active.json',state)
    mark();native=chain.Native();rows=[];coverage=set()
    try:
        for group,engine,cases in [('collision',direct,collisions),('movement',chain,movements)]:
            for i,case in enumerate(cases):
                a=engine.execute(snapshot,case,payload,symbols,False)
                b=engine.execute(snapshot,case,payload,symbols,True)
                diff=[key for key in ['ram','registers','trace']if a[key]!=b[key]]
                if diff:
                    direct.g.save(out/'mismatch.json',dict(group=group,index=i,case=case,differences=diff,original_trace=a['trace'],candidate_trace=b['trace'],original_registers=a['registers'],candidate_registers=b['registers']))
                    raise AssertionError('C-chain ordered comparison failed')
                an=engine.replay(native,snapshot,case,payload,symbols,False,a)
                bn=engine.replay(native,snapshot,case,payload,symbols,True,b)
                if an!=bn:
                    direct.g.save(out/'native-mismatch.json',dict(group=group,index=i,case=case,original=an,candidate=bn))
                    raise AssertionError('C-chain fullCPU/physical-helper/virtual-collision mismatch')
                coverage.update(a['coverage'])
                rows.append(dict(group=group,index=i,original_steps=len(a['machine']),candidate_steps=len(b['machine']),original_depth=a['private_depth'],candidate_depth=b['private_depth'],physical_or_virtual_helper_entries=len(an['events']),virtual_collision_entries=sum('virtual_collision_entry'in step for step in b['machine'])))
                state['completed']=len(rows)
                if i%64==0:
                    mark();print(group,i+1,'/',len(cases),'depth',b['private_depth'],flush=True)
        assert all(direct.g.sha(p)==h for p,h in hashes.items())
        direct.g.save(out/'results.json',rows)
        state.update(status='terminal_source_owned_actor_chain_preflight_pass'if args.limit else'terminal_source_owned_actor_chain_pass',completed=len(rows),collision_cases=len(collisions),movement_cases=len(movements),max_private_depth=max(row['candidate_depth']for row in rows),max_collision_depth=max(row['candidate_depth']for row in rows if row['group']=='collision'),max_movement_depth=max(row['candidate_depth']for row in rows if row['group']=='movement'),virtual_collision_entries=sum(row['virtual_collision_entries']for row in rows),original_sites=sorted(coverage))
        mark()
        if not args.limit:
            direct.g.save(ROOT/'verification/native-actor-chain-final-current.json',state)
        print(json.dumps({k:state[k]for k in ['status','binary_bytes','collision_cases','movement_cases','max_private_depth','virtual_collision_entries']}),flush=True)
    except BaseException as error:
        state.update(status='terminal_source_owned_actor_chain_failed',error=repr(error))
        mark();raise
    finally:
        native.close()


if __name__=='__main__':
    main()
