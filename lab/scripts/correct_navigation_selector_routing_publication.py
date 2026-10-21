"""Use actual new-route selector/creation counts rather than inherited old counts."""
import copy,hashlib,json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save
V=ROOT/'verification'
def main():
 pointer=V/'current-biwn-latest-publication-current.json';prior=json.loads(pointer.read_text());jobp=V/'native-navigation-dynamic-candidate-current.json';job=json.loads(jobp.read_text());a=job['observations'];assert prior['facts']['experimental_build']['resident_bytes']==29876 and job['live_monitor_pass']
 assert a['interior_kind_successes']==[14,0]and a['interior_kind_failures']==[0,2]and a['interior_skips']==1
 assert a['ad_returns']==15 and a['ad_actor']==13 and a['ad_sprite']==2
 out=V/'current-biwn-latest-publication'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);save(out/'previous-publication.json',prior);snap=out/'snapshots';snap.mkdir();f=copy.deepcopy(prior['facts']);f['recorded_at']=datetime.now(timezone.utc).isoformat()
 f['selector_outcomes']['sprite'].update(skipped_failures=1,non_skipped_failures=1)
 f['selector_outcomes']['scope']='Live actor14successes; sprite2failures(1skip/1non-skipped). Routing15calls(13actors/2sprites) is a separate count. Sprite success and actor failures remain component-only.'
 f['dispatcher_routing_counts']=dict(completed_calls=a['ad_returns'],actor_routes=a['ad_actor'],sprite_routes=a['ad_sprite'],pool_exhaustion_returns=a['ad_full'],scope='Routing counts only,not selector boolean success/failure.')
 f['gameplay_comparison'].update(creation_dispatch_returns=a['ad_returns'],creation_actor_routes=a['ad_actor'],creation_sprite_routes=a['ad_sprite'],initializer_returns=a['ai_returns'],initializer_actual_helpers=a['ai_helper_returns'],sprite_creator_returns=a['sc_returns'],sprite_creator_actual_helpers=a['sc_helper_returns'],parent_context_checks=a['ad_context_checks'],initializer_context_checks=a['ai_context_checks'],sprite_context_checks=a['sc_context_checks'],creation_max_private_depth=a['ad_max_depth'],creation_min_task_headroom=a['ad_min_headroom'],creation_min_context_clearance=a['ad_min_context_clearance'],sprite_selection_skipped_failures=1,sprite_selection_non_skipped_failures=1)
 f['live_path_coverage']=f['live_path_coverage'].replace('spriteselector2skippedfailures','spriteselector2failures(1skipped/1non-skipped)')+' Dispatcher15returns(13actor/2sprite),initializer13returns/18helpers,spritecreator2returns/6helpers;allcontext/taskgatespass.'
 f['checked_current_summary']=f['checked_current_summary'].replace('sprite2skippedfailures','sprite2failures(1skipped/1non-skipped)')
 deps=dict(prior['dependencies_sha256'])
 for p in [Path(__file__),out/'previous-publication.json',jobp]:
  actual=sha(p)
  if p==jobp:
   target=snap/'candidate-job.json';shutil.copy2(p,target);p=target
  deps[str(p)]=actual
 for p,h in deps.items():assert sha(p)==h,p
 result=dict(prior,directory=str(out),recorded_at=f['recorded_at'],facts=f,dependencies_sha256=deps,scope=prior['scope']+' Selector/routing correction uses new actual20navigation/16selector/15creation observations; supersededpublication retained.')
 save(out/'publication.json',result);save(pointer,result);print(json.dumps(dict(resident_bytes=29876,selector_actor_successes=14,sprite_failures=2,sprite_skipped_failures=1,sprite_non_skipped_failures=1,dispatcher_routes=[13,2])))
if __name__=='__main__':main()
