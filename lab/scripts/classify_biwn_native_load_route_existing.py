"""Classify saved terminal route outputs, retaining an unmet gameplay coverage gate."""
from pathlib import Path
from datetime import datetime,timezone
import json,shutil
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 p=ROOT/'verification/native-load-route-active.json';s=json.loads(p.read_text());assert s['status']=='terminal_failed'and s.get('exit_codes')=={'native26_repaired':0,'native28_repaired':0};out=Path(s['directory'])
 save(out/'original-postrun-failure.json',s);shutil.copy2(ROOT/'scripts/run_biwn_native_load_route.py',out/'route-driver-as-run.py');results={};unmet={}
 for lane in s['lanes']:
  path=out/lane/'report.json';d=json.loads(path.read_text());obs=json.loads((out/lane/'gameplay-observation.json').read_text());rows=d['frames'];last=rows[-1]
  assert not(obs['errors']or obs['copy_errors']or obs['repair_code_errors']);assert obs['native_C_resource_release_calls']==obs['resource_release_entries']
  if lane=='native28_repaired':assert obs['native_C_loader_calls']==obs['loader_entries']>0 and obs['old_loader_body_steps']==obs['loader_task_stack_outside']==0 and obs['native_C_acquire_calls']==obs['acquire_entries']>0
  returned=[x for x in rows if(x.get('navigation')or{}).get('return_started')]
  merchant=any(x['player_mode_word']==2 and x['floor_word']==2 and x['scene_word']==314 and abs(x['raw_player_X']-12832)<=16 and abs(x['raw_player_Z']-42385)<=16 for x in rows)
  hold=last['player_mode_word']==1 and(last.get('navigation')or{}).get('outdoor_hold',0)>=120
  results[lane]=dict(executed_frames=d['executed_frames'],first_scene_change=d['scene_change_frame'],merchant_reached=merchant,nonzero_audio_samples=d['audio']['nonzero_samples'],return_floor_values=sorted({x['floor_word']for x in returned}),completed_outdoor_hold=hold,final_fields={k:last[k]for k in ['raw_player_X','raw_player_Z','player_mode_word','floor_word','scene_word']},last_navigation=last.get('navigation'),observation=obs,report_sha256=sha(path))
  unmet[lane]=dict(merchant_not_reached=not merchant,outdoor_hold_not_completed=not hold,resource_release_path_not_exercised=obs['resource_release_entries']==0)
 s.update(status='terminal_fresh_native26_native28_load_routes_classified',results=results,unmet_gameplay_coverage=unmet,original_postrun_assertion_failure='Requiredpositive resource-release coverage notmet infailednative28route; retained asunmetcoverage, notconverted togameplaypass.',saved_output_classification_driver_sha256=sha(__file__),finished_at=datetime.now(timezone.utc).isoformat());save(out/'protocol.json',s);save(p,s);save(ROOT/'verification/native-load-route-current.json',s);print('Classified saved outputs; gameplay failures retained',unmet,flush=True)
if __name__=='__main__':main()
