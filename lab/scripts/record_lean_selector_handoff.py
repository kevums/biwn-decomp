"""Preserve full objective and actual terminal handles after the lean-selector work."""
import json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';p=v/'goal-continuation-current.json';d=read(p);now=datetime.now(timezone.utc)
    out=v/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);shutil.copy2(p,out/p.name)
    configurations=[('geometry-C-processors-route-active.json',55729,17084),('native-geometry-select-lean-candidate-current.json',19136,17382),('native-geometry-select-lean-control-current.json',12186,17382)]
    live=[];terminal=[]
    for name,session,size in configurations:
        q=v/name;job=read(q);entry=dict(status=job['status'],exec_session=session,tested_resident_bytes=size,protocol=str(Path(job['directory'])/'protocol.json'),terminal=job['status'].startswith('terminal_'))
        for key in ['pid','child_pid']:
            if job.get(key):
                text=subprocess.run(['ps','-p',str(job[key]),'-o','pid=,command='],capture_output=True,text=True,timeout=5).stdout.strip()
                entry[key]=job[key];entry[key+'_live']=bool(text);entry[key+'_observed_command']=text
        if entry['terminal']:
            assert not entry.get('child_pid_live',False)
            for key in ['frames','PCM_equal','returned_outdoors','live_monitor_pass']: 
                if key in job:entry[key]=job[key]
            terminal.append(entry)
        else:live.append(entry)
    preview=[]
    for pid in [233,235]:
        text=subprocess.run(['ps','-p',str(pid),'-o','pid=,command='],capture_output=True,text=True,timeout=5).stdout.strip()
        if text:preview.append(dict(pid=pid,observed_command=text))
    d.update(status='active_lean_selector_native_calls_and_local_workflow_verified_preceding_C_routes_complete',recorded_at=now.isoformat(),
      previous_turn_classification='progress:324byte native selector, tagged-pointer fixture expansion, corrected live monitor and13success calls; preceding cache C route reviewed; status/prompt artifacts retained.',
      this_turn_classification='progress:298byte typed lean selector passed1280+512component/final-address and96startup;64byte stack and16.01percent lower component-cycle sum across identical1792development fixtures;two24978frame native routes with13success calls each pass live checks, media/state disagreement retained. Boundary C route finished and reviewed all24978frames/8fields/79929600PCMbytes, zero reported fallback/errors. Generic current MCP/Reader and saved-prompt index installed/tested; latest175word local answer16.82seconds. No new game Author or weight training.',
      prior_state_archive=str(out/p.name),goal_complete=False,finite_jobs=live,
      interactive_preview=dict(observed_live_processes=preview,unchanged=True),
      latest_native_selection_component=str(v/'native-geometry-select-lean-current.json'),
      latest_native_selection_component_review=str(v/'native-geometry-select-lean-reviewed-current.json'),
      latest_native_selection_disc=str(v/'native-geometry-select-lean-disc-build-current.json'),
      latest_native_selection_live_review=str(v/'native-geometry-select-lean-live-reviewed-current.json'),
      latest_boundary_C_route_review=str(v/'geometry-C-processors-reviewed-current.json'),
      latest_current_status_delivery=str(v/'current-biwn-status-v4-delivery-current.json'),
      latest_terminal_status_smoke=str(v/'current-biwn-status-terminal-jobs-current.json'),
      latest_model_work_index=str(v/'current-model-work-index-v4-current.json'),
      latest_human_result=str(ROOT/'BIWN Latest Work.txt'),
      local_model_work_this_turn=dict(Reader_SDK_runs=3,Reader_prediction_rounds=6,Editor_SDK_calls=1,new_game_Author_predictions=0,new_training=False,native_Chat_verified=False,details='v7 raw status omitted explicit failure-path coverage and was unqualified. v8 first158words16.11sec; terminal-jobs followup175words16.82sec, both retain critical scope. Standalone v5Editor159words15.20sec from retained v7 draft, not a fresh main-menu fallback. Same27Bbase32K/oneworker; no weight or default preview changes.'),
      next_actions=[
        'No finite test job from this handoff remains live. Both16872cache and17084boundary C-processor comparisons are terminal/reviewed equal at24978frames, eight fields and79929600PCMbytes, with zero reported Original/Rejected/errors. Do not restart old handles. They do not verify the latest17382selector disc.',
        'Continue complete readable/native game reconstruction. Next adjacent original102C4 scanning selector remains a host-recovered routine without a native C port; use existing typed geometry layouts/1039C update semantics, original CPU and ordered-memory checks, preserving all signed word/partial-register/flag behavior. New logical-function count must not increase merely for native adaptation.',
        'Extend the checked fixed C instruction provider from17084boundary to17382typed selector: new linked298bytes, eight-byte1039Credirect and revised startup catalogue; retain bank-coherent wrapper. Inspect MOVEM masks/typed access instructions, verify primitive fullCPU/RAM/cost plus complete1280+512function coupling before launching a fresh exact-disc C comparison. No transfer of preceding-disc results.',
        'Selector live function contract passes13success calls each on two24978native routes; failure paths remain component-only. Candidate/control still differ in22612CPU frames,12250video frames and fullPCM. First GPU divergence coincides with first selector call frame380; success fixture1104cycles versus original628. Component cost reduction does not resolve route timing. Do not claim cycle/whole-state/physical equivalence or promote default preview.',
        'Start Local AI -> S uses genericv8Reader/v5Editor and currentMCPv4 with166bound proof files, two preceding disc identities/applicability flags. Actual current reply175words16.82sec/oneMCPcall. Literal tool-field name/soft verbosity limits remain. Source review of future generated answers is still needed; no general reliability or training gain.',
        'Start Local AI -> I uses versioned v4source-list collector; latest index34saved prompt/transcript records, not34new predictions. It includes current status plus Author/Reviewer/repair and Advertising history. Exact model identities are per saved request; no streaming in native LM Studio Chat is claimed. Native Chat display for current workflows remains unverified; continue headlessly if locked, never ask another unlock.',
        'Advertising optional trained Reviewer/v5team remain installed with known citation-support failure. Seek genuinely frozen new semantic training/evaluation evidence; current four papers may already appear in training/test files. DEV is not currently mounted, but internal corpus remains available. Do not relabel seen-paper development tasks as independent out-of-source evaluation.',
        'Finish portable lab/corpus/models/MCP migration and future256GBprofile validation. Current-only installer and versionedBootstrap checked; complete runtime reinstall/future hardware remain unverified. Reconcile historical latest_*config annotations during deployment audit without altering bound historical sources.'
      ])
    existing=d.get('terminal_jobs',[]);known={x.get('protocol',x.get('proof'))for x in existing};d['terminal_jobs']=existing+[x for x in terminal if x['protocol']not in known]
    p.write_text(json.dumps(d,indent=2)+'\n');(out/'handoff.json').write_text(json.dumps(d,indent=2)+'\n')
    event=dict(recorded_at=now.isoformat(),classification='progress',action='lean_native_selector_generic_local_status_and_both_preceding_C_routes_reviewed',handoff=str(out/'handoff.json'),Reader_SDK_runs=3,Reader_prediction_rounds=6,Editor_SDK_calls=1,new_game_Author_predictions=0,new_training=False,whole_goal_complete=False,live_jobs=live)
    with(ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(event)+'\n')
    print(json.dumps(dict(handoff=str(out/'handoff.json'),live_finite_jobs=len(live),full_goal_requirements=len(d['full_goal_requirements']))))
if __name__=='__main__':main()
