"""Record actual live handles and scoped proofs without changing job state."""
import json,shutil,subprocess
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads(Path(p).read_text())
def main():
    v=ROOT/'verification';pointer=v/'goal-continuation-current.json';old=read(pointer);now=datetime.now(timezone.utc);out=v/'goal-continuation-handoffs'/now.strftime('%Y%m%dT%H%M%S.%fZ');out.mkdir(parents=True);shutil.copy2(pointer,out/pointer.name)
    jobs=[];terminal=[]
    configurations=[('cache-cluster-C-processors-route-active.json',73190,16872),('geometry-C-processors-route-active.json',55729,17084),('native-geometry-select-route-current.json',50307,17408),('native-geometry-select-layout-control-current.json',98022,17408),('native-geometry-select-diagnostic-candidate-current.json',48834,17408),('native-geometry-select-diagnostic-control-current.json',22482,17408),('native-geometry-select-bus-candidate-current.json',74372,17408),('native-geometry-select-bus-control-current.json',27318,17408),('local-native-geometry-select-author-current.json',77310,None),('local-native-geometry-select-repair-current.json',17389,None)]
    for name,session,resident in configurations:
        path=v/name
        if not path.exists():continue
        d=read(path);summary=dict(status=d['status'],protocol=str(Path(d['directory'])/'protocol.json'),driver_pid=d.get('pid'),exec_session=session,tested_resident_bytes=resident)
        if d['status'].startswith('terminal_'):
            summary.update(terminal=True)
            for key in ['frames','raw_kernel_gate_pass','raw_repair_gate_pass','gate_status','live_monitor_pass']: 
                if key in d:summary[key]=d[key]
            terminal.append(summary);continue
        for key in ['pid','child_pid']:
            if d.get(key):
                command=subprocess.run(['ps','-p',str(d[key]),'-o','pid=,command='],capture_output=True,text=True,timeout=5).stdout.strip()
                summary[key]=d[key];summary[key+'_live']=str(ROOT)in command or 'outputs/local-ai-lab/'in command
                summary[key+'_observed_command']=command
        folder=Path(d['directory']);status=folder/'C/status.json'
        if not status.exists():status=folder/'candidate/status.json'
        if status.exists():summary['latest_recorded_frame']=read(status).get('latest',{}).get('frame')
        summary['checkpoint_only_not_final_verdict']=True;jobs.append(summary)
    old.update(status='active_cache_C_route_passed_selector_live_calls_verified_timing_unresolved_boundary_C_running',recorded_at=now.isoformat(),
       previous_turn_classification='progress: latest boundary C provider passed45312atomic plus1632whole-routine cases; two-disc MCP/main-menu Reader+Editor tested. Controls answer did not alter goal scope.',
       this_turn_classification='progress: cache C route reviewed24978frames/PCM/observers; two-job frontend frozen. Coordinator324byte1039C native port after two rejected local drafts passed896+256component/final-address,96startup, then1280+512tagged fixtures. Isolated original monitor24bit-bus bug in two calls. Corrected candidate/control both24978frames returned outdoors,13success calls each passed all live checks; all frames unchanged by monitor fix. Video/audio/per-frame state divergence remains measured, no preview promotion.',
       prior_state_archive=str(out/pointer.name),goal_complete=False,finite_jobs=jobs,
       latest_C_runtime_review=str(v/'geometry-C-runtime-reviewed-current.json'),latest_cache_C_route_review=str(v/'cache-cluster-C-processors-reviewed-current.json'),
       latest_current_status_delivery=str(v/'current-biwn-status-v3-delivery-current.json'),
       latest_C_instruction_semantics=str(v/'geometry-CPU-instructions-current.json'),latest_C_runtime_build=str(v/'geometry-C-bank-build-current.json'),
       latest_native_selection_author=str(v/'local-native-geometry-select-author-current.json'),
       local_model_work_this_turn=dict(actual_predictions=4,local_Author_candidates_attempted=2,local_Author_candidates_passed=0,new_training=False,native_Chat_verified=False,scope='Exact Author/Reviewer and one repair/Reviewer responses retained. Accepted C/ABI and diagnosis/checks are coordinator work.'),
       next_actions=[
         'Corrected-bus candidate74372/control27318 are terminal and reviewed in native-geometry-select-live-reviewed-current.json. Both24978frames returned outdoors;13success calls each, zero selector/generic/stack errors. Original failed monitor receipts retained. Tagged header0x8015C684 -> physical0x15C684 cause is verified; same source/binary and all gameplay frames unchanged by monitor correction. No failure-path live call; component-only failure coverage.',
         'Poll SAME latest boundary C job: session55729 child23402 driver23384. Exact17084byte disc; no restart for observation timeout. Review all frames/PCM/zero fallback+errors and observer equality only after terminal.',
         'Continue1039C native selection from current component/build/live receipts. Both local drafts failed and both Reviewer responses unreliable/truncated. Coordinator324byte C/ABI passed896+256component/final-address and96startup, then expanded1280stable+512changing tagged object/header/record fixtures with unchanged source/binary. All46original instruction sites covered. No more local repairs; no training gain. Native port of already-recovered host function; new logical functions0.',
         'Selector candidate/control still differ in22613CPU frames,12250video frames and full PCM; full-RAM hashes differ24970frames. Live function contract now passes after monitor correction, but actual per-frame/timing differences remain. No preview or current-status promotion. Preserve both rejected and corrected receipts. Do not claim exact whole-state or physical-console equivalence.',
         'After selector live review, publish its17408byte scoped facts with a new versioned generic Reader prompt that can describe complete coordinator C (not the older one-line hybrid cleanup). The current main-menu publication deliberately remains the17084byte boundary result until that delivery is verified. Preserve bound historical source files. Both existing C jobs are preceding discs relative to the new selector.',
         'Start Local AI.command -> S is verified with actual configured MCP and bounded Reader/Editor. Cache C route now terminal, boundary C route separate. Native Chat-window generation remains unverified; continue headlessly if locked and never request another unlock.',
         'Continue complete readable game and same-console source reconstruction; no standalone full-game rebuild or physical console proof yet. Platform HLE/devices/IRQ line ACK/vector/clock/cost/blitter/object processor remain.',
         'Advertising optional trained Reviewer and team remain installed with known citation-support failure. Need genuinely frozen new semantic training/evaluation evidence; retrieval/arithmetic transport is not semantic reliability.',
         'Finish full lab/corpus/models/MCP migration preparation; future256GB hardware profile is planned and unbenchmarked. Full runtime reinstall and future machine remain unverified.'
       ])
    existing=old.get('terminal_jobs',[]);known={x.get('protocol',x.get('proof'))for x in existing}
    old['terminal_jobs']=existing+[x for x in terminal if x['protocol']not in known]
    for name,key in [('local-native-geometry-select-repair-current.json','latest_native_selection_repair'),('native-geometry-select-current.json','latest_native_selection_component'),('native-geometry-select-disc-build-current.json','latest_native_selection_disc'),('native-geometry-select-reviewed-current.json','latest_native_selection_component_review'),('native-geometry-select-live-reviewed-current.json','latest_native_selection_live_review'),('native-geometry-select-live-rejected-current.json','latest_native_selection_live_rejection'),('native-geometry-select-tagged-reviewed-current.json','latest_native_selection_tagged_review')]:
        if(v/name).exists():old[key]=str(v/name)
    old['latest_native_selection_prediction_index']=str(ROOT/'reports/native-geometry-select-prediction-index.json')
    pointer.write_text(json.dumps(old,indent=2)+'\n');(out/'handoff.json').write_text(json.dumps(old,indent=2)+'\n')
    event=dict(recorded_at=now.isoformat(),classification='progress',action='cache_C_full_route_and_native_geometry_selection_component_tagged_bus_and_live_call_verification',handoff=str(out/'handoff.json'),actual_local_predictions=4,raw_local_code_passed=0,raw_local_code_attempted=2,new_training=False,native_Chat_verified=False,goal_complete=False,live_finite_jobs=jobs)
    with (ROOT/'runs/agent-work-audit.jsonl').open('a')as f:f.write(json.dumps(event)+'\n')
    print(json.dumps(dict(handoff=str(out/'handoff.json'),live_jobs=len(jobs),new_terminal_records=len(terminal))))
if __name__=='__main__':main()
