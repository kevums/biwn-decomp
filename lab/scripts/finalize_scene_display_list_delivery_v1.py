"""Deliver prototype evidence and leave the full game/local-model goal active."""
import json,shutil,sys
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
sys.path.insert(0,str(ROOT))
from native_deck_status_evidence_v1 import load

def main():
    packet=load(ROOT);d=packet['native_display_list_progress'];assert not d['disc_integrated'] and d['module_bytes']==48494
    assert d['native_body_cases']==1153 and d['connected_scene_cases']==772 and d['connected_C_stack_bytes']==208
    assert packet['native_scene_draw_progress']['profile']=='deck-shared-v26-scene-clear'
    root=read(V/'scene-display-list-current-MCP-response.json');copied=read(V/'scene-display-list-copied-MCP-response.json');decoded=json.loads(copied['result']['content'][0]['text'])
    for raw in [root['result'],decoded]:
        assert raw['native_display_list_progress']['module_bytes']==48494 and not raw['native_display_list_progress']['disc_integrated']
        assert raw['native_display_list_progress']['connected_C_stack_margin']==0
    assert root['result']['proof_sha256']==sha(V/'native-Deck-current-status-v1-current.json')
    assert decoded['proof_sha256']==sha(P/'workbench/verification/native-Deck-current-status-v1-current.json')
    assert len(root['metadata']['tools'])==19 and len(copied['tools'])==18
    for lane in ['root','copied']:
        text=(V/f'scene-display-list-{lane}-status.txt').read_text();assert '48,494' in text and '208/208' in text and '1153 actual native body' in text and '772 connected scene' in text
    from native_deck_source_context_v13 import compact_snapshot,matches
    context=compact_snapshot();assert context['native_display_list_progress']['native_body_cases']==1153 and matches('Explain 185B2 display-list recovery')
    indices={n:read(base/'verification/current-model-work-index-v4-current.json')for n,base in [('root',ROOT),('copied',P/'workbench')]};assert indices['root']['saved_prompt_or_transcript_records']==185 and indices['copied']['saved_prompt_or_transcript_records']==186
    audits=[]
    for path in P.glob('path-audit-*.json'):
        a=read(path)
        if any('/scene-display-list-prototype-reviewed-v1/'in p for p in a.get('restored_paths',[])):
            assert not a['denied'];audits.append(path)
    assert audits
    out=V/'scene-display-list-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    for src in [V/'scene-display-list-current-MCP-response.json',V/'scene-display-list-copied-MCP-response.json',V/'scene-display-list-root-status.txt',V/'scene-display-list-copied-status.txt',*audits]:shutil.copy2(src,out/src.name)
    save(out/'compact-source-context.json',context)
    for n,x in indices.items():save(out/(n+'-saved-prompt-index.json'),x)
    brief=ROOT/'reports/BIWN Display List Progress.txt'
    brief.write_text('BIWN progress — display-list native prototype\n\n'
      'The already recovered 185B2 display-list builder now has a compact C prototype with full final CPU/bank state and original guest stack/table effects. It passes 1,217 host cases, 17 host guards, 64 distinct supplementary reread fixtures, 1,153 actual native body cases and 772 connected scene cases. Actual native data-bus checks preserve the original memory-CLR dummy reads missed by the historical C/Unicorn trace.\n\n'
      'Selected module: 48,494 bytes. Direct helper stack: 96 bytes. Connected scene stack: 208 of 208 bytes, with no remaining partition margin. The copied SDK builds identical bytes. Earlier larger/stack-failing variants are preserved.\n\n'
      'This is a component prototype, not a new game disc. Retained callers, fallback, actual nesting, cross-root aliases, final image/resource checks and fresh candidate/control routes are pending. The installed Desktop preview and latest fresh-tested v26 disc are unchanged. Current game fidelity still has 8,160 feedback-route video differences, 279 fixed-input-prefix differences and silent audio captures.\n\n'
      'No new model predictions or optimizer updates. Exact previous model prompts and responses are retained. LM Studio UI inspection timed out; copied-weight native Chat remains unverified. Whole-game readable source, complete same-console rebuilding, useful training quality, audio/IRQ fidelity and physical Jaguar CD validation remain unfinished.\n\n'
      'Detailed review: '+d['report']+'\nNext: '+d['next_action']+'\n')
    watch=ROOT/'WATCH LOCAL AGENTS.txt';shutil.copy2(watch,out/'before-WATCH LOCAL AGENTS.txt')
    watch.write_text('CURRENT GAME WORK — display-list component prototype\n\n'
      'Codex coordinator restructured the existing checked logical/static185B2references, then wrote the compact three-pass full-final-CPU algorithm with original guest LINK/MOVEM/private-table effects. This is one structured/native prototype for an already recovered original function, zero new unique functions. No cloud subagents.\n\n'
      'Deterministic tools: original pinned68000 plus Unicorn host matrices, distinct declared reread fixtures, actual target CPU/RAM/data-bus comparisons, connected shared bridge tests, stack/fence checks and copied-source/SDK byte identity. Selected prototype passes host1217+17guards/supplement64/native1153/connected772. Exact target connected stack208/208; no disc adoption.\n\n'
      'Corrections: actual target bus checks exposed two CLR dummy reads absent from the old C/Unicorn trace. Native CLR sites now retain them; ordinary zero writes remain MOVE. First connected build exceeded the stack partition. Inlining passed but enlarged code; compact source reduces the module to48,494bytes. Old failures and variants remain frozen in the review. Host guards/reread fixtures and target stable-value bus proofs have different scopes.\n\n'
      'Local model roles: no new Author, Repair, Reviewer, Reader prompts or optimizer updates in this continuation. LM Studio UI inspection request timed out, so no new visible Chat verification. Earlier exact prompts/responses remain in Model Prompts and Responses.command. The current source/context tools expose the new prototype facts.\n\n'
      'Current report: '+str(brief)+'\nDetailed evidence: '+str(V/'scene-display-list-prototype-reviewed-v1-current.json')+'\n\nHistorical notes below describe their recorded time.\n\n'+watch.read_text())
    for src in [brief,watch]:shutil.copy2(src,out/src.name);shutil.copy2(src,P/'workbench'/src.relative_to(ROOT))
    for path in [ROOT/'CURRENT DECOMPILATION.txt',P/'CURRENT DECOMPILATION.txt',P/'workbench/CURRENT DECOMPILATION.txt']:
        path.write_text('CURRENT SOURCE PROTOTYPE — compact185B2 passes native1153/connected772;48,494bytes; stack208/208. Not in a disc. Current v26 game and Desktop preview unchanged.\nReport: '+str(brief)+'\n\nEarlier notes:\n'+path.read_text())
    scripts=set(ROOT.glob('scripts/*scene*display*list*.py'))|{ROOT/'scripts/scene_display_list_mutation_vectors_v2.py',ROOT/'scripts/structure_scene_display_list_v1.py'}
    for src in scripts:
        dest=P/'workbench'/src.relative_to(ROOT);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dest)
    gp=V/'goal-continuation-current.json';goal=read(gp);save(out/'previous-goal-state.json',goal)
    goal.update(status='active_display_list_native_component_pass_final_image_pending',recorded_at=datetime.now(timezone.utc).isoformat(),
      previous_goal_turn_classification='Progress: v26clear fresh-gameplay review and local scaffolded passing body delivered; Root/copied status/MCP and185/186saved records preserved.',
      current_turn_classification='Progress: restructured existing185B2reference, host1217+17guards and distinct reread64pass. Actualnativebus exposed two historicalCLRdummyread omissions, corrected with nativeCLRsites. Nativev1direct1153passes but connected overflows208partition; inlinedv2direct1153/connected772passes at168stack but55704bytes. CompactC selected: host1217+64supplement, native1153/fullCPU/nonprivateRAM/actualbus, connected772/680displaycalls/208of208stack; copied48494byte module identical. Prototype only: no disc,fresh route,retained/alias/nesting approval. NativeChatUIconnection timedout, zero new inference/optimizer updates.',
      full_objective_complete=False,blocked=False,ongoing_finite_workers=[],new_training_this_turn=False,optimizer_updates_this_turn=0,completed_new_local_predictions_this_turn=0,recovered_completed_predictions_from_prior_worker=0,newly_reviewed_actual_predictions=0,new_model_authored_complete_functions_this_turn=0,
      new_unique_original_functions_this_turn=0,new_coordinator_authored_routines_this_turn=1,new_internal_native_helper_integrations_this_turn=0,new_disc_internal_native_helper_integrations_this_turn=0,new_shared_native_component_helper_integrations_this_turn=1,
      source_authorship_scope='Existing185B2logical/static references restructured and compacted by coordinator. One additional structured/native prototype, zero new unique original functions and no model-authored code or weight updates. Final CPU normal-call contract; intermediate shadow/IRQ behavior remains unproved.',
      new_disc_built_this_turn=False,candidate_disc_built_this_turn=False,game_reruns_this_turn=0,installed_preview_changed=False,experimental_game_model_adopted=False,
      candidate_metrics_profile='deck-shared-v26-scene-clear',latest_new_component_profile=d['prototype_profile'],latest_new_component_disc_integrated=False,latest_new_component_fresh_gameplay_verified=False,latest_new_component_alias_nesting_verified=False,
      latest_new_component_module_bytes=48494,latest_new_component_direct_C_stack_bytes=96,latest_new_component_connected_C_stack_bytes=208,latest_new_component_C_stack_reserved=208,
      source_recovery_review=str(V/'scene-display-list-prototype-reviewed-v1-current.json'),latest_source_recovery_review=str(V/'scene-display-list-prototype-reviewed-v1-current.json'),latest_component_source_review=str(V/'scene-display-list-prototype-reviewed-v1-current.json'),latest_source_recovery_report=str(brief),latest_delivery_review=str(V/'scene-display-list-delivery-v1-current.json'),
      current_status_reader_live_generation_verified=False,current_status_reader_current_source_reply_approved=False,current_status_reader_scope='Actual Root/copied MCP1.26 returns compact185B2prototype and preserves v26game facts. Checked status and compact model source context verified. Native UI request timedout; no new model Reader or coding generations. No inference/training replay.',
      saved_prompt_or_transcript_records=185,portable_saved_prompt_or_transcript_records=186,next_game_source_target=d['next_action'])
    goal['remaining_requirements']['game']='Compact185B2prototype now passes host1217/17guards,64distinct host reread fixtures,native1153actualCPU/RAM/bus,connected772with680native displaycalls; copied48494byte module identical. Connectedstack208/208no margin. New retained/fallback/nesting/cross-root alias/final-image/resource/fresh-route/read-only witness qualification remain pending. Latest game image is stillv26with8160feedback video/279fixedprefix differences and silent audio. Whole readable source, complete same-console rebuild, remaining originalCPU/GPU/DSP/HLE/device behavior and arbitraryIRQ/audio/physicalJaguarCD validation remain incomplete.'
    goal['remaining_requirements']['local_frontend']='Prior copied daily27B6bit scaffoldedAuthor19.33s passed separate host256/native772; remains outside game. New source/context/status tools expose display prototype. LMStudioUIinspectiontimedoutthisturn; copied-weight nativeChat/current-facts output and broader easy workflow usability remain unverified. Zero new predictions or updates.'
    goal['next_actions']=[d['next_action'],'Keep selected prototype source and completed matrices frozen; use its exact48,494byte module and copied SDK evidence. Do not rerun earlier static/inlined profiles or completed local predictions merely for receipts.','Continue useful local coding/training/evaluation with reviewed development data and untouched holdouts. Existing64update0/4base/adapter pilot remains unpromoted; copied two-update capability is not quality. NativeChatcopied-weight usability and future256GBperformance remain unverified.']
    goal['do_not_restart'] += ['Completed185B2structured host1217/17guards and64distinct reread supplement. The1217include64repetitions of two reread fixtures; not64unique inputs.','Completedactualnativev1direct1153/53164bytes/152stack; connectedfirstcaseexceeded208atobserved212, preserve failure.','Completedinlinev2native1153/55704bytes/56directstack and772connected/168stack; not selected because code footprint.','Deadflagv3passed8connectedpreflightonly at51080bytes/152stack; do not call it fully qualified.','Completedcompactalgorithmhost1217/17guards and64distinct reread supplement; targetstable1153actualCPU/RAM/bus plus772connected/680displaycalls,48494bytes/96direct/208connectedstack; copied module identical. No new disc or alias/nesting/fresh approval.','ActualnativeCLRdummyreads corrected at original1864C/187A4. Historicalhost/Unicorntracesomit them; do not cite host bus order as original CLR proof. Target recorder read values/widths unavailable, host/type/opcode evidence separate.','CompletedRoot/copiedMCP1.26(19/18tools), checkedstatus andcompactsourcecontext for prototype;185/186saved prompt counts unchanged; NativeUIgetApptimedout, no model generation.']
    atomic(gp,goal);shutil.copy2(gp,P/'workbench/verification'/gp.name);shutil.copy2(__file__,out/'finalizer-source.py')
    receipt=dict(status='terminal_display_list_component_Root_copied_status_delivered_goal_active',directory=str(out),prototype_publication=str(V/'scene-display-list-prototype-reviewed-v1-current.json'),whole_objective_complete=False,new_predictions=0,new_training=False,new_disc_built=False,installed_preview_changed=False,root_MCP_tools=19,copied_MCP_tools=18,copied_origin_guard_denied=0,root_saved_records=185,copied_saved_records=186,source_sha256={str(p):sha(p)for p in out.iterdir()if p.is_file()})
    atomic(V/'scene-display-list-delivery-v1-current.json',receipt);shutil.copy2(V/'scene-display-list-delivery-v1-current.json',P/'workbench/verification/scene-display-list-delivery-v1-current.json');print(receipt['status'],str(brief),flush=True)
if __name__=='__main__':main()
