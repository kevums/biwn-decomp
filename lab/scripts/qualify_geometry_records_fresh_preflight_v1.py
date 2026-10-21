"""Bind exact component/alias/read-only monitor evidence before fresh v33 routes."""
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,read,save,sha
import shared_deck_geometry_records_full_observer_v1 as monitor

def main():
 counts={'geometry-records-whole-scene-disc-v3':772,'geometry-records-final-fallback-v1':384,'geometry-records-alias-reentry-v1':320,'native-deck-alias-nesting-geometry-records-final-v1':256,'native-geometry-records-geometry-alias-v1':128,'native-Deck-outer-connected-geometry-records-v1':128,'geometry-records-final-public-bus-v1':14,'geometry-records-final-display-v1':1153}
 names=[*counts,'native-Deck-geometry-records-final-v1','geometry-records-final-copied-rebuild-v1','geometry-records-geometry-observer-qualified-v1','outer-geometry-records-geometry-observer-qualified-v1','shared-Deck-region-check-geometry-records-v1','geometry-records-reset-observer-qualified-v1','geometry-records-shared-observer-qualified-v1','geometry-records-record-observer-actual-CPU-reviewed-v2','geometry-records-fallback-alias-observers-actual-CPU-v1','geometry-records-geometry-observer-actual-CPU-v1','geometry-records-outer-observer-actual-CPU-v2','geometry-records-clear-commit-observer-v1','geometry-records-rotation-commit-observer-v1','geometry-records-commit-observer-qualified-v1']
 out=V/'geometry-records-fresh-preflight-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);deps={str(Path(__file__)):sha(__file__)};gates={}
 for name in names:
  p=V/(name+'-current.json');g=read(p)
  assert g['status'].startswith('terminal_')and 'failed'not in g['status'],(name,g['status'])
  if name in counts:assert g['completed']==counts[name],name
  for f,h in g.get('source_sha256',{}).items():assert sha(f)==h,(name,f)
  deps.update(g.get('source_sha256',{}));deps[str(p)]=sha(p);save(out/(name+'.json'),g);gates[name]=g
 shared=gates['geometry-records-shared-observer-qualified-v1'];assert shared['ELF_C_functions']==52 and shared['C_floor_legal_controls']==shared['C_floor_rejected_controls']==624
 assert gates['geometry-records-record-observer-actual-CPU-reviewed-v2']['CPU_lanes']==64 and gates['geometry-records-fallback-alias-observers-actual-CPU-v1']['CPU_lanes']==704
 assert gates['geometry-records-geometry-observer-actual-CPU-v1']['CPU_lanes']==64 and gates['geometry-records-outer-observer-actual-CPU-v2']['CPU_lanes']==128
 assert gates['geometry-records-outer-observer-actual-CPU-v2']['boundary_pending_explicitly_verified']
 assert gates['geometry-records-reset-observer-qualified-v1']['actual_input_pairs']==64
 assert gates['geometry-records-commit-observer-qualified-v1']['controls']==2048
 assert len(gates['native-Deck-geometry-records-final-v1']['results'])==8 and all(x['exit_code']==0 for x in gates['native-Deck-geometry-records-final-v1']['results'].values())
 bp=V/'native-geometry-records-disc-build-v1-current.json';b=read(bp);assert sha(b['derived_disc'])==b['derived_disc_sha256'];parent=read(V/'native-Deck-coordinate-disc-build-current.json');text,_=monitor.observer_source(b,parent);observer=Path(gates['geometry-records-geometry-observer-qualified-v1']['observer']);assert observer.read_text()==text
 deps.update({str(p):sha(p)for p in [bp,Path(b['component']),Path(b['derived_stage']),Path(b['derived_disc']),observer,ROOT/'scripts/geometry_records_commit_observer_v1.inc.c',ROOT/'scripts/geometry_records_observer_build_v1.py',*ROOT.glob('scripts/shared_deck_geometry_records_*_observer_v1.py')]})
 save(out/'observer.c',text);save(out/'gate-map.json',{name:str(V/(name+'-current.json'))for name in names})
 proof=dict(status='terminal_v33_exact_component_alias_and_readonly_observers_qualified_for_fresh',directory=str(out),build=str(bp),build_sha256=sha(bp),observer=str(observer),observer_sha256=sha(observer),gate_names=names,counts=counts,shared_C_functions=52,read_only_actual_record_and_shared_CPU_lanes=768,actual_geometry_monitor_CPU_lanes=64,actual_outer_monitor_CPU_lanes=128,whole_scene_actual_inherited_provider_cases=772,record_commit_controls=2048,source_sha256=deps,new_predictions=0,new_training=False,whole_game_complete=False,fresh_gameplay_verified=False,scope='Finite CPU/RAM/MMIO/helper/fallback/alias and read-only observer qualification. Actual whole-scene provider comparison uses identical inherited providers with controlled mailbox inputs and synchronous originalGPU4320. Fresh asynchronous route,video/audio fidelity,whole-game rebuilding and console proof remain unverified.');save(out/'review.json',proof);save(V/'geometry-records-fresh-preflight-v1-current.json',proof);print(proof['status'],len(names),flush=True)
if __name__=='__main__':main()
