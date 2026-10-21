"""Publish measured service work with its explicit unequal boundaries."""
import shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
def main():
 manifest=V/'native-Deck-current-status-v1-current.json';w=read(manifest)
 for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
 gp=V/'scene-reset-input-cost-v1-current.json';g=read(gp)
 for p,h in g['source_sha256'].items():assert sha(p)==h,p
 assert g['completed']==8 and g['reset_pairs']==4
 rows=read(Path(g['directory'])/'cases.json');out=V/'scene-reset-cost-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
 save(out/'cost-proof.json',g);save(out/'cases.json',rows);packet=read(w['packet']);save(out/'before-packet.json',packet)
 s=dict(packet['native_scene_reset_progress']);s.update(cost_measured=True,cost_approved=False,sampled_reset_service_cycles=1760,original_reset_body_cycles=612,cost_sample_pairs=8,cost_reset_pairs=4,reset_cost_boundary_scope='Pinned emulator:original27instruction reset body excludes RTS;compiled dispatcher includes guard,marker,Creturn. Includes service overhead;not isolated Cbody or full-game timing.',input_caller_sample_cycle_deltas=[x['costs']['compiled']['cycles']-x['costs']['original']['cycles']for x in rows])
 s['scope']+=' Eight pinned emulator input samples now measure4reset services at1760cycles versus612originalbody cycles with explicitly different boundaries;not a physical/fresh isolated cost claim.'
 report=ROOT/'reports/Scene Reset Service Cost Review.txt';report.write_text('BIWN reset service cost — exact final-image samples\n\n'
  'Eight original/native input pairs retain matchingCPU,nonarenaRAM and helper entries. Four reset pairs cover both stack modes;four no-reset pairs provide controls. Each original reset body uses612pinned-emulatorcycles;the compiled reset service uses1760. Original stops beforeRTS;compiled includes dispatcher guard,marker andCreturn. This ratio includes service overhead and is not a like-for-like isolated Cbody or physical-console benchmark.\n\n'
  'Whole input samples cost11156..16544additional emulatorcycles in the compiled lane,with other input helper effects declared and their execution cost omitted. The reset-service excess alone is1148cycles per observed reset;these component measurements do not attribute the fresh2/1frame shifts to a specific cause. Cost remains unapproved. No game,model or training rerun;the8newCPUcomponentpairs are the only execution for this measurement.\n\n'+str(out/'cost-proof.json')+'\n')
 s['cost_review']=str(report);packet['native_scene_reset_progress']=packet['latest_source_development']=s;packet['latest_native_candidate']['next_action']='Resolve input bridge/caller timing and video differences,including the measured component input overhead,without assuming reset alone caused fresh frame shifts. Continue silent-audio investigation and remaining CPU/GPU/DSP recovery/same-console whole-game rebuilding. Unedited local reset outputs still need full-module/image qualification. Copied-weight nativeChat and useful trained-model quality remain unproven.'
 packet['latest_fresh_reviewed_candidate']=packet['latest_native_candidate'];save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'publisher-source.py')
 deps={str(p):sha(p)for p in out.rglob('*')if p.is_file()};deps.update(g['source_sha256']);deps[str(report)]=sha(report);deps[str(gp)]=sha(gp)
 pub=V/'scene-reset-cost-reviewed-v1-current.json';atomic(pub,dict(status='terminal_scene_reset_cost_scoped_review',directory=str(out),report=str(report),facts=str(out/'cost-proof.json'),new_predictions=0,new_training=False,dependencies_sha256=deps))
 w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(manifest,w)
 index=ROOT/'config/current-model-work-sources.json';items=read(index);items=[x for x in items if x[0]!=pub.name];items.append([pub.name,'BIWN reset service cost with explicit original-body/dispatcher boundaries']);atomic(index,items)
 for p,h in w['dependencies_sha256'].items():
  src=Path(p);assert src.is_relative_to(ROOT);dest=P/'workbench'/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.is_file()or sha(dest)!=h:subprocess.run(['/bin/cp','-c',str(src),str(dest)],check=True,capture_output=True)
 shutil.copy2(manifest,P/'workbench/verification'/manifest.name);shutil.copy2(index,P/'workbench/config'/index.name)
 print('Published reset/input cost measurement;approval remains false')
if __name__=='__main__':main()
