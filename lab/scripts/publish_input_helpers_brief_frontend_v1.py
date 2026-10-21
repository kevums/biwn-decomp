"""Install a concise default status view without changing game/model results."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone


def main():
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,digest in w['dependencies_sha256'].items():assert sha(path)==digest,path
    packet=read(w['packet']);h=packet['current_input_real_helpers_progress']
    assert h['animation_fixture_cases']==318 and h['camera_fixture_cases']==78
    out=V/'input-helpers-brief-frontend-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'before-packet.json',packet)
    packet['current_default_Reader_progress']['entry_source']=str(ROOT/'scripts/portable_biwn_entry_v30.py')
    packet['current_status_frontend_progress']=dict(status='concise_default_view_prepared_actual_transport_checks_pending',
        renderer=str(ROOT/'scripts/show_native_status_v17.py'),portable_entry_version=30,default_brief_lines=12,
        new_predictions=0,game_or_model_results_changed=False,detailed_report=h['report'])
    packet['recorded_at']=datetime.now(timezone.utc).isoformat();save(out/'current-status-packet.json',packet)
    clone(P/'workbench/portable_biwn.py',out/'before-portable_biwn.py')
    clone(ROOT/'scripts/portable_biwn_entry_v30.py',P/'workbench/portable_biwn.py')
    deps={str(Path(__file__)):sha(__file__)}
    for name in ['show_native_status_v17.py','portable_biwn_entry_v30.py']:
        path=ROOT/'scripts'/name;deps[str(path)]=sha(path)
    deps.update({str(path):sha(path)for path in out.iterdir()if path.is_file()})
    for path,digest in deps.items():
        source=Path(path);assert sha(source)==digest;clone(source,P/'workbench'/source.relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps})
    atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    atomic(V/'input-helpers-brief-frontend-v1-current.json',dict(status='terminal_concise_frontend_installed_checks_pending',directory=str(out),dependencies_sha256=deps))
    print('Concise status17/portable entry30 installed;game/model results unchanged.',flush=True)


if __name__=='__main__':main()
