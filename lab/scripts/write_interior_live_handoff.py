"""Record current goal scope and actual live handles after this validation turn."""
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
V=ROOT/'verification'


def read(p):return json.loads(Path(p).read_text())


def main():
    now=datetime.now(timezone.utc)
    out=V/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ')
    out.mkdir(parents=True)
    pointer=V/'goal-continuation-current.json'
    state=read(pointer)
    shutil.copy2(pointer,out/'previous-handoff.json')
    job=read(V/'interior-C-processors-route-active.json')
    checks=[]
    for key,expected in [('pid','run_biwn_interior_C_processors_route.py'),
                         ('child_pid',str(Path(job['directory'])/'probe.py'))]:
        proc=subprocess.run(['ps','-p',str(job[key]),'-o','pid=,etime=,%cpu=,command='],capture_output=True,text=True)
        live=proc.returncode==0 and expected in proc.stdout
        if key=='child_pid':live=live and '--CPU-mode C' in proc.stdout
        checks.append(dict(kind=key,pid=job[key],live_now=live,observed_command=proc.stdout.strip()))
    progress=read(Path(job['directory'])/'C/status.json')
    review=read(V/'native-interior-live-reviewed-current.json')
    frontend=read(V/'local-frontend-readiness-current.json')
    delivery=read(V/'current-interior-status-delivery-current.json')
    integrity=read(V/'interior-live-turn-integrity-current.json')
    preview=[]
    for pid in [233,235]:
        proc=subprocess.run(['ps','-p',str(pid),'-o','pid=,command='],capture_output=True,text=True)
        if proc.returncode==0:preview.append(dict(pid=pid,observed_command=proc.stdout.strip()))
    state.update(
        status='active_18888_native_gameplay_reviewed_exact_disc_C_route_running',recorded_at=now.isoformat(),
        prior_state_archive=str(out/'previous-handoff.json'),goal_complete=False,
        previous_turn_classification='Progress: inspected18888disc build/final-address1958+768checks/96startup, four terminal exact-disc C reviews, frontend/Advertising readiness and235file integrity evidence.',
        this_turn_classification=(
            'Progress: qualified the read-only10520/105DA oracle on1958original+1958compiled fixtures, two corruption negatives and RAM immutability. '
            'Fresh candidate/control each returned outdoors after24996frames with14actor successes and1sprite skipped failure, zero monitor errors; '
            'PCM matches but4video/5navigation and other state differences remain. New provider passed100224atomic cases at261static locations, '
            'four complete-function suites and bridge build. Fresh/live frontend v9 has26matching modules;18tools advertised and5actual calls pass. '
            'MCPv7 observes five separately identified jobs. Actual menu S/Reader v12 used2predictions/one tool call,157words in20.70seconds, '
            'core correct with coverage omissions. Native UI attempt remains unverified after stale controls despite unlocked console; historical '
            'Oct17native roles are separate. Actor group object measures5832bytes against1592spare.405bound files verified; no new weights or preview changes.'),
        latest_published_live_build_resident_bytes=18888,latest_built_disc_resident_bytes=18888,
        latest_native_interior_live_review=str(V/'native-interior-live-reviewed-current.json'),
        latest_interior_C_components=str(V/'interior-C-runtime-reviewed-current.json'),
        latest_frontend_readiness=str(V/'local-frontend-readiness-current.json'),
        latest_local_status_delivery=str(V/'current-interior-status-delivery-current.json'),
        latest_native_UI_attempt=str(V/'current-native-chat-interaction-current.json'),
        latest_actor_group_footprint=str(V/'native-actor-group-footprint-current.json'),
        latest_integrity=str(Path(integrity['directory'])/'protocol.json'),final_integrity_unique_files=405,
        finite_jobs=[dict(status=job['status'],exec_session=19237,terminal=job['status'].startswith('terminal_'),
                         tested_resident_bytes=18888,protocol=str(Path(job['directory'])/'protocol.json'),
                         reference=job['reference'],actual_process_checks=checks,
                         last_recorded_frame=progress.get('latest',{}).get('frame'))],
        finite_jobs_pending=int(any(row['live_now']for row in checks)),
        completed_current_turn_sessions=[62178,86872,35037,10107,4936,64699,96336],
        older_named_C_routes=dict(all_terminal_equal=True,resident_bytes=[16872,17084,17812,18270],apply_to18888_disc=False),
        local_model_work_this_continuation=dict(prediction_rounds=2,role='Current-status Reader through local LM Studio SDK and actual configured MCPv7',
                                               seconds=delivery['seconds'],Editor_used=False,new_code_Author_Reviewer_predictions=0,
                                               new_training=False,current_native_Chat_verified=False,
                                               core_claims_correct=True,coverage_omissions=delivery['omissions']),
        interactive_preview=dict(observed_processes=preview,operated_or_restarted=False,run_keys='Hold C+Up; P pauses/resumes.'),
        current_entrypoints=dict(Bootstrap='install_frontend_current_v9.py',MCP='chat_tools_current_v7.py;26module closure',
                                 status_S='ask_biwn_current_status_v12.py',prompts_I='48saved prompt/transcript records; not48predictions',
                                 Game_9_5='run_native_interior_select_model_trial.py; wrapper target check only, helpers actually executed previously',
                                 Advertising_D_V='Status v2/Reviewer loader v3; optional step8 remains loadable with no observed source-transfer gain'),
        next_actions=[
            'Poll exact18888C processor job exec19237 or actual35110/35120handles; do not restart for observation timeout. On terminal, independently verify frame identities/all8fields/fullPCM/backend counters/full observer equality against the exact18888native candidate. Use a new distinct interior-processor report path; preserve older reports.',
            'Plan whole-group native source ABI/layout before actor creation. Existing high-level actor service has5832text bytes and no unresolved symbols versus1592reserve bytes free. It remains a bus/status/work-budget relocatable object, without original native ABI or runtime proof. Inspect source snapshot/relocations; do not blindly enlarge heap or count old host algorithms as new recovery.',
            'Broaden actor failure and sprite successful/non-skipped search gameplay paths. Current15live calls cover14actor successes and1sprite skip only. Preserve current timing/video/navigation differences and inherited scanner media disagreements.',
            'S12brief status is qualified: component/startup counts, explicit per-kind component-only coverage and explicit inherited media details are omitted. Full MCP facts/report retain them; do not claim a complete semantic summary.',
            'Native UI returned stale/inconsistent AX/pixels, invalid IDs and elementHasNoFrame across a reset, with no current app-written generation. Console was unlocked. Do not ask another unlock or repeat identical UI actions. HistoricalOct17native3-role display exists with identical outputs; current streaming remains unverified. SDK/CLI works.',
            'Advertising optional step8/no observed source-transfer gain and39file/10shard transfer inventory remain unchanged. Continue full readable game/original-console reconstruction, training/source reliability and migration preparation; future-hardware performance remains unverified.'
        ],
        no_completion_claim=True,
        handoff_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    state['full_goal_requirements'][0]['evidence']=frontend['report']
    state['full_goal_requirements'][1]['evidence']=review['report']
    state['full_goal_requirements'][1]['remaining']='Full readable game/original-console reconstruction remains unfinished. Exact18888C route is pending; broader paths and current/inherited timing/state/media differences remain. New18888native gameplay is now checked for15calls under the declared limits.'
    text=json.dumps(state,indent=2)+'\n'
    (out/'protocol.json').write_text(text);pointer.write_text(text)
    audit=dict(recorded_at=now.isoformat(),event='interior_live_validation_and_local_frontend_progress',
               coordinator_work='Oracle/fixtures, native/C processor tests, publication/install/status validation and actor-group size measurement',
               new_local_prediction_rounds=2,new_code_Author_predictions=0,new_training=False,current_native_Chat_verified=False,
               game_report=review['report'],status_transcript=delivery['transcript'],bound_files_verified=405,
               finite_job=state['finite_jobs'][0],goal_complete=False)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as stream:stream.write(json.dumps(audit)+'\n')
    print(json.dumps(dict(status=state['status'],pending_job_frame=state['finite_jobs'][0]['last_recorded_frame'],
                          actual_live_handles=[(x['pid'],x['live_now'])for x in checks],goal_complete=False)))


if __name__=='__main__':main()
