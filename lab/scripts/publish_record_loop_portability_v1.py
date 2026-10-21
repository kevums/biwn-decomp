"""Publish C99-portable v2 with explicit inherited native-byte qualifications."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
    names=['record-loop-portable-label-fix-v1','geometry-record-loop-host-v2','geometry-record-loop-host-v1-failed','native-deck-retained-record-loop-advance-v1','native-record-loop-advance-profile-v1','geometry-records-loop-advance-copied-rebuild-v2']
    gates={n:read(V/(n+'-current.json'))for n in names};deps={str(Path(__file__)):sha(__file__)}
    for n,g in gates.items():
        for path,h in g.get('source_sha256',{}).items():assert sha(path)==h,path
        deps.update(g.get('source_sha256',{}));p=V/(n+'-current.json');deps[str(p)]=sha(p)
    fix,host,failed,retained,geometry,copied=[gates[n]for n in names]
    assert fix['v1_native_module_byte_identical'] and host['completed']==512 and host['host_guards']==19
    assert retained['completed']==4992 and retained['fallback_cases']==16 and geometry['completed']==256
    assert fix['payload_sha256']==retained['payload_sha256']==geometry['payload_sha256']==copied['sha256']
    assert copied['bytes']==54060 and geometry['maximum_C_stack_bytes']==164
    oldhelper=ROOT/'projects/black-ice-white-noise/restoration/experimental/coordinator-record-loop-advance-v1/model-native-advance.inc'
    helper=ROOT/'projects/black-ice-white-noise/restoration/experimental/coordinator-record-loop-advance-v2/model-native-advance.inc';assert sha(helper)==sha(oldhelper)
    out=V/'record-loop-portability-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,h in w['dependencies_sha256'].items():assert sha(path)==h,path
    packet=read(w['packet']);save(out/'before-packet.json',packet);previous=packet['latest_source_development'];assert previous['profile']=='deck-shared-v37-record-loop-advance-v1'
    facts=dict(previous);facts.update(status='terminal_portable_coordinator_loop_prototype_host_native_scene_retained_geometry_copied_pass_unpromoted',profile='deck-shared-v37-record-loop-advance-v2',directory=str(out),host_cases_new=512,host_cases=512,host_guards=19,retained_caller_cases=4992,retained_fallback_cases=16,geometry_cases=256,geometry_C_stack_bytes=164,
        native_qualifications_inherited_by_full_module_byte_identity=True,native_case_count_inherited_by_byte_identity=512,scene_case_count_inherited_by_byte_identity=772,
        helper_wide_cases_inherited_by_identical_source_and_native_module=True,
        v1_host_C99_compile_failed=True,v2_host_C99_compile_pass=True,native_module_byte_identical_to_v1=True,
        source_body=str(ROOT/'projects/black-ice-white-noise/restoration/experimental/coordinator-record-loop-advance-v2/coordinator-reference.inc'),native_helper=str(helper),
        scope='v2adds only null statements after two labels so strictC99host compilation succeeds. At the same prototype code/arena addresses,full54060byte native module and helper source are identical to v1. Native512,scene772,widehelper131072 and retained4992/geometry256 machine-code qualifications therefore apply by identity,not rerun claims. Host512+19 execute new portable C source. Copiedv2SDK also produces identical54060bytes. No deployed-image,alias/observer/fresh/IRQ/whole-game proof.',
        next_action='Build a separate candidate after verifying these prototype gates,then run all exact-address component/startup/heap,provider,fallback/alias/connected/observer and copied-final gates before fresh testing. Do not rerun terminal prototype proofs. Keep v34gameplay/preview unchanged pending qualification;continue whole-game source,audio/IRQ/same-console rebuild,useful training and copied-weight Chat usability.')
    report=ROOT/'reports/BIWN Record Loop Portability and Retained Callers Review.txt';facts['report']=str(report)
    report.write_text('BIWN — portable loop-tail prototype and retained callers\n\n'
        'The new source version fixes two labels that strictC99 requires to precede a statement. Empty statements change no intended behavior. The first host compile failure and original source are retained. v2now passes512host cases and19guards,including completeCPU/banks/RAM,ordered bus and real nested copy/matrix provider comparisons.\n\n'
        'The full native module at prototype addresses is byte-identical to v1,54060bytes. Its native512record and772connected-scene qualifications transfer by exact binary identity;the131072all-lowword helper cases also transfer through identicalhelper source/machine bytes. These are inherited results,not new executions of those test suites. Retained4992cases+16fallbacks and geometry256with actual text/formatter/blitter dependencies now pass on that same payload. Copiedv2SDK build is byte-identical. Record Cstack112bytes,scene168/208,geometry164/176.\n\n'
        'The loop-tail prototype saves74modulebytes and6304–6612emulatorCPUcycles in eight matched fixtures againstv34;GPUtimeexcluded. No new disc/deployedlayout/heap/alias/read-onlyobserver/freshgameplay qualification yet. The current gameplay image remainsv34;the installed preview is unchanged.\n\n'
        'This passing helper is coordinator-authored. One localAuthor took16.92seconds and failed strictcompile;no localcode was silently repaired or adopted. A Repair prompt is prepared but its two launch attempts madezero predictions due the sharedmodellease. No optimizerupdates or useful training-quality gain. Exact inputs/output are appended to the saved model-work index.\n\n'+facts['next_action']+'\n')
    packet['previous_latest_source_before_C99_portability_fix']=previous
    packet['native_geometry_record_loop_progress']=packet['latest_source_development']=facts
    packet['native_scene_draw_progress']['record_loop_prototype_progress']=facts
    packet['checked_current_summary']+=' Loop prototype sourcev2now passes strictC99host512+19guards;two null label statements preserve the entire54060byte native module. Native512/scene772/widehelper131072 transfer by exact identity. Retained4992+16fallback and actualdependencygeometry256 pass;copiedv2buildmatches. These remain prototype-address results,no new disc/heap/freshclaim.'
    packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat();save(out/'facts.json',facts);save(out/'current-status-packet.json',packet)
    deps[str(report)]=sha(report);deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()})
    for path in deps:assert Path(path).is_relative_to(ROOT),path;clone(Path(path),P/'workbench'/Path(path).relative_to(ROOT))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    save(V/'record-loop-portability-reviewed-v1-current.json',dict(status=facts['status'],directory=str(out),facts=str(out/'facts.json'),report=str(report),new_predictions=0,new_training=False))
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    print('Portable v2host512+19,retained4992+16,geometry256;nativebytes unchanged.',flush=True)

if __name__=='__main__':main()
