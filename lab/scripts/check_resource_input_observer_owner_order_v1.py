"""Isolate both resource/GPU conflict orders and different-task controls."""
import ctypes as c
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha


def main():
    gp=V/'resource-input-arena-observer-qualified-v1-current.json';g=read(gp)
    for p,h in g['source_sha256'].items():assert sha(p)==h,p
    bp=V/'native-input-arena-disc-build-v1-current.json';b=read(bp);f=c.CDLL(g['library'])
    f.fixture_put.argtypes=[c.c_uint32,c.c_uint32];f.fixture_reg.argtypes=[c.c_uint,c.c_uint32];f.fixture_active.argtypes=[c.c_uint,c.c_uint];f.fixture_observe.argtypes=[c.c_uint32];f.fixture_stat.argtypes=[c.c_uint];f.fixture_stat.restype=c.c_uint64
    stage=Path(b['derived_stage']).read_bytes();GPU=int.from_bytes(stage[0xe220-0x4000+2:0xe220-0x4000+6],'big');entry=b['resource_arena_symbols']['biwn_acquire_arena_entry'];rows=[]
    for slot in [0,50,100,101]:
        task=0xc0928+slot*1024 if slot<101 else 0;other_slot=(slot+1)%101;other=0xc0928+other_slot*1024
        for order in ['resource_inside_GPU','GPU_inside_resource']:
            for same in [False,True]:
                f.fixture_reset();f.fixture_put(0xc0920,task);f.fixture_reg(15,task+900 if task else 0x1d9000)
                if order=='resource_inside_GPU':
                    f.fixture_active(slot if same else other_slot,1);f.fixture_observe(0x1af04);f.fixture_observe(entry)
                else:
                    f.fixture_observe(0x1af04);f.fixture_observe(entry)
                    if not same:f.fixture_put(0xc0920,other);f.fixture_reg(15,other+900)
                    f.fixture_observe(GPU)
                assert bool(f.fixture_stat(1))==same,(slot,order,same)
                assert bool(f.fixture_stat(0))==same,(slot,order,same)
                rows.append(dict(slot=slot,order=order,same_task=same,alias_rejected=same))
    out=V/'resource-input-observer-owner-order-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'cases.json',rows)
    proof=dict(status='terminal_resource_input_observer_both_owner_orders_isolated_controls_pass',directory=str(out),controls=len(rows),same_task_rejected=sum(r['same_task']for r in rows),different_task_accepted=sum(not r['same_task']for r in rows),boot_slot_included=True,observer_only_not_production_reentry_guard=True,actual_guest_execution=False,new_predictions=0,optimizer_updates=0,source_sha256={str(p):sha(p)for p in [Path(__file__),gp,bp,Path(g['library']),out/'cases.json']})
    save(out/'protocol.json',proof);save(V/'resource-input-observer-owner-order-v1-current.json',proof);print(proof['status'],len(rows),flush=True)


if __name__=='__main__':main()
