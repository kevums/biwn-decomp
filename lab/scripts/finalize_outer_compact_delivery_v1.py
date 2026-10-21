"""Deliver current memory/game evidence, exact Reader output and portable launchers."""
import shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
from publish_scene_reset_fresh_v1 import ROOT,V,P,read,save,sha,atomic
from publish_scene_gpu_family_component_v1 import clone

def main():
    wp=V/'native-Deck-current-status-v1-current.json';w=read(wp)
    for p,h in w['dependencies_sha256'].items():assert sha(p)==h,p
    packet=read(w['packet']);readerp=V/'copied-Reader38-reviewed-v1-current.json';reader=read(readerp)
    for p,h in reader['dependencies_sha256'].items():assert sha(p)==h,p
    pre=read(P/'workbench/verification/Reader38-preflight-current.json');assert pre['new_predictions']==0
    evidence=read(Path(pre['directory'])/'evidence.json')
    assert evidence['experimental_candidate']['candidate_frames']==24985 and evidence['measured_heap_while_outer_active']==dict(candidate=19696,control=19696)
    assert evidence['latest_source_artifact_kind']=='built_experimental_disc'and evidence['pending_native_candidate']is None
    out=V/'outer-compact-current-delivery-v1'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True)
    save(out/'before-wrapper.json',w);save(out/'before-packet.json',packet)
    subprocess.run(['/bin/cp','-cR',pre['directory'],str(out/'copied-Reader38-preflight')],check=True,capture_output=True)
    packet['previous_copied_Reader_before_artifact_type_fix']=packet['current_copied_Reader_progress']
    packet['current_copied_Reader_progress']=dict(status=reader['status'],directory=reader['directory'],review=str(readerp),actual_predictions=1,seconds=11.02,words=127,max_words=150,word_limit_pass=True,
        required_current_numeric_facts_correct=True,supplied_snapshot_factual_claims_approved=True,artifact_type_error=False,artifact_type_pass=True,
        code_authorship_statement_present=False,complete_requested_briefing_approved=False,current_source_reply_verified=False,
        current_source_factual_claims_reviewed=True,provided_candidate_profile='v30',provided_sampled_heap_bytes=560,latest_source_changed_since_last_prediction=True,
        broader_quality_approved=False,quality_approved=False,new_training=False,optimizer_updates=0,trained_adapter_used=False,native_Chat_display_verified=False,
        model_identifier=reader['model_identifier'],ordinary_launcher_verified=True,default_reader_version=38,default_reader_prepared=True,default_reader_generation_verified=True,
        scope=reader['scope'])
    packet['current_default_Reader_progress'].update(status='terminal_Reader38_current_evidence_preflight_and_prior_snapshot_generation_verified',current_evidence_preflight_verified=True,
        actual_prediction_verified=True,actual_prediction_words=127,actual_prediction_seconds=11.02,actual_prediction_supplied_profile='v30',latest_compact_source_reply_verified=False,
        prior_quality_pilot_explicit_in_prompt=True,pending_vs_tested_disc_scopes_separate=True,preflight=str(out/'copied-Reader38-preflight/protocol.json'),
        preflight_input_proof_sha256=pre['evidence_proof_sha256'],path_audit_denied=[],
        scope='Copied Reader38 evidence preflight supplies compact-image facts without inference. One actual Reader38 generation used the earlier v30 snapshot and fixed its prototype/image distinction; it omitted requested authorship. No accepted reply on latest compact facts or copied-weight Native Chat rendering claim.')
    report=ROOT/'reports/BIWN Current Game Memory and Local Model.txt'
    report.write_text('BIWN — current game, memory and local model\n\n'
        'The compact experimental disc passes a fresh route of 24,985 candidate and 24,969 control frames. All 6,299 native scene calls return; display-list, rotation, clear and captured geometry-record services each return 5,297 times. All monitors finish clear and quiescent. No checkpoint or host CPU/RAM/task repair was used.\n\n'
        'The capacity change is verified: sampled free heap while the outer task was active rises from 560 to 19,696 bytes in both lanes. This is not the global minimum. Outer slots shrink from 576 to 384 bytes, reclaiming 19,392 bytes; code/alignment costs 256 bytes, leaving a 19,136-byte net gain. Initial heap is 139,456 bytes. Outer stack is 164/224 bytes; scene stack remains 168/208 bytes. All relocated component, startup, heap, nesting, alias and read-only observer checks pass. Both deployed modules rebuild byte for byte with the copied SDK.\n\n'
        'Fidelity is open: 7,351 paired video differences; final video and selected final fields agree. Both audio captures are silent. Game-latched controller RAM differs on 359 frames and actual frontend schedules on 338 frames. The identical-input prefix differs on 437 of 1,000 video frames; compact versus v30 controls differ on 216 frames. The memory gain does not establish a rendering or speed improvement.\n\n'
        'Local-model test: copied Reader37 generated 140 words in 13.2 seconds, with correct numbers but an invented pending disc. Prompt/evidence clarification led Reader38 to generate 127 words in 11.02 seconds and correctly identify the prototype as a component. Reader38 was correct for its supplied v30 snapshot, omitted the requested explicit code-authorship statement, and predates the compact-image publication. Generation times exclude queue waiting; total launcher latency was not instrumented. Both raw prompts and responses are saved. No weight update or general/held-out quality improvement is claimed. The earlier quality pilot remains base 0/4 and adapter 0/4.\n\n'
        'The copied current-evidence preflight and actual Root/copied MCP transports verify the new 19,696-byte heap and compact-image facts. Root launchers now use the copied workbench instead of Reader29: BIWN Current Status reads checked saved evidence, Live Local BIWN Briefing requests a fresh local answer, and Model Prompts and Responses shows exact saved exchanges. Reader38 is the default; no current compact-facts response or copied-weight Native Chat rendering has been approved. Native-window inspection timed out, so work continued headlessly.\n\n'
        'Current outer-context/layout changes are coordinator-authored. Earlier linked hybrid components retain their recorded attribution. No new model body, adapter or trained weights were adopted. The Desktop checkpoint preview is unchanged.\n\n'
        'Next: implement and qualify readable 170A0 geometry-record processing and its copy/movement-matrix providers using the recovered capacity. Complete same-console/source rebuilding, remaining CPU/GPU/DSP/HLE/device/rendering recovery, useful training quality and audio/IRQ/physical-console fidelity remain open. Future hardware performance has not been measured.\n\n'
        'Game review: '+packet['latest_native_candidate']['report']+'\nReader review: '+str(readerp)+'\n')
    packet['current_delivery_report']=str(report)
    save(out/'current-status-packet.json',packet);save(out/'Reader38-readiness.json',packet['current_default_Reader_progress']);shutil.copy2(__file__,out/'publisher-source.py');shutil.copy2(report,out/report.name)
    for name in ['run_deck_status_live_v38.py','portable_biwn_entry_v11.py','show_native_status_v3.py','check_copied_Reader38_evidence_v1.py']:
        shutil.copy2(ROOT/'scripts'/name,out/name)
    shutil.copy2(ROOT/'native_deck_source_context_v13.py',out/'native_deck_source_context_v13.py')
    deps={str(p):sha(p)for p in out.rglob('*')if p.is_file()};deps.update(reader['dependencies_sha256']);deps[str(readerp)]=sha(readerp);deps[str(report)]=sha(report)
    pub=V/'outer-compact-current-delivery-v1-current.json';atomic(pub,dict(status='terminal_compact_game_memory_and_local_Reader_delivery_goal_open',directory=str(out),report=str(report),new_predictions=0,new_training=False,whole_objective_complete=False,dependencies_sha256=deps))
    w.update(packet=str(out/'current-status-packet.json'),dependencies_sha256={**w['dependencies_sha256'],**deps,str(pub):sha(pub)});atomic(wp,w)
    for p,h in deps.items():
        src=Path(p);assert src.is_relative_to(ROOT);clone(src,P/'workbench'/src.relative_to(ROOT))
    clone(pub,P/'workbench/verification'/pub.name);clone(wp,P/'workbench/verification'/wp.name)
    # Include the component review's complete dated bundle as a portable
    # reference, in addition to the dependency closure already copied above.
    component=read(V/'outer-compact-components-reviewed-v1-current.json');src=Path(component['directory']);dst=P/'workbench'/src.relative_to(ROOT)
    dst.parent.mkdir(parents=True,exist_ok=True)
    if not dst.exists():subprocess.run(['/bin/cp','-cR',str(src),str(dst)],check=True,capture_output=True)
    else:
        for path in src.rglob('*'):
            if path.is_file():clone(path,dst/path.relative_to(src))
    for root in [ROOT,P/'workbench']:
        (root/'CURRENT DECOMPILATION.txt').write_text(report.read_text());(root/'WATCH LOCAL AGENTS.txt').write_text(report.read_text()+'\nUse Model Prompts and Responses.command for exact role prompts and raw replies. No local model decompilation body was adopted in this capacity change.\n')
    print('Delivered current compact game/memory facts and Reader38 scope:',report,flush=True)

if __name__=='__main__':main()
