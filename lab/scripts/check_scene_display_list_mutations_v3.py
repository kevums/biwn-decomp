"""Check64distinct external reread fixtures without replaying the completed parent matrix."""
import json
from datetime import datetime,timezone
from pathlib import Path
import scene_display_list_mutation_vectors_v2 as vectors
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha

def main():
    h=vectors.parent;base=h.base;parent_path=V/'scene-display-list-algorithm-host-v2-current.json';parent=read(parent_path)
    assert parent['completed']==1217
    for p,d in parent['source_sha256'].items():assert sha(p)==d,p
    out=V/'scene-display-list-mutations-v3'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    session=Path(read(ROOT/'projects/black-ice-white-noise/analysis/current-session.json')['directory']);mapping=read(session/'display-list-fullCPU-generation.json');runtime=h.Runtime(parent['library'],mapping['instructions_decoded']);snapshot=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();rows=[]
    try:
        for case in vectors.cases(snapshot):
            ram=base.fixture(snapshot,case);left,a,n=runtime.native(ram,case,set());other,b,u=runtime.unicorn(ram,case,set());right,c,r=runtime.translated(ram,case)
            valid=bytes(a)==bytes(b)==bytes(c) and left==other==right and not r['status'] and u['trace']==r['trace']
            if not valid:save(out/'counterexample.json',dict(case=case,original=base.queue.cd.scheduler.cpu_dict(a),rebuilt=base.queue.cd.scheduler.cpu_dict(c),Unicorn=u,translated=r))
            assert valid,out/'counterexample.json'
            assert not any(runtime.queues.values()),runtime.queues
            rows.append(dict(case=case['id'],CCR=case['SR']&31,supervisor=bool(case['SR']&0x2000),ordered_accesses=len(r['trace'])))
    finally:runtime.close()
    save(out/'cases.json',rows);save(out/'vectors.json',vectors.cases(snapshot));state=dict(status='terminal_64_distinct_display_list_reread_full_CPU_RAM_order_pass',directory=str(out),completed=64,parent_host_cases=1217,parent_distinct_reread_vectors=2,parent_reread_case_count=64,new_predictions=0,new_training=False,source_sha256={str(p):sha(p)for p in [Path(__file__),Path(vectors.__file__),Path(h.__file__),parent_path,out/'cases.json',out/'vectors.json']},scope='Additional64distinct fixtures, all32CCR/bothbanks. Native pinnedCPUinjects before exact operand, Unicorn/C bus-read changes. Two original reread fixtures in the1217parent run were repeated64times; this supplement adds actual distinct inputs. No hardware concurrency or timing claim.');save(V/'scene-display-list-mutations-v3-current.json',state);print(state['status'],flush=True)
if __name__=='__main__':main()
