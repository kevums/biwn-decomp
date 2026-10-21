"""Publish checked185B2prototype separately from the still-current v26 game image."""
import shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic

def main():
    wp=V/'native-Deck-current-status-v1-current.json';wrapper=read(wp)
    for p,h in wrapper['dependencies_sha256'].items():assert sha(p)==h,p
    names=['scene-display-list-structured-host-v1','scene-display-list-mutations-v2','scene-display-list-native-v1','scene-display-list-native-v2','scene17-display-list-bridge-v2','scene-display-list-algorithm-host-v2','scene-display-list-mutations-v3','scene-display-list-native-v4','scene17-display-list-bridge-v4','scene17-display-list-copied-rebuild-v1']
    proofs={n:read(V/(n+'-current.json'))for n in names}
    for n,g in proofs.items():
        assert g['status'].startswith('terminal_')and'failed'not in g['status']and'preflight'not in g['status'],(n,g['status'])
        for k in ['source_sha256','copied_source_sha256']:
            for p,h in g.get(k,{}).items():assert sha(p)==h,(n,p)
    host=proofs['scene-display-list-algorithm-host-v2'];native=proofs['scene-display-list-native-v4'];bridge=proofs['scene17-display-list-bridge-v4'];copied=proofs['scene17-display-list-copied-rebuild-v1']
    assert host['completed']==1217 and host['host_guards']==17
    assert proofs['scene-display-list-mutations-v3']['completed']==64
    assert native['completed']==1153 and native['maximum_C_stack_bytes']==96 and native['original_display_instructions_on_native_path']==0
    assert bridge['completed']==772 and bridge['maximum_C_stack_bytes']==208 and bridge['native_display_calls']==680 and bridge['original_display_instructions_executed']==0
    assert native['payload_sha256']==bridge['payload_sha256']==copied['sha256'] and native['payload_bytes']==copied['bytes']==48494
    out=V/'scene-display-list-prototype-reviewed-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    packet=read(wrapper['packet']);assert packet['native_scene_draw_progress']['profile']=='deck-shared-v26-scene-clear'
    save(out/'previous-wrapper.json',wrapper);save(out/'previous-status-packet.json',packet)
    for n,g in proofs.items():
        save(out/(n+'.json'),g);subprocess.run(['/bin/cp','-cR',g['directory'],str(out/n)],check=True,capture_output=True)
    # The unsuccessful connected run stopped at the first observed overrun;
    # do not describe its152byte standalone peak as a safe connected peak.
    failed=[]
    for p in sorted((V/'scene17-display-list-bridge-v1').glob('*/protocol.json')):
        g=read(p)
        if g['status']=='terminal_failed':
            dest=out/'failed-connected-v1';subprocess.run(['/bin/cp','-cR',str(p.parent),str(dest)],check=True,capture_output=True);failed.append(dict(status=g['status'],error=g.get('error'),scope='Connected path crossed208byte partition; stopped at observed212bytes, not a measured peak.'))
    assert failed
    for stem in ['scene-display-list-structured-v1','scene-display-list-algorithm-v2']:
        src=ROOT/'projects/black-ice-white-noise/restoration/experimental'/stem;subprocess.run(['/bin/cp','-cR',str(src),str(out/stem)],check=True,capture_output=True)
    report=ROOT/'reports/BIWN Display List Native Prototype Review.txt'
    report.write_text('BIWN — compact native display-list prototype, not installed\n\n'
      '185B2 is an already recovered function. This continuation restructures it into a three-pass C body with the original guest LINK/MOVEM saves, dynamic private link table, local-frame effects, source jump-table reads, descriptor rereads and final full CPU/bank state. There are zero new unique original functions and one additional structured native prototype. The game disc and Desktop preview are unchanged.\n\n'
      'The compact body passes 1,217 host comparisons against the original pinned 68000 and independent Unicorn, plus 17 host guards. The 1,217 include 1,025 mixed/captured descriptor fixtures, 128 CCR/bank/body/full-call combinations, and 64 repetitions of two reread fixtures. A separate supplement tests 64 distinct reread fixtures with varied registers, CCR, banks and field values. These counts are test executions, not counts of unique recovered functions.\n\n'
      'The earlier host/static translation and Unicorn omit two memory-CLR dummy reads. Actual native CPU bus comparison found this gap even though registers and RAM matched. Native CLR instructions now preserve those reads at the local-frame clear and scaled-object output clear. Other native stores use explicit MOVE so an ordinary zero value does not introduce a CLR read. Host/Unicorn access traces alone are not evidence for the original CLR bus protocol.\n\n'
      'The selected compact module passes 1,153 native body cases. Complete logical registers/PC/SR/USP/SSP and 2 MB RAM match outside the supplied 98-byte context and private 208-byte C stack. Actual data-bus read addresses/count/order and write values match outside native code/private arenas and original instruction fetch; source jump-table data reads remain included. The recorder does not expose widths/read values; host and typed/opcode source evidence are separate. Native body fixtures use stable descriptor values. External reread mutations are a host fixture proof, not a target concurrency proof.\n\n'
      'The connected scene matrix passes 772 cases through the actual shared 68000 bridge. Native clear, rotation and display-list bodies each run 680 times with full CPU, non-arena RAM, helper records, MMIO ordering and all seven fences across 101 task slots checked. The original 185B2 body executes zero instructions on the native connected path; other services remain explicit component fixtures. This is not fresh gameplay.\n\n'
      'Resource variants are preserved. The first native module was 53,164 bytes and passed the direct 1,153-case body test at 152 bytes of C stack, but failed connected stack admission beyond 208 bytes. Forced inlining produced 55,704 bytes, direct stack 56 and connected stack 168; it passes the full direct and connected matrices. A separate dead-flag candidate passed only eight connected preflight cases and was not selected. The compact algorithm is 48,494 bytes, direct stack 96 and connected stack 208 of 208. It has no connected C-stack margin. Retained-caller regression, invalid-task fallback, actual nesting, cross-root aliases, final-address image gates and fresh resource/timing/IRQ behavior still require qualification. A smaller code footprint alone does not prove heap admission or a speedup.\n\n'
      'The copied sources and copied 68000 SDK rebuild the same 48,494-byte prototype. No disc was built or promoted in this continuation. The latest game-qualified image remains v26 with 5,360 clear/rotation returns, 8,160 paired video differences, 279 fixed-input-prefix differences and silent audio captures. Full game rebuilding, audio/IRQ fidelity and physical Jaguar CD validation remain unfinished.\n\n'
      'No new model inference or optimizer updates. LM Studio UI inspection timed out, so copied-weight native Chat remains unverified; this was not evidence that the screen was locked. Existing local model prompts/results and the unpromoted 0/4 training pilot remain intact.\n\n'
      'Selected source: '+str(ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-display-list-algorithm-v2/coordinator-reference.inc')+'\nNative profile: '+str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-shared-v27-scene-display-list-algorithm-v4')+'\n')
    progress=dict(status='terminal_structured_display_list_native_component_pass_disc_pending',entry='0x185b2',prototype_profile='deck-shared-v27-scene-display-list-algorithm-v4',host_cases=1217,host_guards=17,host_reread_case_count=64,host_reread_unique_vectors=2,distinct_supplemental_reread_cases=64,native_body_cases=1153,native_body_C_stack_bytes=96,connected_scene_cases=772,connected_native_display_calls=680,connected_C_stack_bytes=208,connected_C_stack_reserved=208,connected_C_stack_margin=0,module_bytes=48494,module_sha256=native['payload_sha256'],prototype_payload=native['payload'],original_display_instructions_on_native_path=0,native_memory_CLR_sites=2,host_Unicorn_CLR_dummy_read_gap=True,actual_native_data_bus_orders_match=True,actual_native_bus_read_values_and_widths_available=False,target_descriptor_values_stable=True,host_declared_reread_mutations_separate=True,copied_module_byte_identical=True,disc_integrated=False,new_disc_built=False,fresh_gameplay_verified=False,retained_callers_regression_verified=False,alias_nesting_verified=False,arbitrary_IRQ_or_intermediate_shadow_CPU_verified=False,new_unique_original_functions=0,new_structured_native_helpers=1,new_predictions=0,new_training=False,optimizer_updates=0,native_Chat_verified=False,UI_inspection_timed_out=True,installed_preview_changed=False,report=str(report),review=str(V/'scene-display-list-prototype-reviewed-v1-current.json'),source=str(ROOT/'projects/black-ice-white-noise/restoration/experimental/scene-display-list-algorithm-v2/coordinator-reference.inc'),next_action='Qualify the compact185B2prototype with retained callers, fallback/nesting/public-bus and alias matrices, then final image/address/resource gates and fresh candidate/control gameplay with an extended read-only display witness. Connected C stack uses208of208bytes. Keep v26 game/preview unchanged until broader qualification; whole-game source, useful model training, audio/IRQ and physical-console fidelity remain open.')
    packet['native_display_list_progress']=packet['latest_source_development']=progress
    for section in ['native_scene_draw_progress','latest_native_candidate','latest_fresh_reviewed_candidate']:
        packet[section]['next_action']=progress['next_action']
    for key in ['checked_current_summary','checked_answer','current_verified_route_summary']:
        packet[key]+=' New185B2 compact prototype: 1,153 native body and772connected cases pass,48,494bytes; connected stack208/208. Copied build identical. Not in the game image; final-image/alias/nesting/fresh qualification pending.'
    packet['current_copied_Reader_progress'].update(latest_source_changed_since_last_prediction=True,current_source_reply_verified=False)
    save(out/'progress.json',progress);save(out/'current-status-packet.json',packet);shutil.copy2(report,out/report.name)
    for src in [Path(__file__),ROOT/'scripts/show_native_status_v2.py',ROOT/'native_deck_source_context_v13.py']:shutil.copy2(src,out/src.name)
    deps={str(p):sha(p)for p in out.rglob('*')if p.is_file()};deps[str(report)]=sha(report)
    for p in [Path(native['payload']),V/'scene17-display-list-bridge-v4-current.json',V/'scene-display-list-native-v4-current.json']:deps[str(p)]=sha(p)
    pub=V/'scene-display-list-prototype-reviewed-v1-current.json';atomic(pub,dict(**progress,directory=str(out),dependencies_sha256=deps,whole_objective_complete=False))
    wrapper.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**wrapper['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(wp,wrapper)
    for p,h in wrapper['dependencies_sha256'].items():
        src=Path(p);assert src.is_relative_to(ROOT);dest=P/'workbench'/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.is_file()or sha(dest)!=h:subprocess.run(['/bin/cp','-c',str(src),str(dest)],check=True,capture_output=True)
    shutil.copy2(wp,P/'workbench'/wp.relative_to(ROOT))
    for src in [ROOT/'scripts/show_native_status_v2.py',ROOT/'native_deck_source_context_v13.py']:shutil.copy2(src,P/'workbench'/src.relative_to(ROOT))
    print(progress['status'],str(report),flush=True)
if __name__=='__main__':main()
