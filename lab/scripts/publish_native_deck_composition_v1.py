"""Freeze this continuation's game and local-model evidence without completion."""
import json
import subprocess
from datetime import datetime,timezone
from pathlib import Path
import check_native_deck_fresh_restore_v1 as common
ROOT=common.ROOT;V=ROOT/'verification';read=common.read;save=common.save;sha=common.sha

def main():
    pub=V/'native-Deck-composition-delivery'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');pub.mkdir(parents=True);print(pub,flush=True)
    names=['native-Deck-fresh-machine-restore-current.json','native-Deck-composed-fresh-reviewed-current.json','native-Deck-ordinary-input-reviewed-current.json','Deck-status-live-v8-reviewed-current.json','Deck-status-live-v9-reviewed-current.json','Deck-status-live-v10-reviewed-current.json','native-composed-Deck-team-reviewed-current.json','advertising-timing-ordinary-retest-current.json','advertising-timing-narrowed-rejected-current.json','advertising-timing-short-roles-reviewed-current.json','advertising-chronology-feedback-reviewed-current.json','advertising-timing-final-team-reviewed-current.json','native-Deck-context-v3-current.json','current-model-work-index-v4-current.json']
    records={name:read(V/name)for name in names}
    c=records['native-Deck-composed-fresh-reviewed-current.json'];o=records['native-Deck-ordinary-input-reviewed-current.json'];reader=records['Deck-status-live-v10-reviewed-current.json'];ad=records['advertising-timing-final-team-reviewed-current.json']
    assert c['native_coordinate_calls']==c['nested_coordinate_GPU4720_calls']==17 and c['paired_checkpoints']==46
    assert o['candidate']['observations']['acquire_pending']==1 and not o['cause_identified']
    assert reader['status']=='terminal_current_composed_and_ordinary_Deck_Reader_review_pass'
    catalog=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(catalog)==1 and catalog[0]['identifier']=='advertising-scholar'and catalog[0]['status']=='idle'and catalog[0]['queued']==0
    save(pub/'model-catalog.json',catalog)
    paths=set(V/name for name in names)
    for name,record in records.items():
        save(pub/name,record)
        for path,digest in record.get('source_sha256',{}).items():
            assert sha(path)==digest,path;paths.add(Path(path))
        for path,digest in record.get('files',{}).items()if isinstance(record.get('files'),dict)else []:
            assert sha(path)==digest;paths.add(Path(path))
    scripts=['check_native_deck_fresh_restore_v1.py','check_native_deck_composed_fresh_v1.py','review_native_deck_composed_fresh_v1.py','run_native_deck_ordinary_input_v1.py','run_native_deck_ordinary_input_v2.py','review_native_deck_ordinary_input_v1.py','run_deck_status_live_v8.py','run_deck_status_live_v9.py','run_deck_status_live_v10.py','native_chat_team_context.py','check_native_deck_context_v3.py','run_advertising_chronology_feedback_v1.py','publish_native_deck_composition_v1.py']
    paths.update(ROOT/'scripts'/name for name in scripts)
    paths.update(ROOT/name for name in ['native_deck_source_context_v2.py','native_deck_source_context_v3.py','advertising_study2a_context_v1.py','Live Local BIWN Briefing.command','Play BIWN Preview.command','config/current-model-work-sources.json'])
    save(pub/'source-and-raw-artifact-hashes.json',{str(p):sha(p)for p in sorted(paths)})
    review=ROOT/'reports/Native Deck Integration and Local Workflow Review.txt'
    text=f'''BIWN NATIVE INTEGRATION AND LOCAL WORKFLOW REVIEW

Full goal remains active. This continuation adds integration evidence and local workflow corrections; no game routine, disc image, default game preview or model weights changed.

GAME
The actual saved machine from the fresh experimental CDI route round-trips byte-exactly with its matching core. The installed native coordinate module and all other recovered native routines remain present. A controlled world/Deck roundtrip differs only by the coordinate root enabled versus original body. The installed native GPU family executes on both lanes. It observes17 compiled coordinate calls,17 directly nested native GPU4720 calls,113 GPU4720 calls per lane in total,149 GPU commands per lane and46 matching CPU/RAM/hardware/command checkpoints. Eighteen active cached slots and their payloads restore. No active coordinate helper yield is observed. Two world updates complete. CPU entry, two-task ring, selector/count13 patch and synchronous disc/GPU providers are explicit fixtures; this is not natural activation or hardware-timing proof.

The ordinary fresh-disc route then tries keypad1, B+C and0 with no snapshot restore, CPU/task seed or additional selector patch. At25024frames it has zero coordinate calls and one unfinished resource acquisition. Its final native loader frame is waiting for CD progress0x1d159c to reach0x1e8000. Reported ABI/stack/arena errors are zero, but a pending acquisition prevents a whole-route pass. The unmodified original image ran34538frames and stopped in return_loading before reaching the equivalent input phase. It is not a matched Deck-loading baseline; the candidate wait's cause remains unassigned.

The exact deployed files correct an earlier reporting split:9548bytes for deck-build/native-deck.bin and98bytes for finalizer.bin, rather than9532/114. Total installed code remains44430bytes. Only11D1A of the six recovered Deck callers is installed; the other five are hosted-only. Full readable game, same-console whole-game rebuild, natural Deck activation, suspension/reentrancy/IRQ and physical-console validation remain incomplete.

LOCAL INFERENCE AND WHO DID WHAT
Codex authored the new test harnesses, inspected the saved CPU/GPU/RAM evidence and reviewed model answers. Existing coordinate C authorship remains localV6Repair plus10 coordinator flag updates and coordinator native ABI/loader adapters. No new game C from a local model is accepted this turn.

The actual27B6bit daily model was loaded in LM Studio. Reader, Analyst, Restorer and Reviewer are sequential model roles on the same weights; compiler/emulator comparisons are separate tools. The current one-click Reader streams a correct completed/limits answer in{reader['stream']['seconds']}seconds, with{reader['stream']['time_to_first_message_seconds']}seconds to first response fragment. It distinguishes17controlledcalls/46checkpoints from zero ordinary calls and the pending transfer. The v9 driver mixed an older31-checkpoint fact into current evidence; that raw failure remains saved. Main menu11 and Live Local BIWN Briefing.command now use the tested v10 driver. The existing Play BIWN Preview.command remains the separate saved-checkpoint playable preview.

Three actual game roles passed source review through the exact installed plugin handler with a mock UI controller. This proves backend inference and prompt/response blocks, not native Chat selection or rendering. Full exact prompts and responses are indexed by Model Prompts and Responses.command.

ADVERTISING
The first new full team answer repeated an overlong132word draft and used a later-study methods citation. A narrower source selection then stopped at the unchanged exact quote/page gate after its single repair failed. Shorter task-specific roles produced correct chronology and conditional follow-ups in73words, but retained imprecise baseline-identification wording. The separate actual Reviewer feedback produced a source-checked67word correction. The final full-team retest status is:{ad['status']}. Its reviewed final word count is:{ad.get('final_words')}. Review details:{ad.get('review','See its bound source review.')}

This paper/task-specific selector retains all original indexed chunks24-29 for Study2A pages9-11, with unchanged source text/IDs/hashes. Unrelated-study and appendix excerpts are excluded for this chronology question. Other-paper, scale-operationalization and cross-study questions keep the general workflow. Quote/page gates remain enforced; no schema gate was loosened.

Sixteen predictions occurred before the final full-team retest; the retest adds{ad['actual_predictions']}. Zero optimizer updates occurred. These supplied-facts cases do not prove general Advertising reliability or constitute newly trained weights. The daily model and optional previously trained Reviewer remain distinct.

FULL REQUIREMENT AUDIT
Game: partial native/source restoration and controlled integration; full game/rebuild/physical tests incomplete.
Local frontend: tested one-click terminal briefing and actual plugin backend roles; latest native Chat UI unverified.
Advertising: task-specific source/role corrections and bounded retest above; wider reliability/training acceptance incomplete.
Future256GB setup: prior portable package retained; latest new files and workflows not yet migrated or verified on another machine/future hardware.

Next work: isolate the pending resource transfer with a matched loader/CD-device witness; do not attribute it from the unmatched original route. Preserve the passed native coordinate/GPU composition. Extend remaining source/asset closure and actual helper-suspension/IRQ tests. Continue Advertising evals and full native Chat/current-package acceptance.

Composed raw evidence:{c['directory']}
Ordinary-input evidence:{o['directory']}
Current prompt index:{records['current-model-work-index-v4-current.json']['report']}
Publication:{pub}
'''
    review.write_text(text);(pub/'review.txt').write_text(text)
    audit=dict(full_objective_complete=False,game='Partialnative/source integration. Ordinarytransferpending;wholegame/rebuild/physical unverified.',local_frontend='Actualterminal/pluginbackend;latestnativeChatUIunverified.',Advertising='Boundedtask-specificretest;widerreliability/trainingacceptanceincomplete.',future_hardware='Currentnewfilesnotmigrated;actualfuturehardwareunverified.')
    save(pub/'requirement-audit.json',audit)
    state=dict(status='terminal_native_Deck_composition_and_local_workflow_delivery',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(pub),review=str(review),review_sha256=sha(review),actual_predictions=16+ad['actual_predictions'],new_training=False,native_code_bytes=44430,native_coordinate_module_bytes=9548,finalizer_bytes=98,composed_native_coordinate_calls=17,nested_native_GPU_calls=17,paired_checkpoints=46,GPU_commands_per_lane=149,ordinary_coordinate_calls=0,ordinary_resource_acquisition_pending=1,original_baseline_matched=False,ordinary_wait_cause_identified=False,Reader_seconds=reader['stream']['seconds'],Advertising_final_team_status=ad['status'],whole_game_complete=False,physical_console_verified=False,native_Chat_verified=False,ongoing_finite_workers=[])
    save(pub/'protocol.json',state);save(V/'native-Deck-composition-delivery-current.json',state)
    gpath=V/'goal-continuation-current.json';goal=read(gpath);goal.update(status='active_native_Deck_composition_and_ordinary_wait_reviewed',recorded_at=state['recorded_at'],directory=str(pub),review=str(review),full_objective_complete=False,blocked=False,previous_goal_turn_classification='progress: installed native Deck image and component/boot/heap proof',current_turn_classification='progress',current_turn_predictions=state['actual_predictions'],new_training=False,ongoing_finite_workers=[],saved_prompt_or_transcript_records=records['current-model-work-index-v4-current.json']['saved_prompt_or_transcript_records'],limits='Controlled native Deck/GPU composition verified. Ordinary input stalls before coordinate entry; unmatched original route cannot attribute cause. Full-game source rebuild/physical, helper IRQ/reentrancy, native Chat UI, wider Advertising reliability and current migration remain incomplete.',native_Deck_composition_delivery=state)
    goal['remaining_requirements']=audit
    goal['next_actions']=['Isolate ordinary Deck resource-transfer wait with matched loader/CD-device evidence. Native finalprogress1D159C < target1E8000; original fullroute did not reachmatchinginput.','Retain17nestednativecoordinate/GPUcalls/46checkpoint proof; qualifyactualhelper-suspension/reentrancy/IRQ andremainingDeck/source/assets.','Use frozen accepted/rejected local transcripts for proof-mapped training/evals; no newweights thisturn. ContinuegeneralAdvertisingquality and nativeChatUI acceptance.','Package latest frontend/source/test files separately from retained passed portable package; verify actual other/futurehardware.']
    save(gpath,goal);save(pub/'goal-state-final.json',goal)
    integrity={str(p.relative_to(pub)):sha(p)for p in pub.rglob('*')if p.is_file()};save(pub/'integrity.json',dict(files=integrity,count=len(integrity)))
    print(state['status'],state['actual_predictions'],'predictions',len(paths),'raw/source files bound',flush=True)

if __name__=='__main__':main()
