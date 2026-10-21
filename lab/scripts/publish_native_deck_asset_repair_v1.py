"""Publish the native ordinary-Deck milestone; leave the full goal active."""
from datetime import datetime,timezone
from pathlib import Path
import json,subprocess
import check_native_deck_fresh_restore_v1 as common
ROOT=common.ROOT;V=ROOT/'verification';read=common.read;save=common.save;sha=common.sha
def main():
    pub=V/'native-Deck-asset-repair-delivery'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ');pub.mkdir(parents=True);print(pub,flush=True)
    names=['native-Deck-transfer-probe-current.json','native-Deck-asset-repair-build-current.json','frame-acquire-selector13-qualified-current.json','native-Deck-selector13-source-current.json','native-Deck-asset-repair-reviewed-current.json','Deck-asset-layout-local-reviewed-current.json','Deck-asset-layout-repair-reviewed-current.json','deck-asset-layout-training-prepared-current.json','Deck-status-live-v11-reviewed-current.json','native-Deck-context-v4-current.json','current-model-work-index-v4-current.json']
    records={n:read(V/n)for n in names};reviewed=records['native-Deck-asset-repair-reviewed-current.json'];reader=records['Deck-status-live-v11-reviewed-current.json'];build=records['native-Deck-asset-repair-build-current.json']
    assert reviewed['ordinary_native_coordinate_entries']==reviewed['ordinary_native_coordinate_returns']==140 and reviewed['native_GPU_roots_reached']==8
    assert reader['status']=='terminal_current_repaired_native_Deck_local_Reader_review_pass'
    paths=set(V/n for n in names)
    for name,r in records.items():
        save(pub/name,r)
        for p,digest in r.get('source_sha256',{}).items():assert sha(p)==digest,p;paths.add(Path(p))
    catalog=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True));assert len(catalog)==1 and catalog[0]['identifier']=='advertising-scholar'and catalog[0]['status']=='idle'and catalog[0]['queued']==0
    save(pub/'model-catalog.json',catalog)
    scripts=['probe_native_deck_transfer_v1.py','build_native_deck_asset_repair_v1.py','run_native_deck_asset_repair_v1.py','check_frame_acquire_selector13_disc_v1.py','check_native_deck_selector_source_v1.py','review_native_deck_asset_repair_v1.py','run_local_deck_asset_analysis_v1.py','run_local_deck_asset_analysis_repair_v1.py','run_deck_status_live_v11.py','check_native_deck_context_v4.py','native_chat_team_context.py','publish_native_deck_asset_repair_v1.py']
    paths.update(ROOT/'scripts'/p for p in scripts);paths.update(ROOT/p for p in ['native_deck_source_context_v4.py','Live Local BIWN Briefing.command','config/current-model-work-sources.json'])
    matrix=records['frame-acquire-selector13-qualified-current.json'];paths.add(Path(matrix['reviewed_report']))
    text=f'''BIWN NATIVE DECK — FRESH ORDINARY INPUT NOW REACHES RECOVERED CODE

Full goal remains active. This is an experimental restoration milestone, not a whole-game decompilation or physical-console claim.

RESULT
The separate repaired native CDI freshly boots under the retained HLE/emulator profile, follows the existing outdoor route, accepts keypad1/B+C, enters and renders Deck, accepts0, exits and returns to normal outdoor play. The25024frame run contains140native coordinate entries and140native returns, with zero original coordinate-body instructions and no invalid native task identities. All eight native GPU wrapper roots execute; GPU4720 returns974times. All reported observer error, pending-call and task-stack-outside fields are zero. Resource acquisitions all return. The101Deck-arena guards pass; only task slot6uses its private Deck arena. Immutable native code is unchanged. No snapshot restore or supplied CPU/task/RAM/GPU state is used in this fresh run.

The first24624frames before the new input phase match the unrepaired candidate in every recorded field except fullRAM and stage hashes, which include the static repair bytes. CPU/GPU/DSP PCs, fullCPU registers/banks/SR, navigation, positions and video hashes all match. This does not claim wholeRAM/timing/physical equivalence after a behavior-changing repair.

CAUSE AND REPAIR
The earlier final snapshot caught a transfer in flight, not a permanently stalled DMA. Exact restoration and120retained frames reveal four new read arms with identical request signatures: the loader repeatedly transfers, fails to find its marker and retries. The old mode3 group1marker lies8624bytes behind the requested normalized stream. Prior original/source real-disc evidence already recorded the same unresolved mode3 group.

Preserved marker offsets20719506,20826066 and20932626 differ by106560bytes, exactly64markerbytes plus13*8192framebytes. The original mode3 count table and constructor use16. This run applies the existing selector13 restoration repair to the current native image: table464A6 becomes13 and the36byte constructor window at10AC2 multiplies by13 while preserving public acquisition/return behavior. The two sites span38bytes;37actual CDI bytes differ. The separate experimental image preserves the previous image and original CDI. The retained native loader already contains the earlier word-scan repair.

Coordinator-written68000 assembly and linker placement rebuild the38bytes exactly and match the installed stage. An original pinned CPU versus accepted portable-source matrix now passes all9real-disc cold loads and9cache reuses with the repaired count; both formerly unresolved mode3 groups pass. Those component tests retain BIOS/disc-completion adapters and do not replace the separate fresh ordinary-input proof.

WHAT IS STILL PARTIAL
Only coordinate root11D1A of the six recovered Deck callers is native-installed; five remain hosted-only. The44,430byte native code footprint is unchanged, including the9,548byte coordinate module and98byte finalizer. This image changes original behavior and retains original code and HLE/emulator/device providers. Full readable game/same-console source rebuild, actual helper suspension/reentrancy/IRQ coverage, audio/audibility and physical-console validation remain unfinished. The default Python source-game preview is unchanged; this CDI is a separate experimental artifact.

LOCAL MODEL TEST AND TRAINING
Codex traced the machine state, applied the pre-existing restoration repair to the native image, wrote its source assembly, and ran/reviewed the compiler/emulator/disc checks. Local Restorer inferred13but proposed a shift by3, which multiplies by8, and violated the requested schema. Its sole repair returned12while proposing multiply13. Both actual outputs are rejected and preserved; no local source proposal was adopted. The accepted repair is coordinator-authored/source-assembled.

Two source-bound SFT examples from this exposed case family are prepared, with both failures and proof provenance. They are not held-out evaluation and no optimizer update or new weights were produced. A separate actual local Reader correctly reports140ordinary calls/returns,8GPUroots and the behavior-changing13-frame repair in{reader['stream']['seconds']}seconds; time to first fragment{reader['stream']['time_to_first_message_seconds']}seconds. Three local predictions occurred this continuation. This is a checked supplied-facts case, not general model reliability.

The one-click Live Local BIWN Briefing.command and main menu11now use this current result. Actual backend contexts for game/control/copyediting routes pass. Native Chat display remains unverified. Model Prompts and Responses.command indexes{records['current-model-work-index-v4-current.json']['saved_prompt_or_transcript_records']}saved prompt/transcript records; those records are not a prediction count.

Advertising remains on the daily27Bbase and optional previously trained Reviewer configuration. Its prior70word full-team chronology/causal improvement and remaining citation-granularity gap are retained; no new Advertising prediction or training this continuation. Current migration/future256GBhardware acceptance remains incomplete; prior passed portable package is retained.

NEXT
Extend the remaining five Deck callers to native source components and test real helper suspension/reentrancy/IRQ. Prepare a separately verified native keyboard-preview launcher and complete native Chat/current-package acceptance. Use disjoint held-out source families before evaluating any new training; never promote these two rejected source proposals.

Experimental CDI:{build['derived_disc']}
Reviewed gameplay:{reviewed['directory']}
Exact current prompt index:{records['current-model-work-index-v4-current.json']['report']}
Publication:{pub}
'''
    report=ROOT/'reports/Native Deck Ordinary Input Restoration Review.txt';report.write_text(text);(pub/'review.txt').write_text(text)
    readme=Path(build['directory'])/'READ ME - Native Deck Asset Repair.txt';readme.write_text('EXPERIMENTAL JAGUAR CD NATIVE DECK RESTORATION\n\nSeparate image; changes original mode3 asset groups16 to13. The original image and default Python preview are retained. Fresh emulator/HLE ordinary input verified140nativecoordinatecalls/returns and all8nativeGPUroots; fullgame rebuild/audio/physicalconsole remain unverified.\n\nFull review: '+str(report)+'\nSource repair assembly: '+str(ROOT/'projects/black-ice-white-noise/restoration/native-m68k/deck-selector13-restoration.S')+'\n')
    paths.update([report,readme,Path(build['derived_stage']),Path(build['derived_disc'])])
    save(pub/'source-and-raw-artifact-hashes.json',{str(p):sha(p)for p in sorted(paths)})
    audit=dict(full_objective_complete=False,game='Native coordinate ordinary input now verified on explicit repairedimage; fullgame source rebuild,other5Decknative,IRQ/reentrancy,audio/physical remain incomplete.',local_frontend='CurrentoneclickReader andbackendcontexts verified; nativeChatUI/newnativekeyboardfrontend remain unverified.',Advertising='Priorbounded70word improvement withcitationgap; broaderreliability/trainingacceptanceincomplete.',future_hardware='Currentnewfilesnotmigrated;actualfuturehardwareunverified.')
    save(pub/'requirement-audit.json',audit)
    state=dict(status='terminal_native_Deck_asset_repair_and_ordinary_input_delivered',recorded_at=datetime.now(timezone.utc).isoformat(),directory=str(pub),review=str(report),review_sha256=sha(report),disc=build['derived_disc'],disc_sha256=build['derived_disc_sha256'],ordinary_coordinate_calls=140,ordinary_coordinate_returns=140,native_GPU_roots_reached=8,all_observed_errors_and_pending_zero=True,source_assembled_repair_bytes=38,changed_CDI_bytes=37,restoration_changes_original_behavior=True,Reader_seconds=reader['stream']['seconds'],actual_predictions=3,new_training=False,prepared_training_examples=2,held_out_case_families=0,local_source_proposals_accepted=0,default_preview_promoted=False,whole_game_complete=False,physical_console_verified=False,native_Chat_verified=False,ongoing_finite_workers=[])
    save(pub/'protocol.json',state);save(V/'native-Deck-asset-repair-delivery-current.json',state)
    goalpath=V/'goal-continuation-current.json';goal=read(goalpath);goal.update(status='active_repaired_native_Deck_ordinary_input_reviewed',recorded_at=state['recorded_at'],directory=str(pub),review=str(report),full_objective_complete=False,blocked=False,previous_goal_turn_classification='progress: composednativeDeck/GPUtest andordinarytransferwaitidentified',current_turn_classification='progress',current_turn_predictions=3,new_training=False,ongoing_finite_workers=[],remaining_requirements=audit,native_Deck_asset_repair_delivery=state,saved_prompt_or_transcript_records=records['current-model-work-index-v4-current.json']['saved_prompt_or_transcript_records'],limits='Fresh repairednativeDeckordinaryinput140calls/returns andall8GPUroots pass. Explicitselector13restoration changesoriginalbehavior;fullgame/sourceconsole rebuild,remaining5nativeDeck,IRQ/reentrancy,audio/physical,nativeChatUI/currentmigration andwiderAdvertising reliability unfinished.')
    goal['next_actions']=['ExtendremainingfivehostedDeckcallerstonativeC/ABIwithrealstackandhelpercontinuationgates;retain140ordinarynativecallsproof.','Verifyactualhelper-suspension/reentrancy/IRQ andaudio/physicalconsole;fullgame source/assets remainincomplete.','Create/testseparatenativekeyboardpreviewlauncher;nativeChatUI remainsunverified.','Useproofmappedexposedcurriculumwithdisjointholdouts beforetraining/evaluation;bothactualnewlocalcodeproposalsrejected.','ContinueAdvertisingcitation/causal/Reviewerquality andpackagecurrentfilesseparatelyfromretainedpassedportablebaseline;futurehardwareunverified.']
    save(goalpath,goal);save(pub/'goal-state-final.json',goal)
    files={str(p.relative_to(pub)):sha(p)for p in pub.rglob('*')if p.is_file()};save(pub/'integrity.json',dict(files=files,count=len(files)))
    print(state['status'],len(paths),'raw/source files bound',flush=True)
if __name__=='__main__':main()
