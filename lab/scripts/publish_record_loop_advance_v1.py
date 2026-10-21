"""Publish measured coordinator prototype beside unchanged v34 gameplay."""
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_geometry_records_progress_v1 import clone

def main():
    names=['record-strides-first-scene-profile-reviewed-v1','geometry-records-native-loop-advance-cost-v1','scene17-geometry-records-loop-advance-bridge-v1','geometry-records-loop-advance-copied-rebuild-v1','record-loop-advance-all-words-v2','local-record-loop-advance-v1','local-record-loop-compile-v1']
    gates={n:read(V/(n+'-current.json'))for n in names};deps={str(Path(__file__)):sha(__file__)}
    for n,g in gates.items():
        assert g['status'].startswith('terminal_')
        for path,h in g.get('source_sha256',{}).items():assert sha(path)==h,path
        deps.update(g.get('source_sha256',{}));p=V/(n+'-current.json');deps[str(p)]=sha(p)
    body=gates[names[1]];scene=gates[names[2]];copied=gates[names[3]];wide=gates[names[4]];author=gates[names[5]]
    assert body['completed']==512 and scene['completed']==772 and copied['bytes']==54060 and wide['total_cases']==131072
    assert body['payload_sha256']==scene['payload_sha256']==copied['sha256']
    assert body['maximum_C_stack_bytes']==112 and scene['maximum_C_stack_bytes']==168
    assert author['new_predictions']==1 and author['seconds']==16.92 and gates[names[6]]['exit_code']!=0
    old=read(V/'geometry-records-native-stride-cost-v1-current.json');current={x['case']:x for x in body['cases']};savings=[]
    for row in old['cases']:
        new=current[row['case']];assert row['original_CPU_cycles']==new['original_CPU_cycles']
        savings.append(dict(case=row['case'],old_native_CPU_cycles=row['native_CPU_cycles'],new_native_CPU_cycles=new['native_CPU_cycles'],cycles_saved=row['native_CPU_cycles']-new['native_CPU_cycles'],old_native_instructions=row['native_instructions'],new_native_instructions=new['native_instructions']))
    assert min(x['cycles_saved']for x in savings)==6304 and max(x['cycles_saved']for x in savings)==6612
    deps[str(V/'geometry-records-native-stride-cost-v1-current.json')]=sha(V/'geometry-records-native-stride-cost-v1-current.json')
    out=V/'record-loop-advance-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    report=ROOT/'reports/BIWN Record Loop Advance Prototype Review.txt'
    facts=dict(status='terminal_coordinator_record_loop_prototype_native_scene_wide_words_and_copied_build_pass_unpromoted',directory=str(out),report=str(report),profile='deck-shared-v37-record-loop-advance-v1',parent_profile='deck-shared-v34-record-strides-v1',artifact_type='coordinator_source_component_prototype_not_disc_image',authorship='Coordinator-authored fused ADDQ/CMPI/SLE native loop-tail helper and integration. Local Author output failed strict compilation and is not used. Earlier linked hybrid attribution retained.',
        entry='0x170a0',new_unique_original_functions=0,new_internal_readable_helper_integrations=0,
        host_cases_new=0,baseline_host_fixture_cases=512,baseline_host_fixture_guards=19,native_body_cases=512,prototype_scene_cases=772,all_lowword_helper_cases=131072,
        module_bytes=54060,module_bytes_saved_relative_v34=74,body_C_stack_bytes=112,parent_body_C_stack_bytes=120,connected_C_stack_bytes=168,C_stack_reserved=208,
        copied_prototype_module_byte_identical=True,cost_fixture_count=8,cost_samples=savings,CPU_cycles_saved_min=6304,CPU_cycles_saved_max=6612,
        cost_scope='Sum of emulator m68k_execute return cycles including actual pinned original copy/matrix/wait CPU providers;GPU execution excluded. Boundary differences to original remain. Eight same-seed comparisons to v34,not fresh gameplay or physical speed.',
        source_body=str(ROOT/'projects/black-ice-white-noise/restoration/experimental/coordinator-record-loop-advance-v1/coordinator-reference.inc'),
        native_helper=str(ROOT/'projects/black-ice-white-noise/restoration/experimental/coordinator-record-loop-advance-v1/model-native-advance.inc'),
        new_disc_built=False,candidate_disc=None,model_source_installed=False,new_training=False,optimizer_updates=0,actual_predictions_for_this_source=0,
        separate_local_Author_predictions=1,separate_local_Author_seconds=16.92,separate_local_Author_compile_pass=False,separate_local_Repair_predictions=0,separate_local_Repair_status='prepared_not_running_shared_model_slot_was_busy',
        fresh_gameplay_verified=False,installed_preview_changed=False,whole_game_complete=False,game_fidelity_verified=False,
        next_action='Qualify retained callers,geometry,exact-image/startup/heap/bus/fallback/aliases/observers and copied final build before new-disc/fresh evaluation. Preserve v34 gameplay and separate localv35component. Retry prepared local Repair only after a verified shared-slot availability change;do not replay failed Author. Continue whole-game CPU/GPU/DSP/HLE recovery,audio/IRQ/fidelity,same-console rebuilding and useful training quality.')
    report.write_text('BIWN — fused record-loop tail prototype\n\n'
        'Read-only first-scene profiling uses identical public entry and caller return. Native23929/original14359instruction-observer callbacks;record body6166/706. Root busywait4496/4497iterations is not the main excess. Both profile runs preserve every earlier1000frameCPU/RAM/GPU/DSP/video hash. Callback counts are not cycle costs.\n\n'
        'The coordinator fused each ADDQ.W #1,D3 / CMPI.W #39,D3 / BLE tail using actual68000 flags and SLE while preserving logicalD3upper bits,SRupper bits,and ADD-produced X. This coordinator source is distinct from the local Author. Native512cases match original logicalCPU/banks,all nonprivateRAM,helper states and scoped public-bus order. Connected772scene cases match using pinned originalcopy/matrix/waitCPU providers and synchronousoriginalGPU4320;other mailbox fixtures remain controlled. Wide helper probe131072cases covers everylowD3word in bothphysicalstackbanks,varied upperD3/all2048logicalupperSR/all32CCR patterns,with independent arithmetic flags and128bytecontextcanaries. Patterns are correlated,not fullCartesian. Initial wide-probe v1 exhausted its one-billion-cycle driver bound;v2 records progress and completes with a five-billion bound. Neither source nor expected results were changed to pass it.\n\n'
        'Prototype module54060bytes,74smaller thanv34. Recordbody Cstack112versus120bytes;connectedscene168/208unchanged. CopiedSDK build is byte-identical. Eight matching cost fixtures save6304–6612emulatorCPUcycles and1310–1321instructionsteps each versusv34. GPUtime excluded;no fresh-frame or physical speed improvement is established.\n\n'
        'One actuallocalAuthor prediction completed16.92seconds. Its function failed strict unused-variable checking and diagnostic assembly constraints;its uninitializedoperand/branch-register/MOVEC issues are preserved. No model statements were edited into passing code. One intendedRepair prompt is saved;two launch attempts generated zero predictions because another job held the shared lease. No unrelated model/job was changed. Zerooptimizerupdates. This is scaffolded development,not untouched-task evaluation or a trained-model quality gain.\n\n'
        'The latest gameplay disc remainsv34with standard route25012/24966,additional scene268matrix190native/266original-record returns,and450video differences in the current1000frame equal-input prefix. v37is a prototype with no disc/final-layout/retained/alias/observer/freshqualification. The older localv35prologue remains a separately verified unpromotedcomponent. Preview unchanged;fullgame/audio/IRQ/console/source-only rebuild and useful training remain incomplete.\n\n'+facts['next_action']+'\n\nExact local Author transcript: '+str(Path(author['directory'])/'prompts-and-responses.txt')+'\nPrepared Repair: '+str(V/'local-record-loop-Repair-prepared-v1.json')+'\n')
    save(out/'facts.json',facts);save(out/'cost-comparisons.json',savings)
    for p in [V/'local-record-loop-Repair-prepared-v1.json',Path(gates[names[6]]['directory'])/'diagnostic-compiler.log',V/'record-loop-advance-all-words-v1-current.json']:
        deps[str(p)]=sha(p)
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for path,h in w['dependencies_sha256'].items():assert sha(path)==h,path
    packet=read(w['packet']);save(out/'before-packet.json',packet)
    packet['previous_latest_source_development_before_v37']=packet['latest_source_development']
    packet['native_geometry_record_loop_progress']=packet['latest_source_development']=facts
    packet['native_scene_draw_progress']['record_loop_prototype_progress']=facts
    packet['native_scene_draw_progress']['first_scene_instruction_profile']={k:v for k,v in gates[names[0]].items()if k!='source_sha256'}
    packet['local_record_loop_Author_progress']={k:v for k,v in author.items()if k!='source_sha256'}
    packet['local_record_loop_Author_progress'].update(strict_compile_pass=False,model_source_installed=False,repair_predictions=0,repair_status='prepared_not_running_shared_model_slot_was_busy')
    packet['checked_current_summary']+=' Newer coordinatorv37loop-tail prototype:module54060bytes(74less),body stack112/scene168of208,native512/connected772/widehelper131072/copiedbuildpass. Eight matching fixtures save6304–6612emulatorCPUcycles,GPUtimeexcluded. Not a disc or fresh-gameplay result;v34 remains latest gameplay. One separatelocalAuthor16.92seconds failed strictcompile;preparedRepair haszero predictions due sharedleasebusy. No model source adoption or optimizerupdates.'
    packet['checked_answer']=packet['checked_current_summary'];packet['recorded_at']=datetime.now(timezone.utc).isoformat()
    packet['current_status_renderer']='show_native_status_v9.py';packet['portable_entry_version']=18
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False,current_source_factual_claims_reviewed=False)
    save(out/'current-status-packet.json',packet)
    for name in ['show_native_status_v9.py','portable_biwn_entry_v18.py']:
        p=ROOT/'scripts'/name;deps[str(p)]=sha(p)
    deps[str(report)]=sha(report);deps.update({str(p):sha(p)for p in out.iterdir()if p.is_file()})
    for path in deps:
        assert Path(path).is_relative_to(ROOT),path
        clone(Path(path),P/'workbench'/Path(path).relative_to(ROOT))
    clone(ROOT/'scripts/portable_biwn_entry_v18.py',P/'workbench/portable_biwn.py')
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps});atomic(wp,w);clone(wp,P/'workbench/verification'/wp.name)
    save(V/'record-loop-advance-reviewed-v1-current.json',dict(status=facts['status'],directory=str(out),report=str(report),facts=str(out/'facts.json'),new_predictions=0,new_training=False))
    for root in [ROOT,P/'workbench']:(root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
    print('Published coordinatorv37prototype;v34gameplay and preview unchanged.',flush=True)

if __name__=='__main__':main()
