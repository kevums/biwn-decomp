"""Read-only actual CPU/RAM replay for the compact persistent-context outer watcher.

Sixty-four seeded root entries run original/native lanes. Unlike continuation
fixtures, every lane witnesses its actual public root before monitoring.
No observer reconstruction or CPU/RAM writes are applied to the guest.
"""
import ctypes as c,importlib.util,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
    pointer=V/'outer-outer-compact-geometry-observer-qualified-v1-current.json';g=read(pointer)
    for p,h in g['source_sha256'].items():assert sha(p)==h,p
    folder=Path(g['directory']);text=(folder/'fixture.c').read_text()
    out=V/'outer-compact-outer-observer-actual-CPU-v2'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    start=text.index(' unsigned relevant=',text.index('static void o6_watch('));end=text.index(' if(!relevant)return;',start)
    text+='\nvoid snapshot(const void *raw,const struct cpu *cpu){memcpy(memory,raw,sizeof(memory));current=*cpu;}\nint wants(uint32_t pc){'+text[start:end]+'return relevant!=0;}\nuint64_t boundaries(unsigned n){if(n==0)return o6_iterations;if(n==1)return o6_original_iterations;uint64_t total=0;for(unsigned i=0;i<13;i++)total+=n==2?o6_helper_entries[i]:o6_helper_returns[i];return total;}\n'
    source=out/'fixture.c';source.write_text(text);library=out/'fixture.dylib'
    q=subprocess.run(['clang','-dynamiclib','-std=c99','-O2','-Wall','-Wextra','-Werror',str(source),'-o',str(library)],capture_output=True,text=True);(out/'compiler.log').write_text(q.stdout+q.stderr);assert q.returncode==0,q.stderr
    f=c.CDLL(str(library));f.snapshot.argtypes=[c.c_void_p,c.c_void_p];f.wants.argtypes=[c.c_uint32];f.wants.restype=c.c_int;f.fixture_pc.argtypes=[c.c_uint32];f.fixture_stat.argtypes=[c.c_uint];f.fixture_stat.restype=c.c_uint64
    driver=ROOT/'scripts/check_native_deck_outer_connected_outer_compact_v1.py';body=driver.read_text()
    before='source[i%64 if i%8==0 else 64+i]';assert body.count(before)==1;body=body.replace(before,'source[i%64]')
    body=body.replace('low=368\n','low=368;iterations=0\n')
    old_native="if native and pc==osym['biwn_outer_iteration_boundary']:state.pc=0x11e86;status=6;break"
    old_original="if not native and pc==0x11e86 and step:status=6;break"
    assert body.count(old_native)==body.count(old_original)==1
    body=body.replace(old_native,"if native and pc==osym['biwn_outer_iteration_boundary']:\n                iterations+=1\n                if iterations>=2:state.pc=0x11e86;status=6;break")
    body=body.replace(old_original,"if not native and pc==0x11e86 and step:\n                iterations+=1\n                if iterations>=2:status=6;break")
    body=body.replace('native-Deck-outer-connected-outer-compact-v1','native-Deck-outer-connected-outer-compact-observed-root-v1')
    harness=out/'root-harness.py';harness.write_text(body);spec=importlib.util.spec_from_file_location('compact_root_observed',harness);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    f.boundaries.argtypes=[c.c_uint];f.boundaries.restype=c.c_uint64
    rows=[]
    class Observed(m.Engine):
        observing=False
        def cpu(self):
            state=super().cpu()
            if self.observing and f.wants(state.pc):
                f.snapshot(c.create_string_buffer(self.native.device.ram()),c.byref(state));f.fixture_pc(state.pc)
            return state
        def run(self,*args):
            assert args[1].pc==0x11e6c
            native=args[-1];f.fixture_reset();self.observing=True
            try:result=super().run(*args)
            finally:self.observing=False
            stats=[f.fixture_stat(i)for i in range(12)]
            boundaries=[f.boundaries(i)for i in range(4)]
            assert stats[0]==stats[2]==stats[3]==0 and stats[4]==1 and boundaries[2]==boundaries[3],(stats,boundaries)
            if result[0]==6:
                assert stats[1]==1 and stats[6]==stats[7]==0,(stats,boundaries)
                assert (stats[5]==1 and stats[10]>0 and boundaries[0]==2)if native else(stats[5]==0 and boundaries[1]==2),(stats,boundaries)
            else:
                assert result[0]==0 and stats[1]==0
                assert (stats[5:8]==[1,1,0]and stats[10]>0)if native else(stats[5:8]==[0,0,1]),stats
            rows.append(dict(native=native,status=result[0],stats=stats,boundaries=boundaries));save(out/'cases-progress.json',rows);return result
    m.Engine=Observed;sys.argv=[str(harness),'--limit','64'];m.main()
    assert len(rows)==128
    save(out/'cases.json',rows)
    proof=dict(status='terminal_compact_outer_monitor_128_actual_root_and_iteration_CPU_lanes_pass',directory=str(out),CPU_lanes=128,actual_public_root_entries=128,all_errors_outside_zero=True,boundary_pending_explicitly_verified=True,complete_task_lifetime_verified=False,host_guest_RAM_writes=0,new_predictions=0,new_training=False,
        source_sha256={str(p):sha(p)for p in [Path(__file__),pointer,Path(g['source_sha256'] and folder/'fixture.c'),source,library,driver,harness,out/'cases.json']},scope=__doc__+' Root plus one full subsequent iteration runs to an explicit status6 boundary; one active outer monitor is expected there and checked, while helper pending/errors/outside must be zero. Actual helper/capture CPU sites, persistent CPU pointer and compact stack bounds are checked. Both underlying lanes also compare CPU/nonarenaRAM/ordered helper entries. Component fixtures do not establish arbitrary IRQ or live game timing.')
    save(out/'review.json',proof);save(V/'outer-compact-outer-observer-actual-CPU-v2-current.json',proof);print(proof['status'],flush=True)

if __name__=='__main__':main()
