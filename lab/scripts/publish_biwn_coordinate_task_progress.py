"""Publish checked readable task/cleanup progress and accurate local inference."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path.home()/'.lmstudio/local-ai-lab'
def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()
def save(path,value):Path(path).write_text(json.dumps(value,indent=2)+'\n')

def main():
    now=datetime.now(timezone.utc).isoformat()
    out=ROOT/'verification/coordinate-task-progress-evidence'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    paths={name:ROOT/'verification'/name for name in ['natural-coordinate-gameplay-current.json','natural-coordinate-coverage-current.json',
        'task-gates-current.json','coordinate-task-controls-current.json','coordinate-task-controls-installed-MCP-current.json',
        'coordinate-task-controls-menu-current.json','local-task-gates-author-current.json','local-task-gates-repair-current.json']}
    proofs={name:json.loads(path.read_text()) for name,path in paths.items()}
    task=proofs['coordinate-task-controls-current.json']; gate=proofs['task-gates-current.json']; menu=proofs['coordinate-task-controls-menu-current.json']
    assert task['cases']==2086 and task['native_cases']==18 and task['coordinate_remaining_fixture_helpers']==['0xdf60','0x20f78']
    assert sha(task['library'])==task['library_sha256'] and sha(gate['source'])==gate['source_sha256']
    for path,digest in task['sources_sha256'].items():assert sha(path)==digest,path
    assert sha(ROOT/'projects/black-ice-white-noise/restoration/biwn_task_gates.c')==gate['source_sha256']
    turn=menu['turn'];answer=turn['answer']
    assert menu['exit_code']==0 and not turn['quality_flags'] and turn['rounds']==2
    assert all(word in answer for word in ['2,086','2,147','3,400','18 repair bytes','0xdf60','0x20f78','not installed'])
    assert len(answer.split())<140 and 'Local 27B' in answer and 'coordinator' in answer
    # Source review: frame1 is relative to the restored continuation, not the
    # earlier cold-start patch frame23539. The natural proof retains that origin.
    menu.update(status='terminal_actual_menu1_source_review_pass_after_same_model_revision',
        source_review_actor='Codex coordinator',source_review={
            'counts_and_two_service_addresses_match':True,'local_guided_authorship_and_coordinator_role_match':True,
            'inherited18_repair_bytes_disclosed':True,'before_frame1_refers_to_restored_continuation':True,
            'supplied_component_fixtures_distinguished_from_live_runtime':True,'separate_branches_disclosed':True,
            'readable_API_not_in_live_frames_disclosed':True,'initial_answer_accepted':False,
            'initial_omissions':['inherited18byte repair','initial0xf78alias was erroneous; final0x20f78correct'],
            'same_model_revision_not_independent_review':True},word_count=len(answer.split()))
    save(paths['coordinate-task-controls-menu-current.json'],menu)
    save(Path(menu['directory'])/'source-review.json',menu['source_review'])
    # Fresh native helper lookup, without generating or fabricating a Chat.
    helper=subprocess.run([sys.executable,str(ROOT/'scripts/native_chat_team_context.py')],
        input=json.dumps(dict(domain='game',query=menu['question']))+'\n',capture_output=True,text=True)
    assert helper.returncode==0,helper.stderr
    ready=json.loads(helper.stdout); assert ready['status']=='ready' and len(ready['roles'])==3
    assert ready['evidence']['coordinate_task_controls_linkage']['cases']==2086
    assert ready['evidence']['natural_coordinate_gameplay']['inherited_repair_bytes']==18
    save(out/'native-helper-ready.json',ready)
    pins={}
    for name in ['interactive-preview-recipe.json','outdoor-restoration-preview-recipe.json']:
        recipe=json.loads((ROOT/'verification'/name).read_text())
        for path,digest in recipe['hashes'].items():assert sha(path)==digest,path
        pins[name]=dict(files=len(recipe['hashes']),all_hashes_match=True,recipe_sha256=sha(ROOT/'verification'/name))
    models=json.loads(subprocess.check_output([str(Path.home()/'.lmstudio/bin/lms'),'ps','--json'],text=True))
    assert len(models)==1 and models[0]['identifier']=='advertising-scholar' and models[0]['status']=='idle' and models[0]['queued']==0
    restore=ROOT/'projects/black-ice-white-noise/restoration'
    decomp=f'''BLACK ICE WHITE NOISE — PARTIAL RECONSTRUCTION
Updated {now}

READABLE COORDINATE CONTROLS: THREE SUPPLIED SERVICES REMOVED
The new separate coordinate/task-controls variant computes peer task pause/resume counters and the25-room texture/object/actor/allocator cleanup. All2,082prior controls inputs were rechecked with a captured18-task topology and supplied room records; four additional mixed-counter/nonempty-room inputs bring the total to2,086. All match original D0, ordered logical bus effects, public RAM and MMIO. Eighteen selected native M68000/blitter cases match, emitting2,147actual blitter commands; seven nested error checks pass. One artificial changing-inventory-read case remains native-excluded but passes original/C logical comparison.
Task pause/resume was generated by the local27B model in a guided repair, accepted byte-for-byte after69original-instruction/65native cases and32host guards. The first raw draft was rejected for formatting/compilation/ABI mistakes; the coordinator had omitted the included bus type definition from that first prompt, then supplied the actual type and corrections. No coordinator edits to the accepted repair. Coordinator wrote the header, adapter and checks; existing readable cleanup was reused.
The coordinate variant now has two supplied service bodies: DF60 context switching and20F78 scene setup/streaming. Clock/raw controller rows, task topology and coherent room/heap/font/panel data are supplied inputs. This does not mean only two tasks remain before the whole game is complete. The high-level coordinate API is still separate from the live instruction-compatible CPU frame runtime. Scheduling, private CPU stack/CCR/caller-saved registers and physical timing are excluded from this component API.
Source: {restore/'biwn_game_controls_coordinate_tasks.c'}
Generated task routines: {restore/'biwn_task_gates.c'}
Proof: {paths['coordinate-task-controls-current.json']}
Original2082-case coordinate variant and all prior previews remain separate and intact.

NATURAL COORDINATE GAMEPLAY
Three ordinary-control source-runtime continuations from the verified outdoor checkpoint pass full original/source CPU/cycle/frame/PCM/final-machine comparisons:400cancel,1500confirm,1500edit frames. Total3,400frames across independent branches, not one continuous run;53,604,583source CPU instructions. They select the existing item46 at inventory position4, activate with B+C, then use keypad/A/B/C. No item grant, player/scene transplant or new patch. They inherit18repair bytes from the earlier source outdoor checkpoint. DSP is inactive in these continuations and explicitly qualified, not newly exercised here.
Cancel retains X12992/Z42408. Typing/editing203662 and accepting computes X13024/Z42400. All166coordinate instruction locations are naturally reached, including both backspace paths. These frames execute instruction-compatible C, not the separate readable high-level API above. The routes add246addresses/four entries to the main-stage test inventory:6,825/18,306instruction locations and145/206function entries. This is reachability, not readable decompilation percentage, full branch coverage or all-disc coverage.
Proof: {paths['natural-coordinate-gameplay-current.json']}
Real source image: {ROOT/'verified-previews/natural-coordinate-edited.png'}

STARTUP / EXISTING PREVIEWS
Fresh source execution reaches the unmodified merchant after23,538frames and395,449,715CPU instructions, with no original warmup/checkpoint and zero game-byte repairs. The earlier continuous merchant/elevator/outdoor chain reaches24,738frames/416,052,785CPU instructions, applying18bytes after merchant. CPU/cycle/frame/PCM/final-machine comparison matches the same-core reference. Source CPU/GPU/DSP/IRQ-selection/entry counters have no original/rejected execution fallback on that startup route; every GPU/DSP internal instruction state is not compared.
P restores the source-produced zero-repair merchant, then applies56declared repair bytes in three patches. Same-profile Deck/mail200, unarmed120, Beretta300 and elevator/outdoor1200frame branches pass. O retains the18byte outdoor profile and4,600frame building570entry/exit test; a separate6,000frame route reaches building532. New task/cleanup code is not promoted into P/O. All112P and84O pinned files still match.

PERFORMANCE / REMAINING WORK
The600frame headless primary replay matched in14.807seconds source wall time (~40.52frames/total wall second), versus2.301seconds reference. This includes load/check/capture/cleanup; it is not native-window FPS. Profiling points to GPU OP/IRQ/register-transfer costs; LTO supplied no dependable speedup and was not promoted.
Remaining work includes readable live integration and explicit continuations, broader game/branch coverage, remaining engine/services, full uninterrupted current combined profile, performance, sustained keyboard/audio and a standalone build. Original IRQ queue/device line/ACK, host commit/prefetch/cycle charging, firmware HLE/CD bootstrap, Object Processor and hardware remain providers. Future256GBhardware is unbenchmarked. The whole-game goal remains incomplete.
Exact prompts/actions: {ROOT/'runs/agent-work-audit.jsonl'}
'''
    local=f'''LOCAL AI — DAILY WORKFLOW
Updated {now}

Open Start Local AI.command. Menu1 Game Assistant,2 Advertising Assistant;3/4use three sequential roles on the same local weights. They are not independent reviewers. Exact prompts, outputs, evidence and timing are saved. Preferred model remains the tested27B/6bit base with source retrieval,32Kcontext/one worker, loaded as advertising-scholar. No new weights in this continuation.

LATEST REAL INSTALLED MENU1 TEST
Question: {menu['question']}
Final answer: {answer}
This took18.34seconds across two generations with one same-model scope revision; it is not an unassisted first-answer success. Initial answer omitted inherited18bytes and had a wrong0xf78alias; final source review accepts the corrected counts,0x20f78address, guided authorship and fixture/live distinction. Beforeframe1 refers to the restored continuation. A disclosure guard was corrected to distinguish18native cases from18repair bytes. Final response has{len(answer.split())}words and no mechanical flags; coordinator source review is separately recorded.
Proof: {paths['coordinate-task-controls-menu-current.json']}

LOCAL CODE WRITING
First Author attempt30.93seconds: raw fenced output failed compilation, omitted a NULL header and passed bus instead of bus->context. The initial prompt lacked the included typed bus definition. Guided Remediator33.31seconds: accepted C unchanged after69original/65native/32host checks, then integrated into2,086controls cases/18native comparisons by coordinator adapter. This is a guided code-generation success for two small task-list functions, not autonomous porting capability or a general model ranking. Both exact prompts/responses remain saved.
Author: {Path(proofs['local-task-gates-author-current.json']['directory'])/'prompts-and-responses.txt'}
Repair: {Path(proofs['local-task-gates-repair-current.json']['directory'])/'prompts-and-responses.txt'}

NATIVE LM STUDIO CHAT
Existing genuine saved native gameChat verifies three roles and visible prompts/responses. The updated helper freshly returns current task/cleanup and natural gameplay scope for all three roles. This turn's code requests and menu1 test ran headlessly; they were not rendered in native Chat. Revision2 native token/speed/title/cancellation behavior and Advertising UI rendering remain unverified after the earlier CUA timeout. Continue without unlock requests; no conversation files fabricated.

ADVERTISING
Base+retrieval remains the preferred daily model, now idle. V6/V7 training experiments remain quality-rejected and unpromoted. Prior native backend role lookup and shared causal/rubric/timing guidance are fixed; three local backend outputs and the coordinator-qualified teaching copy are preserved, with native Advertising rendering still pending. See CURRENT ADVERTISING.txt. No new advertising quality/training claim this turn.
'''
    for name,content in [('CURRENT DECOMPILATION.txt',decomp),('CURRENT LOCAL INFERENCE.txt',local)]:
        (ROOT/name).write_text(content);shutil.copy2(ROOT/name,RUNTIME/name)
    for name,path in paths.items():
        shutil.copy2(path,out/name);shutil.copy2(path,RUNTIME/'verification'/name)
    audit=dict(recorded_at=now,actor='Codex coordinator',local_roles=['Restorer Author','Restorer Remediator'],
        action='Accepted guided local task pause/resume C unchanged and linked task gates plus existing full-room cleanup into readable coordinate controls',
        author_seconds=30.93,repair_seconds=33.31,raw_first_source_accepted=False,coordinator_guided_ABI=True,
        original_native_and_guard_cases=[69,65,32],linked_cases=2086,native_cases=18,native_blitter_commands=2147,
        remaining_coordinate_service_targets=['0xdf60','0x20f78'],high_level_API_live=False,natural_gameplay_proof=str(paths['natural-coordinate-gameplay-current.json']),
        native_Chat_this_turn=False,weight_training=False,proof=str(paths['coordinate-task-controls-current.json']),
        prompts=[str(Path(proofs[name]['directory'])/'prompts-and-responses.txt')for name in ['local-task-gates-author-current.json','local-task-gates-repair-current.json']],
        same_model_menu_revision=True,menu_reviewed=True,preview_pins=pins)
    with (ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:stream.write(json.dumps(audit)+'\n')
    ledger_path=ROOT/'verification/goal-continuation-current.json';ledger=json.loads(ledger_path.read_text());shutil.copy2(ledger_path,out/'previous-goal-continuation.json')
    ledger.update(status='concrete_progress_goal_incomplete',recorded_at=now,
        previous_turn_classification='no progress: read-only response to the user overall status question; revalidated latest natural proof, no blocker remained',
        this_turn_classification='progress: guided local task-gate repair accepted unchanged69original/65native/32guards, linked real pause/resume and existing25-room cleanup;2086original/C,18native/2147blittercommands/7nestedguards pass; two coordinate supplied helper bodies remain. Installed freshMCP/native-helper evidence and18.34second two-generation menu answer source-reviewed with inherited18byte disclosure; prior natural3400frame proof now exposed and all P/O pins intact.',
        latest_coordinate_task_controls=str(paths['coordinate-task-controls-current.json']),latest_task_gates=str(paths['task-gates-current.json']),
        latest_natural_coordinate_gameplay=str(paths['natural-coordinate-gameplay-current.json']),latest_added_static_coverage=str(paths['natural-coordinate-coverage-current.json']),
        latest_coordinate_local_inference=str(paths['coordinate-task-controls-menu-current.json']),latest_coordinate_MCP=str(paths['coordinate-task-controls-installed-MCP-current.json']),
        latest_evidence_snapshot=str(out),live_processes=[],goal_complete=False,preview_pin_checks=pins,
        live_process_observation=dict(observed_at=now,finite_compute_jobs_running=False,model=models),
        native_UI_observation='No new UI call this continuation. Latest earlier CUA timeout leaves lock state unknown. Genuine earlier native gameChat remains verified; new code/menu checks are headless.',
        next_actions=[
            'All local Author/Remediator, task-gate/component comparisons and menu/MCP checks are terminal. No active finite compute job; daily27Bmodel idle. Do not poll/restart closed sessions54290/51922/89028/89418/12214/14182/27896/2717.',
            'Continue readable coordinate live integration with explicit resumable input/clock/scheduler continuations. Blocking logical API cannot replace a frame-runtime routine without preserving task switching and timing. Task pause/resume and25-room cleanup are now computed; DF60context switching and20F78scene streaming remain supplied in this variant, while previously readable scheduler/scene APIs exist separately.',
            'Extend linked coordinate controls toward actual scene stream and scheduler services using real captured game data and explicit continuations, retaining original bus/CPU/frame behavior and existing preview capability. Component task/room fixtures are not a live installation.',
            'Continue broader game/branch coverage, remaining maintainable game systems, runtime-provider removal, uninterrupted combined-profile route, performance and standalone build. Address reachability is not a readable-source completion percentage.',
            'Keep Advertising base+retrieval; broaden source-grounded research/education tasks and review before another training objective. V6/V7 remain rejected; do not repeat unchanged smallSFT.',
            'When native UI is available verify Advertising rendering and pluginrevision2stats/title/cancel without unlock requests. New code prompts/responses are genuine headless requests, not fabricated native Chat.'
        ])
    save(ledger_path,ledger);shutil.copy2(ledger_path,RUNTIME/'verification'/ledger_path.name)
    report=dict(status='coordinate_task_cleanup_progress_published',recorded_at=now,directory=str(out),
        menu_word_count=len(answer.split()),menu_seconds=18.34,menu_generations=2,preview_pins=pins,
        source_generated_repair_accepted_unchanged=True,high_level_coordinate_API_live=False,new_training=False,whole_goal_complete=False,
        files_sha256={str(path):sha(path)for path in paths.values()})
    save(out/'report.json',report);save(ROOT/'verification/coordinate-task-progress-publication-current.json',report)
    print(json.dumps(dict(status=report['status'],directory=str(out),menu_words=report['menu_word_count'],preview_pins=pins)),flush=True)

if __name__=='__main__':main()
