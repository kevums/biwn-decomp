"""Add reviewed local component progress while preserving the v26 gameplay record."""
import shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def main():
    wp=V/'native-Deck-current-status-v1-current.json';wrapper=read(wp)
    for path,h in wrapper['dependencies_sha256'].items():assert sha(path)==h,path
    localptr=V/'local-scene-clear-worker-reviewed-v2-current.json';local=read(localptr)
    for path,h in local['dependencies_sha256'].items():assert sha(path)==h,path
    assert local['target_native_cases']==772 and local['accepted_complete_functions']==1
    assert not local['model_source_installed'] and not local['new_training']
    packet=read(wrapper['packet']);assert packet['native_scene_draw_progress']['profile']=='deck-shared-v26-scene-clear'
    out=V/'local-clear-native-progress-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'previous-wrapper.json',wrapper);save(out/'previous-status-packet.json',packet)
    packet['previous_local_scene_clear_development_progress']=packet['local_scene_clear_development_progress']
    packet['local_scene_clear_development_progress']=local
    for key in ['checked_current_summary','checked_answer','current_verified_route_summary']:
        packet[key]+=' Local clear v2: one unedited scaffolded body passes 256 host and 772 native component cases; outside the game image. Author 19.33 seconds, no training updates. Initial harness import failure corrected; raw records retained.'
    save(out/'current-status-packet.json',packet);save(out/'local-review.json',local)
    viewer=ROOT/'scripts/show_native_status_v2.py';shutil.copy2(viewer,out/viewer.name);shutil.copy2(__file__,out/'publisher-source.py')
    native=read(local['native_gate']);assert sha(local['native_payload'])==local['native_payload_sha256']
    deps={str(p):sha(p)for p in out.iterdir()if p.is_file()}
    deps.update(local['dependencies_sha256']);deps[str(localptr)]=sha(localptr)
    for p in [Path(local['native_gate']),Path(local['native_payload']),ROOT/'scripts/run_local_scene_clear_worker_v3.py']:
        deps[str(p)]=sha(p)
    pub=V/'local-clear-native-progress-v1-current.json';atomic(pub,dict(status='terminal_reviewed_unedited_local_clear_native_component_published',directory=str(out),report=local['report'],new_predictions=3,new_training=False,whole_objective_complete=False,dependencies_sha256=deps))
    wrapper.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**wrapper['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(wp,wrapper)
    for path,h in wrapper['dependencies_sha256'].items():
        source=Path(path);assert source.is_relative_to(ROOT);dest=P/'workbench'/source.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.is_file()or sha(dest)!=h:subprocess.run(['/bin/cp','-c',str(source),str(dest)],check=True,capture_output=True)
    shutil.copy2(wp,P/'workbench'/wp.relative_to(ROOT));shutil.copy2(viewer,P/'workbench'/viewer.relative_to(ROOT))
    # Preserve all native proof files at their declared relative location for copied evidence reading.
    original=Path(native['directory']);dest=P/'workbench'/original.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
    if not dest.exists():subprocess.run(['/bin/cp','-cR',str(original),str(dest)],check=True,capture_output=True)
    print('Local clear native component published; game image and preview unchanged.',flush=True)
if __name__=='__main__':main()
