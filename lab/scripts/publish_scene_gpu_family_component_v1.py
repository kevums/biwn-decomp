"""Publish v30 integration evidence while retaining v29 as the latest reviewed game run."""
import shutil,subprocess
from datetime import datetime,timezone
from pathlib import Path
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def clone(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.is_file() or sha(src)!=sha(dst):
        subprocess.run(['/bin/cp','-c',str(src),str(dst)],check=True,capture_output=True)

def main():
    counts={'scene-gpu-command-family-host-v1':768,'scene-gpu-command-family-native-v1':768,
            'native-deck-retained-scene17-gpu-family-v1':4992,'native-geometry-scene17-gpu-family-v1':256,
            'scene17-gpu-family-bridge-v2':772,'scene17-gpu-family-final-bridge-v1':772,
            'scene-gpu-family-final-native-v1':1153,'scene17-gpu-family-final-fallback-v1':384,
            'scene17-gpu-family-final-reentry-v1':64,'scene17-gpu-family-final-public-bus-v1':14,
            'scene17-gpu-family-final-input-face-alias-v1':256,
            'native-deck-alias-nesting-scene17-gpu-family-final-v1':256,
            'native-scene17-gpu-family-geometry-alias-v1':128,
            'native-Deck-outer-connected-scene17-gpu-family-v1':128}
    more=['native-Deck-scene17-gpu-family-final-v1','scene17-gpu-family-final-copied-rebuild-v1',
          'scene17-gpu-family-shared-observer-qualified-v1','scene17-gpu-family-shared-observer-actual-CPU-v2',
          'scene17-gpu-family-geometry-observer-qualified-v1','outer-scene17-gpu-family-geometry-observer-qualified-v1',
          'shared-Deck-region-check-scene17-gpu-family-v1','scene17-gpu-family-observer-actual-CPU-v1',
          'scene17-gpu-family-reset-observer-qualified-v1','scene17-gpu-family-commit-observer-v1',
          'scene17-gpu-family-clear-commit-observer-v1']
    out=V/'scene-gpu-family-component-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    dependencies={str(Path(__file__)):sha(__file__)};gates={}
    for name in [*counts,*more]:
        pointer=V/(name+'-current.json');gate=read(pointer)
        assert gate['status'].startswith('terminal_') and 'failed'not in gate['status'],name
        if name in counts:assert gate['completed']==counts[name],name
        for p,h in gate.get('source_sha256',{}).items():assert sha(p)==h,p
        dependencies.update(gate.get('source_sha256',{}));dependencies[str(pointer)]=sha(pointer)
        save(out/(name+'.json'),gate);gates[name]=gate
    driver=gates['native-Deck-scene17-gpu-family-final-v1'];assert len(driver['results'])==8
    assert all(x['exit_code']==0 for x in driver['results'].values())
    shared=gates['scene17-gpu-family-shared-observer-actual-CPU-v2'];assert shared['CPU_lanes']==512
    bridge=gates['scene17-gpu-family-final-bridge-v1'];assert bridge['maximum_C_stack_bytes']==168
    bp=V/'native-scene17-gpu-family-disc-build-v1-current.json';b=read(bp)
    assert b['shared_Deck_code_bytes']==48738 and b['initial_heap_bytes']==120320
    payload=Path(bridge['payload']).read_bytes();resident=Path(b['component']).read_bytes()
    assert payload==resident[b['shared_Deck_code_address']-b['resident_address']:b['shared_Deck_code_address']-b['resident_address']+len(payload)]
    assert sha(b['derived_disc'])==b['derived_disc_sha256']
    dependencies[str(bp)]=sha(bp);dependencies.update(b['source_sha256'])
    previous_build=read(V/'native-scene17-direct-dispatch-disc-build-v1-current.json')
    stage=Path(b['derived_stage']).read_bytes();prior_stage=Path(previous_build['derived_stage']).read_bytes()
    baseline=(ROOT/'render-assets/biwn-inventory-baseline.bin').read_bytes();entry_audit=[]
    for a in [0xe098,0xe0a6,0xe0f2,0xe148,0xe19e,0xe202]:
        actual=stage[a-0x4000:a-0x4000+10];inherited=prior_stage[a-0x4000:a-0x4000+10]
        assert actual==inherited and actual[:2]==bytes.fromhex('4ef9') and actual!=baseline[a:a+10]
        entry_audit.append(dict(entry=hex(a),pinned_original_bytes=baseline[a:a+10].hex(),v29_and_v30_bytes=actual.hex(),inherited_JMP_target=hex(int.from_bytes(actual[2:6],'big')),new_v30_global_redirect=False))
    save(out/'global-entry-audit.json',dict(entries=entry_audit,original_global_entries_preserved=False,scope='Older metadata saying global helper redirects are absent does not describe these inherited GPU sites. V30 leaves the existing redirects unchanged. Its internal pure-original idle wait bypasses the inherited pending-command guard; no game compatibility result is inherited.'))
    dependencies[V.__str__()+'/native-scene17-direct-dispatch-disc-build-v1-current.json']=sha(V/'native-scene17-direct-dispatch-disc-build-v1-current.json')

    localp=V/'local-scene-gpu-family-reviewed-v1-current.json';local=read(localp)
    dependencies[str(localp)]=sha(localp);dependencies.update(local['dependencies_sha256'])
    for p,h in dependencies.items():assert sha(p)==h,p
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
    packet=read(w['packet']);save(out/'before-wrapper.json',w);save(out/'before-packet.json',packet)
    report=ROOT/'reports/BIWN Scene GPU Command Family Review.txt'
    action='Review the v30 fresh candidate/control route and fixed-input comparison without inheriting v29 fidelity claims. Continue geometry-record service170A0, remaining CPU/GPU/DSP/HLE source recovery and heap/code capacity work. Useful held-out training quality, copied-weight Native Chat usability, whole-game rebuilding and physical-console/audio fidelity remain open.'
    facts=dict(status='terminal_v30_gpu_CPU_family_image_components_and_observers_pass_fresh_review_pending',
        profile='deck-shared-v30-scene-gpu-commands-v1',directory=str(out),report=str(report),
        authored_source=str(ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-gpu-command-family-v1/coordinator-reference.inc'),
        authorship='Coordinator structured C; actual local Author/Repair outputs rejected and preserved.',
        new_unique_original_functions=0,new_internal_native_helper_integrations=6,
        native_CPU_helper_entries=['0xe098','0xe0a6','0xe0f2','0xe148','0xe19e','0xe202'],
        remaining_original_scene_services=['0x170a0'],global_original_helper_entries_preserved=False,global_helper_entries_unchanged_by_v30=True,inherited_global_GPU_redirects=True,pending_acceptance_wait_bypassed_inside_scene=True,
        GPU_programs_recovered_by_this_change=False,host_cases=768,host_guards=16,native_body_cases=768,
        prototype_scene_cases=772,final_scene_cases=772,final_display_cases=1153,
        retained_caller_cases=4992,retained_fallback_cases=16,geometry_cases=256,
        final_scene_fallback_cases=384,final_scene_nested_cases=64,final_scene_alias_cases=256,
        other_alias_cases=dict(input_face=256,coordinate_geometry=128),outer_connected_cases=128,
        final_existing_gates=8,new_read_only_observers_qualified=True,actual_shared_monitor_CPU_lanes=512,
        module_bytes=48738,module_increase_from_v29=328,connected_C_stack_bytes=168,C_stack_reserved=208,
        linked_native_bytes=b['linked_component_bytes'],reservation_bytes=b['component_bytes'],
        boot_copy_bytes=b['copy_component_bytes'],initial_heap_bytes=b['initial_heap_bytes'],
        copied_final_module_byte_identical=True,new_disc_built=True,disc_integrated=True,
        candidate_disc=b['derived_disc'],candidate_disc_sha256=b['derived_disc_sha256'],
        module_sha256=bridge['payload_sha256'],fresh_gameplay_verified=False,fresh_review_pending=True,
        live_heap_headroom_measured=False,game_fidelity_verified=False,installed_preview_changed=False,
        new_predictions=0,recovered_actual_local_predictions=2,new_training=False,optimizer_updates=0,
        native_Chat_verified=False,whole_game_complete=False,next_action=action,
        scope='Six already recovered CPU helper entries now execute structured native C inside the scene caller. Exact CPU/banks/private guest return words, scoped bus order, nested calls and arena ownership pass finite fixtures. Declared mailbox idle/ack/completion inputs are not GPU program execution. Normal-return boundaries do not establish arbitraryIRQ, cycle timing, complete rendering, audio or physical-console equivalence.')
    report.write_text('BIWN v30 — scene GPU CPU command family\n\n'
        'Six GPU command CPU helpers now execute structured C inside the scene caller: E098, E0A6, E0F2, E148, E19E and E202. These routines were already recovered in earlier logical/static work; this adds six internal native implementations, zero newly recovered original functions. The global GPU entries retain earlier native redirects, not the original unpatched instructions. Inherited GPU programs remain. The prior global E098 wait checks F03204==FFFFFFFF before F03200==0; the new internal E098 implements only the pinned original F03200 check. Therefore this changes the inherited restoration wait behavior inside the scene and needs fresh validation. Geometry-record processing at170A0 is the only remaining captured service in this scene caller. The selected C is coordinator-authored.\n\n'
        'Host768 cases plus16 guards and native768 cases pass complete final CPU/bank/private guest-return-word and memory comparisons. Connected772 cases pass at prototype and deployed addresses, including ordered mailbox operations and internal wait boundaries. Deployed display1153, retained4992+16 fallbacks, geometry256 and all8 startup/component/heap gates pass. Additional scene fallback384, self-reentry64, scene/input/face aliases256, input/face aliases256, coordinate/geometry aliases128, outer-connected128 and public-bus14 pass. Read-only observer fault controls and512 actual shared CPU lanes pass. These are finite component fixtures.\n\n'
        'Module48738 bytes,328 larger thanv29. Connected C stack168/208 bytes,40 spare. Linked code89568 bytes; reservation277568; boot copy115968; initial heap120320. Copied sources and SDK rebuild byte-identically. Live heap availability and game speed have not been measured forv30. A separate experimental CDI is built; fresh gameplay review remains pending. The latest reviewed gameplay image remainsv29; the Desktop checkpoint preview is unchanged.\n\n'
        'The first connected fixture stopped after23 cases because its simulated completion queue did not clear the flag written by a later projection. Revised fixtures explicitly hold completion zero after queue exhaustion on both lanes. No GPU consumer runs in these component tests. The failed fixture is preserved; its failure was not a native-C mismatch. The first coordinator compile also had an incorrect extra arithmetic-width argument, corrected before passing tests. A copied-build driver initially generated a nonexistent path, corrected before a successful rebuild.\n\n'
        'Local Author130.92 seconds: incomplete output at its2600token cap; not compiled. Same-model Repair125.76 seconds: complete response but6begin and57end markers violate the required single lexical pair. It also retains carry/zero-mask, guest return-address and projection-result errors on static inspection. Neither was compiled or installed. Exact prompts and outputs are preserved. Ambiguous bit-number wording in feedback and an incomplete arithmetic-return API description are documented prompt limitations. No optimizer updates, useful-quality result or copied-weight Native Chat rendering claim follows.\n\n'+action+'\n\nDisc: '+b['derived_disc']+'\n')
    packet['native_scene_gpu_family_progress']=packet['latest_source_development']=facts
    packet['native_scene_draw_progress']['gpu_family_prototype']=facts
    packet['native_scene_draw_progress']['next_action']=action
    packet['native_scene_dispatch_headroom_progress']['next_action']=action
    packet['native_display_list_progress']['next_action']=action
    packet['pending_native_candidate']=dict(facts,variant='v30 scene GPU CPU command-family experimental disc',new_fresh_gameplay_verified=False)
    packet['local_scene_gpu_family_development_progress']=dict(status=local['status'],review=str(localp),roles=local['roles'],actual_predictions=2,new_training=False,model_source_installed=False,report=str(Path(local['directory'])/'prompts-and-responses.txt'))
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False)
    packet['checked_current_summary']='V30 integrates six structured GPU command CPU helpers into a separate experimental disc. Final scene772, native body768, all8 component gates, aliases/nesting and read-only monitors pass; fresh review is pending. V29 remains the latest reviewed game run:5284 display/rotation/clear returns,8478 paired video differences, final video agrees; sampled outer-active heap880 bytes. Full game, fidelity and useful training quality remain open; checkpoint preview unchanged.'
    save(out/'facts.json',facts);save(out/'current-status-packet.json',packet);shutil.copy2(__file__,out/'publisher-source.py')
    shutil.copy2(report,out/report.name)
    dependencies.update({str(p):sha(p)for p in out.rglob('*')if p.is_file()});dependencies[str(report)]=sha(report)
    pub=V/'scene-gpu-family-component-reviewed-v1-current.json'
    atomic(pub,dict(status=facts['status'],directory=str(out),report=str(report),facts=str(out/'facts.json'),new_predictions=0,new_training=False,whole_objective_complete=False,dependencies_sha256=dependencies))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**dependencies,str(pub):sha(pub)})
    atomic(wp,w)
    for path,h in dependencies.items():
        src=Path(path);assert src.is_relative_to(ROOT),src
        clone(src,P/'workbench'/src.relative_to(ROOT))
    clone(pub,P/'workbench/verification'/pub.name);clone(wp,P/'workbench/verification'/wp.name)
    for root in [ROOT,P/'workbench']:
        (root/'CURRENT DECOMPILATION.txt').write_text(report.read_text())
        (root/'WATCH LOCAL AGENTS.txt').write_text(report.read_text()+'\nExact local Author and Repair prompts/responses are available through Model Prompts and Responses.command. These were API runs with the copied local model; Native Chat rendering was not tested in this work block.\n')
    print(facts['status'],report,flush=True)

if __name__=='__main__':main()
