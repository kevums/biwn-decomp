"""Classify recorded runtime failures explicitly; source receipts are separate."""
import json
from datetime import datetime,timezone
from pathlib import Path
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
def main():
 paths={k:ROOT/'verification'/(v+'-current.json')for k,v in [('slow_deck','native-core-entry-selector-deck-pair'),('slow_route','native-core-format-long-route'),('slow_raw_control','native-core-raw-layout-control'),('inline_deck','native-fast-core-entry-selector-deck-pair'),('inline_route','native-fast-core-format-long-route')]}
 records=[];dependencies={str(Path(__file__)):sha(__file__)}
 for kind,p in paths.items():
  if not p.exists():records.append(dict(run=kind,status='no_terminal_receipt_yet'));continue
  state=json.loads(p.read_text());dependencies[str(p)]=sha(p);d=Path(state['directory'])
  lanes=['candidate','control']if kind.endswith('deck')else['control']if kind=='slow_raw_control'else['parent','core']if kind=='slow_route'else['parent','fast']
  for lane in lanes:
   reportp=d/lane/'report.json';report=json.loads(reportp.read_text());dependencies[str(reportp)]=sha(reportp);rows=report['frames'];bad=[v for v in rows if int(v['CPU'],16)&1]
   completed=state.get('results',{}).get(lane,{}).get('completed_outdoor_hold')
   verdict='runtime_failed_odd_CPU_PC'if bad else'finite_route_incomplete'if completed is False else'no_odd_PC_in_recorded_frames'
   records.append(dict(run=kind,lane=lane,status=verdict,executed_frames=report['executed_frames'],first_odd_PC_frame=bad[0]['frame']if bad else None,first_odd_PC=bad[0]['CPU']if bad else None,odd_PC_frames=len(bad),first_scene_change=report.get('scene_change_frame'),merchant_reached=state.get('results',{}).get(lane,{}).get('merchant_reached'),completed_outdoor_hold=completed,last_fields={k:rows[-1][k]for k in ['raw_player_X','raw_player_Z','scene_word','player_mode_word','floor_word','CPU']}))
 out=ROOT/'verification/native-formatter-runtime-sanity'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 proof=dict(status='terminal_recorded_formatter_runtime_sanity_classified',directory=str(out),records=records,source_and_component_checks_supersede_runtime_failure=False,all_scenarios_pass=all(row.get('status')=='no_odd_PC_in_recorded_frames'for row in records),default_promoted=False,whole_game_complete=False,dependencies_sha256=dependencies,scope='Read-only analysis of per-frame retained68000PC. Odd instructionPC is a definitive runtime failure signal here; absence is not proof of fullCPU/game equivalence. Route-completion booleans reported separately. As-run runners labeled classified without these sanity gates, so a terminal receipt alone is not a gameplay pass. Control failure invalidates an equivalence/comparative-performance conclusion even when candidate has no observed oddPC.')
 save(out/'analysis.json',proof);save(ROOT/'verification/native-formatter-runtime-sanity-current.json',proof);print(json.dumps(records,indent=2))
if __name__=='__main__':main()
