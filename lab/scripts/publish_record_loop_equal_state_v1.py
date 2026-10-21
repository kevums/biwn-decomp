"""Deliver bounded diagnostic evidence without altering failed acceptance gates."""
from datetime import datetime, timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT, V, P, read, save, sha, atomic
from publish_geometry_records_progress_v1 import clone


def main():
    rp=V/'record-loop-equal-state-reviewed-v3-current.json';r=read(rp)
    assert r['actual_recovered_C_integrator_transitions']==627 and r['unchanged_replicas_exact']
    for path,digest in r['source_sha256'].items():assert sha(path)==digest,path
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,digest in w['dependencies_sha256'].items():assert sha(path)==digest,path
    out=V/'record-loop-equal-state-delivered-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    p=read(w['packet']);save(out/'before-packet.json',p)
    assert p['latest_native_candidate']['native_record_returns']==4777
    pending=p['pending_native_candidate'];assert not pending['default_promoted'] and not pending['final_matrix_video_comparison_pass']
    assert pending['matrix_route']['final_differing_pixels']==22858
    assert p['current_copied_Reader_progress']['default_reader_version']==43
    evidence={k:v for k,v in r.items()if k!='source_sha256'}
    evidence.update(review=str(rp),scope='Twelve restored-snapshot diagnostic lanes,not fresh gameplay. Native/original stationary pixels agree at each of two distinct poses;fixed Up-input reveals different world-update cadence and22versus23movementsteps in one origin. Actual recovered C integration matches627captured transitions. No pose/timer normalization;code-only ten-byte scene-entry intervention. Fixed180-frame cuts may leave one scene call active. Failed fresh-matrix comparison is not waived;cause of that specific route remains unresolved.')
    p['current_equal_state_diagnostic_progress']=evidence
    p['current_copied_Reader_progress']['new_diagnostic_facts_not_in_saved_briefing']=True
    p['current_default_Reader_progress']['entry_source']=str(ROOT/'scripts/portable_biwn_entry_v24.py')
    p['checked_current_summary']+=' Equal-state saved diagnostics show stationary video equality at both poses;fixed Up input changes movement cadence and22/23step count at one origin. Existing C integration matches627captured transitions. This narrows diagnosis without passing the failed fresh matrix gate.'
    p['checked_answer']=p['checked_current_summary'];p['recorded_at']=datetime.now(timezone.utc).isoformat()
    save(out/'current-status-packet.json',p)
    report=ROOT/'reports/BIWN v37 Equal State Diagnosis and Local Reader43.txt'
    report.write_text('BIWN — current work\n\n'
        'The reviewed gameplay baseline remains v34. The newer built v37 image passed its23component/provider/observer prerequisites and the standard fresh route,but its additional matrix-route final video differs22858pixels;it remains unpromoted. The Desktop outdoor checkpoint preview is unchanged.\n\n'
        +Path(r['report']).read_text()+'\n\nLOCAL INFERENCE\n'
        'Ordinary copied-package Reader43 is now installed as default. One actual99-word,two-paragraph reply passed supplied-snapshot factual,byte-unit,artifact and causal-scope review. Warm CLI firsttext18.94seconds,completion25.18seconds including setup/evidence;generation8.27seconds. Earlier Reader41/42 replies remain rejected and saved. All three exact prompts/raw responses are appended to the frozen Root/copied indices(199/200records). This is prompt/evidence workflow improvement,not new weight training or heldout quality. Native LM Studio Chat display of this result remains unverified.\n\n'
        'Latest local code Author16.92seconds and Repair19.48seconds produced the same failed candidate;neither was adopted. Current loop source is coordinator-authored,with earlier linked hybrid attribution retained. Zero new optimizer updates;earlier base and adapter pilot scores each0/4. Full readable CPU/GPU/DSP/HLEsource-only same-console rebuilding,audio/IRQ/wider fidelity,useful training gain and future256GBhardware capacity remain unfinished.\n\n'
        'DIAGNOSTIC EVIDENCE\n'+str(rp)+'\nREADER REVIEW\n'+str(V/'copied-Reader43-reviewed-v1-current.json')+'\n')
    deps={str(Path(__file__)):sha(__file__),str(rp):sha(rp),**r['source_sha256'],str(report):sha(report)}
    # Preserve reviewer harness failures without replaying any completed game lane.
    for source in [ROOT/'scripts/review_record_loop_equal_state_v1.py',ROOT/'scripts/review_record_loop_equal_state_v2.py',V/'record-loop-equal-state-review-v1-failure.json',
                   ROOT/'scripts/append_reader41_43_model_index_v1.py',V/'Reader41-43-model-index-append-v1-current.json']:
        deps[str(source)]=sha(source)
    for version in [41,42]:
        trial=read(V/f'copied-Reader{version}-rejected-v1-current.json')
        for source in Path(trial['directory']).rglob('*'):
            if source.is_file():deps[str(source)]=sha(source)
    for source in [ROOT/'scripts/show_native_status_v11.py',ROOT/'scripts/portable_biwn_entry_v24.py']:
        deps[str(source)]=sha(source);clone(source,P/'workbench/scripts'/source.name)
    clone(P/'workbench/portable_biwn.py',out/'before-portable_biwn.py')
    clone(ROOT/'scripts/portable_biwn_entry_v24.py',P/'workbench/portable_biwn.py')
    deps.update({str(x):sha(x)for x in out.iterdir()if x.is_file()})
    for path,digest in deps.items():
        source=Path(path);assert source.is_relative_to(ROOT)and sha(source)==digest,path
        clone(source,P/'workbench'/source.relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps})
    atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:
        (root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    save(V/'record-loop-equal-state-delivered-v1-current.json',dict(status='terminal_equal_state_diagnostic_published_v34_retained_v37_fresh_gate_failed',
         directory=str(out),report=str(report),new_predictions=0,new_training=False,new_fresh_routes=0,gameplay_promoted=False))
    print('Diagnostic delivered;Reader43 retained;v37 fresh gate remains failed.',flush=True)


if __name__=='__main__':main()
