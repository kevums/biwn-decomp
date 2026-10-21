"""Separate dispatch routing from selector success/failure counts in evidence."""
import json,shutil
from pathlib import Path
from datetime import datetime,timezone
from run_biwn_native_fast_gameplay_route import ROOT,sha,save

def main():
 v=ROOT/'verification';p=v/'current-biwn-latest-publication-current.json';d=json.loads(p.read_text());assert d['facts']['experimental_build']['resident_bytes']==26220;r=json.loads((v/'actor-move-integration-reviewed-current.json').read_text());o=r['candidate_observations'];assert o['interior_kind_entries']==[14,1]and o['interior_kind_successes']==[14,0]and o['interior_kind_failures']==[0,1]and o['interior_skips']==1 and o['ad_actor']==12 and o['ad_sprite']==1
 out=v/'current-biwn-latest-publication'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);shutil.copy2(p,out/'previous-publication.json');d['directory']=str(out);d['facts']['selector_outcomes']=dict(actor=dict(entry='0x10520',completed_calls=14,successes=14,failures=0),sprite=dict(entry='0x105da',completed_calls=1,successes=0,failures=1,skipped_failures=1),scope='Live selector outcomes only. The12actor/1sprite dispatch routes are different counts,not selector successes. Other selector failure/success/non-skipped outcomes remain component-only.');d['facts']['dispatcher_routing_counts']=dict(completed_calls=13,actor_routes=12,sprite_routes=1,pool_exhaustion_returns=0,scope='Routing counts only,not boolean return success/failure.');d['dependencies_sha256'].update({str(q):sha(q)for q in [Path(__file__),out/'previous-publication.json',Path(r['directory'])/'protocol.json']});save(out/'publication.json',d);save(p,d);print(json.dumps(dict(tested_disc=26220,actor_selector_successes=14,actor_dispatch_routes=12,binary_changed=False)))
if __name__=='__main__':main()
